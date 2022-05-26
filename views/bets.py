from functools import wraps
import flask_praetorian
from flask import request, jsonify
from flask_restx import Resource, Namespace
from sqlalchemy import text
from config import API_KEY
from model import Bet, db, Runs_Horses, Client
from schema import BetSchema
from views.clients import getClientIDFromToken

api_bet = Namespace("Bets", "Bets management")


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


# functions
def reformatBet(bet):
    betData = BetSchema().dump(bet)

    statement = text("""
                        select r.tag, h.equineID
                        from runs_horses rh
                        join run r
                        join horse h
                        where rh.id == :runHorseId and r.id == rh.run_id and h.id == rh.horse_id
                    """)
    result = db.session.execute(statement, {"runHorseId": bet.run_horse_id}).first()

    betData["run_Tag"] = result[0]
    betData["horse_EquineID"] = result[1]
    if betData.get("client"):
        username = betData.get("client").get("user").get("username")
        betData["client_Username"] = username
        del betData["client"]
    del betData["run_horse_id"]

    return betData


# Client endopoints
@api_bet.route("/my_bets", doc=False)
class BetController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        idClient = getClientIDFromToken(request)
        statement = text("""
                    select b.id, b.win, b.bet_amount, b.payment_amount, b.claimed, b.created_on, r.tag, h.name, 
                        rh.run_id, rh.horse_id
                    from bet b
                    join client c on c.id = b.client_id
                    join runs_horses rh on b.run_horse_id = rh.id
                    join run r on rh.run_id = r.id
                    join horse h on rh.horse_id = h.id
                    where client_id = :clientID
                    order by b.created_on desc
                """)
        result = db.session.execute(statement, {"clientID": idClient})
        return jsonify([{'id': r['id'],
                         'race_tag': r['tag'],
                         'horse_name': r['name'],
                         'win': r['win'],
                         'bet_amount': r['bet_amount'],
                         'payment_amount': r['payment_amount'],
                         'date': r['created_on'].split()[0],
                         'time': r['created_on'].split()[1],
                         'claimed': r['claimed']
                         } for r in result])


@api_bet.route("/client_new_bet", doc=False)
class BetController(Resource):
    @flask_praetorian.auth_required
    def post(self):
        run_id = int(request.json.get("race_id"))
        horse_id = int(request.json.get("horse_id"))
        run_horse = Runs_Horses.query.filter(Runs_Horses.run_id == run_id, Runs_Horses.horse_id == horse_id).first()
        idClient = getClientIDFromToken(request)

        del request.json["race_id"]
        del request.json["horse_id"]
        bet = BetSchema().load(request.json)
        setattr(bet, "client_id", idClient)
        setattr(bet, "run_horse_id", run_horse.id)
        db.session.add(bet)
        bet.payment_amount = round(float(request.json.get("bet_amount")) * float(request.json.get("benefit_ratio")), 2)

        client = Client.query.get_or_404(idClient)
        bet_amount = float(request.json.get("bet_amount"))
        client.cash = round(client.cash - bet_amount, 2)

        db.session.commit()
        return jsonify({'new_cash': client.cash})


# Admin endopoints
@api_bet.route("/<bet_id>")
class BetController(Resource):
    @apiKey_required
    @api_bet.doc(description='*Try it out* and introduce a bet id you want to see; then, hit *Execute* button to '
                             'show the desired bet from your database. In *Code* section you will see the bet ('
                             '*Response body*) and a code for a succeded or failed operation.')
    def get(self, bet_id):
        """Shows a detailed bet from given id."""
        bet = Bet.query.get_or_404(bet_id)
        return reformatBet(bet), 200

    @apiKey_required
    @api_bet.doc(description='*Try it out* and introduce a bet id you want to delete; then, hit *Execute* button to '
                             'delete the desired bet from your database. In *Code* section you will see the '
                             'deleted bet (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, bet_id):
        """Deletes a bet from given id."""
        bet = Bet.query.get_or_404(bet_id)
        client = Client.query.get_or_404(bet.client_id)

        # Si la recompensa está reclamada se la quito al cash del cliente
        # Devuelvo la cantidad apostada al cash del cliente
        if bet.claimed: client.cash -= bet.payment_amount
        client.cash += bet.bet_amount

        betData = reformatBet(bet)
        db.session.delete(bet)
        db.session.commit()
        return betData, 200


@api_bet.route("/client/<Username>")
class BetListController(Resource):
    @apiKey_required
    @api_bet.doc(description='*Try it out* and introduce a client username, then, hit *Execute* button to show a list '
                             'of your client bets. In *Code* section you will see the list (*Response body*) and a '
                             'code for a succeded or failed operation.')
    def get(self, Username):
        """Shows a detailed list of bets from given Client username."""
        statement = text("""
                            select b.*
                            from bet b
                            join client c on c.id = b.client_id
                            join user u on u.id = c.user_id
                            where u.username = :userName
                        """)
        result = db.session.execute(statement, {"userName": Username}).all()

        betsListData = []
        for bet in result: betsListData.append(reformatBet(bet))

        return betsListData, 200
