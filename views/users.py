import os.path
import uuid
import flask_praetorian
from flask import request, current_app
from flask_restx import abort, Resource, Namespace
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from model import User, db, Role, Client
from schema import UserSchema, ClientSchema
from views.clients import getClientIDFromToken

api_user = Namespace("Users", "Users management")

""" 
Client endopoints 
"""


@api_user.route("/register")
class ClientListController(Resource):
    def post(self):
        try:
            guard = flask_praetorian.Praetorian()
            guard.init_app(current_app, User)
            userRequest = {
                "username": request.form.get("username"),
                "email": request.form.get("email"),
                "hashed_password": guard.hash_password(request.form.get("password"))
            }
            user = UserSchema().load(userRequest)
            db.session.add(user)
            role = Role.query.get_or_404(1)
            user.roles = []
            user.roles.append(role)

            clientRequest = {
                "cif": request.form.get("nif")
            }
            client = ClientSchema().load(clientRequest)
            client.user_id = user.id

            image = request.files['image']
            filename = str(uuid.uuid4().hex) + "_" + secure_filename(image.filename)
            folder = current_app.root_path + "/static/images/"
            image.save(folder + filename)
            client.cifImage = filename

            db.session.add(client)
            db.session.commit()
            return ClientSchema().dump(client), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.orig)
            return error, 500


@api_user.route("/update")
class ClientListController(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        try:
            clientID = getClientIDFromToken(request)
            client = Client.query.get_or_404(clientID)
            user = User.query.get_or_404(client.user_id)

            user.username = request.form.get("username")
            user.email = request.form.get("email")

            newImage = request.files['image']
            if newImage:
                folder = current_app.root_path + "/static/images/"
                if client.image != "default_user.jpg":
                    os.unlink(os.path.join(folder + client.image))
                filename = str(uuid.uuid4().hex) + "_" + secure_filename(newImage.filename)
                newImage.save(folder + filename)
                client.image = filename

            client.cif = request.form.get("nif")

            db.session.commit()
            return ClientSchema().dump(client), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.orig)
            return error, 500


""" 
Admin endopoints 
"""


@api_user.route("/<user_id>")
class UserController(Resource):
    @flask_praetorian.auth_required
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return UserSchema().dump(user)

    @flask_praetorian.roles_required("admin")
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return f"Deleted user {user_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, user_id):
        new_user = UserSchema().load(request.json)
        if str(new_user.id) != user_id:
            abort(400, "id mismatch")
        db.session.commit()
        return UserSchema().dump(new_user)


@api_user.route("/")
class UserListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return UserSchema(many=True).dump(User.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        user = UserSchema().load(request.json)
        db.session.add(user)
        db.session.commit()
        return UserSchema().dump(user), 201
