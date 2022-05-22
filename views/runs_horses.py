from functools import wraps
import flask_praetorian
from flask import request, jsonify
from flask_restx import Resource, Namespace
from sqlalchemy import text
from config import API_KEY
from model import Runs_Horses, db, Bet, Run, Horse
from schema import RunSchema
from views.clients import getClientIDFromToken

api_run_horse = Namespace("Runs_Horses", "Runs_Horses management")

# SWAGGER PUT FORM FIELDS
parserPUT = api_run_horse.parser()
parserPUT.add_argument('Run Tag', type=str, location='form', required=True)
parserPUT.add_argument('Horse(equineID)', type=str, location='form', required=True)
parserPUT.add_argument('Position', type=int, location='form', required=True, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


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


# Client endopoints
@api_run_horse.route("/getHorses", doc=False)
class Runs_HorsesController(Resource):
    @flask_praetorian.auth_required
    def post(self):
        # Busco runs_horses en función del id de la carrera para ver todos los caballos inscritos en la misma
        # Recojo la información de los caballos
        run_id = int(request.json.get("race_id"))
        statement = text("""
                            select rh.id, horse_id, h.name, h.win_ratio
                            from runs_horses rh
                            join horse h on horse_id = h.id
                            where run_id = :runID
                        """)
        result = db.session.execute(statement, {"runID": run_id})
        runs_horses = jsonify([{'id': r['id'],
                                'horse_id': r['horse_id'],
                                'horse_name': r['name'],
                                'win_ratio': r['win_ratio']
                                } for r in result])

        # Busco apuestas del cliente sobre los distintos caballos de cada run, es decir, sobre cada run_horse.
        # Por cada caballo recogido anteriormente introduzco TRUE si ya hay una apuesta hecha, y FALSE si no la hay
        idClient = getClientIDFromToken(request)
        new_horses_response = []
        for run_horse in runs_horses.json:
            bet = Bet.query.filter(Bet.client_id == idClient, Bet.run_horse_id == run_horse.get('id')).first()
            if bet:
                run_horse['bet_done'] = True
            else:
                run_horse['bet_done'] = False
            new_horses_response.append(run_horse)

        return new_horses_response


# Admin endopoints
@api_run_horse.route("/<Runtag>")
class Runs_HorsesController(Resource):
    @apiKey_required
    def get(self, Runtag):
        """Shows a detailed run with registered horses along with their positions."""
        run = RunSchema().dump(Run.query.filter(Run.tag == Runtag).first())
        statement = text("""
                        select rh.horse_id, rh.final_position 
                        from runs_horses rh
                        where rh.run_id == :runId
                        order by rh.horse_id asc
                    """)
        result = db.session.execute(statement, {"runId": run.get('id')})
        for horse, r in zip(run.get("horses"), result):
            if r['final_position'] is None:
                horse["position"] = "-"
            else:
                horse["position"] = r['final_position']
        return run, 200


@api_run_horse.route("/")
class Runs_HorsesListController(Resource):
    @apiKey_required
    def get(self):
        """Shows a detailed list of runs with registered horses along with their positions."""
        runs = RunSchema(many=True).dump(Run.query.all())
        for run in runs:
            statement = text("""
                select rh.horse_id, rh.final_position 
                from runs_horses rh
                where rh.run_id == :runId
                order by rh.horse_id asc
            """)
            result = db.session.execute(statement, {"runId": run.get('id')})
            for horse, r in zip(run.get("horses"), result):
                if r['final_position'] is None:
                    horse["position"] = "-"
                else:
                    horse["position"] = r['final_position']
        return runs, 200

    @apiKey_required
    @api_run_horse.expect(parserPUT, validate=True)
    def put(self):
        """Update horses final position for a given run tag"""
        run = Run.query.filter(Run.tag == request.form.get("Run Tag")).first()
        horse = Horse.query.filter(Horse.equineID == request.form.get("Horse(equineID)")).first()

        run_horse = Runs_Horses.query.filter(Runs_Horses.run_id == run.id, Runs_Horses.horse_id == horse.id).first()
        run_horse.final_position = request.form.get("Position")

        db.session.commit()
        return "Horse " + horse.equineID + " final position set to: " + str(run_horse.final_position), 200
