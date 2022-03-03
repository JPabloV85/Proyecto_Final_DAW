import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text

from model import Runs_Horses, db
from schema import Runs_HorsesSchema

api_run_horse = Namespace("Runs_Horses", "Runs_Horses management")

"""
Consulta de Run_Horse por runId y horseId para hacer una bet

@api_run_horse.route("/<run_id>/<horse_id>")
class Runs_HorsesController(Resource):
    @flask_praetorian.auth_required
    def get(self, run_id, horse_id):
        runs_horses = Runs_Horses.query.filter(Runs_Horses.run_id == run_id,
                                               Runs_Horses.horse_id == horse_id)
        return Runs_HorsesSchema(many=True).dump(runs_horses)
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
