import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text
from model import Runs_Horses, db, Bets
from schema import Runs_HorsesSchema
from views.clients import getClientIDFromToken

api_run_horse = Namespace("Runs_Horses", "Runs_Horses management")

""" 
Client endopoints 
"""


@api_run_horse.route("/getHorses")
class Runs_HorsesController(Resource):
    @flask_praetorian.auth_required
    def post(self):
        """
        Busco runs_horses en función del id de la carrera para ver todos los caballos inscritos en la misma
        Recojo la información de los caballos
        """
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

        """
        Busco apuestas del cliente sobre los distintos caballos de cada run, es decir, sobre cada run_horse.
        Por cada caballo recogido anteriormente introduzco TRUE si ya hay una apuesta hecha, y FALSE si no la hay
        """
        idClient = getClientIDFromToken(request)
        new_horses_response = []
        for run_horse in runs_horses.json:
            bet = Bets.query.filter(Bets.client_id == idClient, Bets.run_horse_id == run_horse.get('id')).first()
            if bet:
                run_horse['bet_done'] = True
            else:
                run_horse['bet_done'] = False
            new_horses_response.append(run_horse)

        return new_horses_response


""" 
Admin endopoints 
"""


@api_run_horse.route("/<runs_horses_id>")
class Runs_HorsesController(Resource):
    @flask_praetorian.auth_required
    def get(self, run_horse_id):
        run_horse = Runs_Horses.query.get_or_404(run_horse_id)
        return Runs_HorsesSchema().dump(run_horse)

    @flask_praetorian.roles_required("admin")
    def delete(self, run_horse_id):
        run_horse = Runs_Horses.query.get_or_404(run_horse_id)
        db.session.delete(run_horse)
        db.session.commit()
        return f"Deleted run_horse {run_horse_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, run_horse_id):
        new_run_horse = Runs_HorsesSchema().load(request.json)
        if str(new_run_horse.id) != run_horse_id:
            abort(400, "id mismatch")
        db.session.commit()
        return Runs_HorsesSchema().dump(new_run_horse)


@api_run_horse.route("/")
class Runs_HorsesListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return Runs_HorsesSchema(many=True).dump(Runs_Horses.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        run_horse = Runs_HorsesSchema().load(request.json)
        db.session.add(run_horse)
        db.session.commit()
        return Runs_HorsesSchema().dump(run_horse), 201
