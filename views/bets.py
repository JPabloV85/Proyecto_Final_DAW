import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text

from model import Bets, db
from schema import BetsSchema

api_bet = Namespace("Bets", "Bets management")


@api_bet.route("/<bet_id>")
class BetController(Resource):
    @flask_praetorian.auth_required
    def get(self, bet_id):
        bet = Bets.query.get_or_404(bet_id)
        return BetsSchema().dump(bet)

    @flask_praetorian.roles_required("admin")
    def delete(self, bet_id):
        bet = Bets.query.get_or_404(bet_id)
        db.session.delete(bet)
        db.session.commit()
        return f"Deleted bet {bet_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, bet_id):
        new_bet = BetsSchema().load(request.json)
        if str(new_bet.id) != bet_id:
            abort(400, "id mismatch")
        db.session.commit()
        return BetsSchema().dump(new_bet)


@api_bet.route("/")
class RegionListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return BetsSchema(many=True).dump(Bets.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        bet = BetsSchema().load(request.json)
        db.session.add(bet)
        db.session.commit()
        return BetsSchema().dump(bet), 201
