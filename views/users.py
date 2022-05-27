import os.path
import uuid
import flask_praetorian
from flask import request, current_app
from flask_restx import Resource, Namespace, inputs
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from config import apiKey_required
from model import User, db, Role, Client
from schema import UserSchema, ClientSchema
from views.clients import getClientIDFromToken

api_user = Namespace("Users", "Users management")

# SWAGGER POST FORM FIELDS
parserPOST = api_user.parser()
parserPOST.add_argument('Username', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('E-mail', type=inputs.email(), location='form', required=True, nullable=False)
parserPOST.add_argument('Password', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Add Role', type=str, location='form', required=True, nullable=False,
                        choices=['admin', 'client'])

# SWAGGER PUT FORM FIELDS
parserPUT = api_user.parser()
parserPUT.add_argument('Username', type=str, location='form', nullable=False)
parserPUT.add_argument('E-mail', type=inputs.email(), location='form', nullable=False)
parserPUT.add_argument('Password', type=str, location='form', nullable=False)
parserPUT.add_argument('Add Role', type=str, location='form', nullable=False, choices=['admin', 'client'])
parserPUT.add_argument('Delete Role', type=str, location='form', nullable=False, choices=['admin', 'client'])


# Client endopoints
@api_user.route("/register", doc=False)
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


@api_user.route("/update", doc=False)
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
                if client.image != "default_user.jpg": os.unlink(os.path.join(folder + client.image))
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


# Admin endopoints
@api_user.route("/User/<Username>")
class UserController(Resource):
    @apiKey_required
    def get(self, Username):
        """Shows a detailed user from given Username."""
        user = User.query.filter(User.username == Username).first()
        return UserSchema().dump(user), 200

    @apiKey_required
    @api_user.doc(description='*Try it out* and introduce a user id you want to delete; then, hit *Execute* button to '
                              'delete the desired user from your database. In *Code* section you will see the '
                              'deleted user (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, Username):
        """Deletes an user from given Username."""
        user = User.query.filter(User.username == Username).first()
        db.session.delete(user)
        db.session.commit()
        return UserSchema().dump(user), 200


@api_user.route("/<User_id>")
class UserController(Resource):
    @apiKey_required
    @api_user.expect(parserPUT, validate=True)
    @api_user.doc(description='*Try it out* and introduce the user data and user id you want to modify; then, '
                              'hit *Execute* button to apply your changes. In *Code* section you will see the '
                              'modified user (*Code*) and a code for a succeded or failed operation.')
    def put(self, User_id):
        """Updates a user with entry data and given id."""
        guard = flask_praetorian.Praetorian()
        guard.init_app(current_app, User)

        user = User.query.get_or_404(User_id)

        if request.form.get("Username"): user.username = request.form.get("Username")
        if request.form.get("E-mail"): user.email = request.form.get("E-mail")
        if request.form.get("Password"): user.hashed_password = guard.hash_password(request.form.get("Password"))
        if request.form.get("Add Role"):
            role = Role.query.filter(Role.name == request.form.get("Add Role")).first()
            user.roles.append(role)
        if request.form.get("Delete Role"):
            role = Role.query.filter(Role.name == request.form.get("Delete Role")).first()
            if role in user.roles: user.roles.remove(role)

        db.session.commit()
        return UserSchema().dump(user), 200


@api_user.route("/")
class UserListController(Resource):
    @apiKey_required
    @api_user.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of users '
                              'stored in your database (*Response body*) and a code for a succeded or failed operation.')
    def get(self):
        """Shows a detailed list of users."""
        return UserSchema(many=True).dump(User.query.all()), 200

    @apiKey_required
    @api_user.expect(parserPOST, validate=True)
    @api_user.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                              'create a new user in your database. In *Code* section you will see your new user ('
                              '*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new user from entry data."""
        guard = flask_praetorian.Praetorian()
        guard.init_app(current_app, User)

        userRequest = {
            "username": request.form.get("Username"),
            "email": request.form.get("E-mail"),
            "hashed_password": guard.hash_password(request.form.get("Password"))
        }
        user = UserSchema().load(userRequest)
        db.session.add(user)
        role = Role.query.filter(Role.name == request.form.get("Add Role")).first()
        user.roles.append(role)

        db.session.commit()
        return UserSchema().dump(user), 200
