import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text

from model import Client, db
from schema import ClientSchema

api_client = Namespace("Clients", "Clients management")


@api_client.route("/<client_id>/bets")
class ClientController(Resource):
    @flask_praetorian.auth_required
    def get(self, client_id):
        statement = text("""
                            select bets.id,
                                   bets.bet_position,
                                   rh.final_position,
                                   bets.win,
                                   bets.bet_amount,
                                   rh.total_bet,
                                   bets.benefit_ratio,
                                   bets.payment_amount
                            from bets
                            join client c on c.id = bets.client_id
                            join runs_horses rh on bets.run_horse_id = rh.id
                            where client_id = :clientID
                        """)
        result = db.session.execute(statement, {"clientID": client_id})
        return jsonify([{'id': r['id'],
                         'bet_position': r['bet_position'],
                         'final_position': r['final_position'],
                         'win': r['win'],
                         'bet_amount': r['bet_amount'],
                         'total_run_horse_bets': r['total_bet'],
                         'benefit_ratio': r['benefit_ratio'],
                         'payment_amount': r['payment_amount']
                         } for r in result])


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
