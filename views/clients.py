import os
import uuid
from functools import wraps
import flask_praetorian
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, inputs
from sqlalchemy import text
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import API_KEY
from model import Client, db, User, Bet, Role
from schema import ClientSchema, UserSchema

api_client = Namespace("Clients", "Clients management")

# SWAGGER POST FORM FIELDS
parserPOST = api_client.parser()
parserPOST.add_argument('Username', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('CIF', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('E-mail', type=inputs.email(), location='form', required=True, nullable=False)
parserPOST.add_argument('Password', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Image', type=FileStorage, location='files')

# SWAGGER PUT FORM FIELDS
parserPUT = api_client.parser()
parserPUT.add_argument('Username', type=str, location='form', nullable=False)
parserPUT.add_argument('CIF', type=str, location='form', nullable=False)
parserPUT.add_argument('E-mail', type=inputs.email(), location='form', nullable=False)
parserPUT.add_argument('Password', type=str, location='form', nullable=False)
parserPUT.add_argument('Cash', type=float, location='form', nullable=False)
parserPUT.add_argument('Image', type=FileStorage, location='files')


# custom decorator
def apiKey_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        apiKey = None
        if 'Authorization' in request.headers:
            apiKey = request.headers['Authorization']
        if not apiKey:
            return 'ApiKey is missing. You have to introduce it in Authorize section at the top of this page.', 401
        if apiKey != API_KEY:
            return 'Your ApiKey is wrong!', 401
        return f(*args, **kwargs)

    return decorated


def getClientIDFromToken(request):
    authHeader = request.headers.get('Authorization')
    token = authHeader.replace('Bearer ', '')
    guard = flask_praetorian.Praetorian()
    guard.init_app(current_app, User)
    user = guard.extract_jwt_token(token)
    result = Client.query.filter(Client.user_id == user['id'])
    clientID = result[0].id
    return clientID


# Client endopoints
@api_client.route("/claim", doc=False)
class ClientController(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        betID = int(request.json.get("idBet"))
        bet = Bet.query.get_or_404(betID)
        bet.claimed = True

        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        reward = float(request.json.get("reward"))
        client.cash = round(client.cash + reward, 2)

        db.session.commit()
        return jsonify({'new_cash': client.cash})


@api_client.route("/my_balance", doc=False)
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        return jsonify({'cash': client.cash, 'image': client.image})


@api_client.route("/profile", doc=False)
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        clientData = ClientSchema().dump(client)

        wonBets = Bet.query.filter(Bet.client_id == idClient, Bet.win.is_(True)).count()
        clientData['wonBets'] = wonBets

        statement = text("""
                        select 
                        (
                            select coalesce(sum(b.payment_amount), 0)
                            from bet b 
                            where b.client_id == :clientID and b.win == TRUE and b.claimed == TRUE 
                        )
                        -
                        (
                            select coalesce(sum(b.bet_amount), 0)
                            from bet b 
                            where b.client_id == :clientID
                        )
                    """)

        moneyEarned = db.session.execute(statement, {"clientID": idClient}).first()[0]
        moneyEarned = 0 if moneyEarned is None else round(moneyEarned, 2)
        clientData['moneyEarned'] = moneyEarned

        return clientData


# Admin endopoints
@api_client.route("/<int:client_id>")
class ClientController(Resource):
    @apiKey_required
    def get(self, client_id):
        """Shows a detailed client from given id."""
        client = Client.query.get_or_404(client_id)
        return ClientSchema().dump(client), 200

    @apiKey_required
    @api_client.doc(description='*Try it out* and introduce a client id you want to delete; then, hit *Execute* '
                                'button to delete the desired client from your database. In *Code* section you will '
                                'see the deleted client (*Response body*) and a code for a succeded or failed '
                                'operation.')
    def delete(self, client_id):
        """Deletes a client from given id."""
        client = Client.query.get_or_404(client_id)
        clientData = ClientSchema().dump(client)
        user = User.query.filter(User.id == client.user_id).first()
        db.session.delete(client)
        db.session.delete(user)
        db.session.commit()
        return clientData, 200

    @apiKey_required
    @api_client.expect(parserPUT, validate=True)
    @api_client.doc(description='*Try it out* and introduce the client data and client id you want to modify; then, '
                                'hit *Execute* button to apply your changes. In *Code* section you will see the '
                                'modified client (*Code*) and a code for a succeded or failed operation.')
    def put(self, client_id):
        """Updates a client with entry data and given id."""
        guard = flask_praetorian.Praetorian()
        guard.init_app(current_app, User)

        client = Client.query.get_or_404(client_id)
        user = User.query.filter(User.id == client.user_id).first()

        if request.form.get("Username"):
            user.username = request.form.get("Username")
        if request.form.get("E-mail"):
            user.email = request.form.get("E-mail")
        if request.form.get("Password"):
            user.hashed_password = guard.hash_password(request.form.get("Password"))
        if request.form.get("CIF"):
            client.cif = request.form.get("CIF")
        if request.form.get("Cash"):
            client.cash = request.form.get("Cash")
        if 'Image' in request.files:
            newImage = request.files['Image']
            folder = current_app.root_path + "/static/images/"
            if client.image != "default_user.jpg":
                os.unlink(os.path.join(folder + client.image))
            filename = str(uuid.uuid4().hex) + "_" + secure_filename(newImage.filename)
            newImage.save(folder + filename)
            client.image = filename

        db.session.commit()
        return ClientSchema().dump(client), 200


@api_client.route("/")
class ClientListController(Resource):
    @apiKey_required
    @api_client.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                                'clients stored in your database (*Response body*) and a code for a succeded or failed '
                                'operation.')
    def get(self):
        """Shows a detailed list of clients."""
        return ClientSchema(many=True).dump(Client.query.all()), 200

    @apiKey_required
    @api_client.expect(parserPOST, validate=True)
    @api_client.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                                'create a new client in your database. In *Code* section you will see your new client '
                                '(*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new client from entry data."""
        guard = flask_praetorian.Praetorian()
        guard.init_app(current_app, User)

        userRequest = {
            "username": request.form.get("Username"),
            "email": request.form.get("E-mail"),
            "hashed_password": guard.hash_password(request.form.get("Password"))
        }
        user = UserSchema().load(userRequest)
        db.session.add(user)
        role = Role.query.filter(Role.name == "client").first()
        user.roles.append(role)

        clientRequest = {
            "cif": request.form.get("CIF")
        }
        client = ClientSchema().load(clientRequest)
        db.session.add(client)
        client.user_id = user.id

        if 'Image' in request.files:
            image = request.files['Image']
            filename = str(uuid.uuid4().hex) + "_" + secure_filename(image.filename)
            folder = current_app.root_path + "/static/images/"
            image.save(folder + filename)
            client.image = filename

        db.session.commit()
        return ClientSchema().dump(client), 200
