import flask_praetorian
from flask import request, jsonify, current_app
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text
from model import Client, db, User, Bets
from schema import ClientSchema

api_client = Namespace("Clients", "Clients management")


# Client endopoints
def getClientIDFromToken(request):
    authHeader = request.headers.get('Authorization')
    token = authHeader.replace('Bearer ', '')
    guard = flask_praetorian.Praetorian()
    guard.init_app(current_app, User)
    user = guard.extract_jwt_token(token)
    result = Client.query.filter(Client.user_id == user['id'])
    clientID = result[0].id
    return clientID


@api_client.route("/claim")
class ClientController(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        betID = int(request.json.get("idBet"))
        bet = Bets.query.get_or_404(betID)
        bet.claimed = True

        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        reward = float(request.json.get("reward"))
        client.cash = round(client.cash + reward, 2)

        db.session.commit()
        return jsonify({'new_cash': client.cash})


@api_client.route("/my_balance")
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        return jsonify({'cash': client.cash, 'image': client.image})


@api_client.route("/profile")
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        client = Client.query.get_or_404(idClient)
        clientData = ClientSchema().dump(client)

        wonBets = Bets.query.filter(Bets.client_id == idClient, Bets.win.is_(True)).count()
        clientData['wonBets'] = wonBets

        statement = text("""
                        select 
                        (
                            select coalesce(sum(b.payment_amount), 0)
                            from bets b 
                            where b.client_id == :clientID and b.win == TRUE and b.claimed == TRUE 
                        )
                        -
                        (
                            select coalesce(sum(b.bet_amount), 0)
                            from bets b 
                            where b.client_id == :clientID
                        )
                    """)

        moneyEarned = db.session.execute(statement, {"clientID": idClient}).first()[0]
        moneyEarned = 0 if moneyEarned is None else round(moneyEarned, 2)
        clientData['moneyEarned'] = moneyEarned

        return clientData


# Admin endopoints
@api_client.route("/<client_id>")
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self, client_id):
        client = Client.query.get_or_404(client_id)
        return ClientSchema().dump(client)

    @flask_praetorian.roles_required("admin")
    def delete(self, client_id):
        client = Client.query.get_or_404(client_id)
        db.session.delete(client)
        db.session.commit()
        return f"Deleted client {client_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, client_id):
        new_client = ClientSchema().load(request.json)
        if str(new_client.id) != client_id:
            abort(400, "id mismatch")
        db.session.commit()
        return ClientSchema().dump(new_client)


@api_client.route("/")
class ClientListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return ClientSchema(many=True).dump(Client.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        client = ClientSchema().load(request.json)
        db.session.add(client)
        db.session.commit()
        return ClientSchema().dump(client), 201
