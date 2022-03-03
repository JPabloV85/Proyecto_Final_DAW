import flask_praetorian
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace
from sqlalchemy import text

from model import Run, db
from schema import RunSchema

api_run = Namespace("Runs", "Runs management")


@api_run.route("/available")
class RunListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        statement = text("""
                            select * from (select run.id, run.date, run.time, count(rh.horse_id) as horses
                                from run
                                join runs_horses rh on run.id = rh.run_id
                                group by rh.run_id
                                )
                            where horses > 1
                        """)
        result = db.session.execute(statement)
        return jsonify([{'id': r['id'], 'date': r['date'], 'time': r['time']} for r in result])


@api_run.route("/<run_id>")
class RegionController(Resource):
    @flask_praetorian.auth_required
    def get(self, run_id):
        run = Run.query.get_or_404(run_id)
        return RunSchema().dump(run)

    @flask_praetorian.roles_required("admin")
    def delete(self, run_id):
        run = Run.query.get_or_404(run_id)
        db.session.delete(run)
        db.session.commit()
        return f"Deleted run {run_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, run_id):
        new_run = RunSchema().load(request.json)
        if str(new_run.id) != run_id:
            abort(400, "id mismatch")
        db.session.commit()
        return RunSchema().dump(new_run)


@api_run.route("/")
class RunListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return RunSchema(many=True).dump(Run.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        run = RunSchema().load(request.json)
        db.session.add(run)
        db.session.commit()
        return RunSchema().dump(run), 201
