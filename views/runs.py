import time
import flask_praetorian
from datetime import datetime
from flask import request, jsonify
from flask_restx import Resource, Namespace
from sqlalchemy import text
from config import apiKey_required
from model import Run, db, Horse
from schema import RunSchema

api_run = Namespace("Runs", "Runs management")

# SWAGGER POST FORM FIELDS
parserPOST = api_run.parser()
parserPOST.add_argument('Tag', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Date', type=str, location='form', required=True, nullable=False,
                        help='Introduce date in proper format: DD/MM/YYYY')
parserPOST.add_argument('Time', type=str, location='form', required=True, nullable=False,
                        help='Introduce time in proper format: HH:MM')

# SWAGGER PUT FORM FIELDS
parserPUT = api_run.parser()
parserPUT.add_argument('Tag', type=str, location='form', nullable=False)
parserPUT.add_argument('Date', type=str, location='form', nullable=False, help='Introduce date in proper format: DD/MM/YYYY')
parserPUT.add_argument('Time', type=str, location='form', nullable=False, help='Introduce time in proper format: HH:MM')
parserPUT.add_argument('Add Horse (equineID)', type=str, location='form', nullable=False)
parserPUT.add_argument('Remove Horse (equineID)', type=str, location='form', nullable=False)


# Client endopoints
@api_run.route("/available", doc=False)
class RunListController(Resource):
    @flask_praetorian.auth_required
    def get(self, ):
        today = datetime.now().strftime("%d/%m/%Y")
        now = datetime.now().strftime("%H:%M")
        today_now = today + " " + now
        statement = text("""
                            select * from (select r.id, r.tag, r.date, r.time, count(rh.horse_id) as horses
                                            from run r
                                            join runs_horses rh on r.id = rh.run_id
                                            where r.date || " " || r.time  > :today_now
                                            group by rh.run_id
                                            order by r.date, r.time
                                            )
                            where horses = 5
                        """)
        result = db.session.execute(statement, {"today_now": today_now})
        return jsonify([{'id': r['id'], 'race_tag': r['tag'], 'date': r['date'], 'time': r['time']} for r in result])


# Admin endopoints
@api_run.route("/Run/<Tag>")
class RunController(Resource):
    @apiKey_required
    def get(self, Tag):
        """Shows a detailed run from given Tag."""
        run = Run.query.filter(Run.tag == Tag).first()
        if run:
            return RunSchema().dump(run), 200
        return "Run not found", 404

    @apiKey_required
    @api_run.doc(description='*Try it out* and introduce a run id you want to delete; then, hit *Execute* button to '
                             'delete the desired run from your database. In *Code* section you will see the '
                             'deleted run (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, Tag):
        """Deletes a run from given Tag."""
        run = Run.query.filter(Run.tag == Tag).first()
        if run:
            db.session.delete(run)
            db.session.commit()
            return RunSchema().dump(run), 200
        return "Run not found", 404


@api_run.route("/<Run_id>")
class RunController(Resource):
    @apiKey_required
    @api_run.expect(parserPUT, validate=True)
    @api_run.doc(description='*Try it out* and introduce the run data and run id you want to modify; then, '
                             'hit *Execute* button to apply your changes. In *Code* section you will see the '
                             'modified run (*Code*) and a code for a succeded or failed operation.')
    def put(self, Run_id):
        """Modify a run with entry data and given id."""
        run = Run.query.get_or_404(Run_id)

        if request.form.get("Tag"): run.tag = request.form.get("Tag")
        if request.form.get("Date"):
            try:
                datetime.strptime(request.form.get("Date"), '%d/%m/%Y')
                run.date = request.form.get("Date")
            except:
                return "Incorrect date format, should be DD/MM/YYYY", 500

        if request.form.get("Time"):
            try:
                time.strptime(request.form.get("Time"), '%H:%M')
                run.time = request.form.get("Time")
            except:
                return "Incorrect time format, should be HH:MM", 500

        if request.form.get("Add Horse (equineID)"):
            horse = Horse.query.filter(Horse.equineID == request.form.get("Add Horse (equineID)")).first()
            run.horses.append(horse)
        if request.form.get("Remove Horse (equineID)"):
            horse = Horse.query.filter(Horse.equineID == request.form.get("Remove Horse (equineID)")).first()
            if horse in run.horses: run.horses.remove(horse)

        db.session.commit()
        return RunSchema().dump(run), 200


@api_run.route("/")
class RunListController(Resource):
    @apiKey_required
    @api_run.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                             'runs stored in your database (*Response body*) and a code for a succeded or failed '
                             'operation.')
    def get(self):
        """Shows a detailed list of runs."""
        return RunSchema(many=True).dump(Run.query.all()), 200

    @apiKey_required
    @api_run.expect(parserPOST, validate=True)
    @api_run.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                             'create a new run in your database. In *Code* section you will see your new '
                             'run (*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new run from entry data."""

        try:
            datetime.strptime(request.form.get("Date"), '%d/%m/%Y')
        except:
            return "Incorrect date format, should be DD/MM/YYYY", 500

        try:
            time.strptime(request.form.get("Time"), '%H:%M')
        except:
            return "Incorrect time format, should be HH:MM", 500

        runRequest = {
            "tag": request.form.get("Tag"),
            "date": request.form.get("Date"),
            "time": request.form.get("Time")
        }
        run = RunSchema().load(runRequest)
        db.session.add(run)
        db.session.commit()
        return RunSchema().dump(run), 200
