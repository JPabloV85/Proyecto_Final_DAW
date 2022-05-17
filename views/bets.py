import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text
from model import Bets, db, Runs_Horses, Client
from schema import BetsSchema
from views.clients import getClientIDFromToken

api_bet = Namespace("Bets", "Bets management")


# Client endopoints
@api_bet.route("/my_bets")
class BetController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        statement = text("""
                    select bets.id,
                           bets.bet_position,
                           rh.final_position,
                           bets.win,
                           bets.bet_amount,
                           rh.total_bet,
                           bets.benefit_ratio,
                           bets.payment_amount,
                           bets.claimed,
                           bets.created_on,
                           r.tag,
                           h.name,
                           rh.run_id,
                           rh.horse_id
                    from bets
                    join client c on c.id = bets.client_id
                    join runs_horses rh on bets.run_horse_id = rh.id
                    join run r on rh.run_id = r.id
                    join horse h on rh.horse_id = h.id
                    where client_id = :clientID
                    order by bets.created_on desc
                """)
        result = db.session.execute(statement, {"clientID": idClient})
        return jsonify([{'id': r['id'],
                         'race_tag': r['tag'],
                         'horse_name': r['name'],
                         'bet_position': r['bet_position'],
                         'final_position': r['final_position'],
                         'win': r['win'],
                         'bet_amount': r['bet_amount'],
                         'total_run_horse_bets': r['total_bet'],
                         'benefit_ratio': r['benefit_ratio'],
                         'payment_amount': r['payment_amount'],
                         'date': r['created_on'].split()[0],
                         'time': r['created_on'].split()[1],
                         'claimed': r['claimed']
                         } for r in result])


@api_bet.route("/client_new_bet")
class BetController(Resource):
    @flask_praetorian.auth_required
    def post(self):
        run_id = int(request.json.get("race_id"))
        horse_id = int(request.json.get("horse_id"))
        run_horse = Runs_Horses.query.filter(Runs_Horses.run_id == run_id, Runs_Horses.horse_id == horse_id)
        idRunHorse = run_horse[0].id
        idClient = getClientIDFromToken(request)

        del request.json["race_id"]
        del request.json["horse_id"]
        bet = BetsSchema().load(request.json)
        setattr(bet, "client_id", idClient)
        setattr(bet, "run_horse_id", idRunHorse)
        db.session.add(bet)

        client = Client.query.get_or_404(idClient)
        bet_amount = float(request.json.get("bet_amount"))
        client.cash = round(client.cash - bet_amount, 2)

        db.session.commit()
        return jsonify({'new_cash': client.cash})


# Admin endopoints
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
