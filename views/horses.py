import os
import uuid
import flask_praetorian
from flask import request, current_app
from flask_restx import Resource, Namespace, inputs
from sqlalchemy import text
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import apiKey_required
from model import Horse, db, Stud
from schema import HorseSchema, StudSchema

api_horse = Namespace("Horses", "Horses management")

# SWAGGER POST FORM FIELDS
parserPOST = api_horse.parser()
parserPOST.add_argument('EquineID', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Name', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Breed', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Age', type=float, location='form', required=True, nullable=False,
                        help='Introduce age in months')
parserPOST.add_argument('Image', type=FileStorage, location='files')
parserPOST.add_argument('Stud Name', type=str, location='form', required=True, nullable=False,
                        help='If horse´s stud is already registered, just fill Stud Name field, otherwise, fill all '
                             'fields')
parserPOST.add_argument('Stud Location', type=str, location='form', nullable=False)
parserPOST.add_argument('Stud E-mail', type=inputs.email(), location='form', nullable=False)

# SWAGGER PUT FORM FIELDS
parserPUT = api_horse.parser()
parserPUT.add_argument('EquineID', type=str, location='form', nullable=False)
parserPUT.add_argument('Name', type=str, location='form', nullable=False)
parserPUT.add_argument('Breed', type=str, location='form', nullable=False)
parserPUT.add_argument('Age', type=float, location='form', nullable=False, help='Introduce age in months')
parserPUT.add_argument('Image', type=FileStorage, location='files')
parserPUT.add_argument('New Stud (name)', type=str, location='form')


def getHorseWins(horseId):
    horse = Horse.query.get_or_404(horseId)
    horseData = HorseSchema().dump(horse)

    statement = text("""
                select rh.final_position, count(*) as times
                from runs_horses rh
                where rh.horse_id == :horseID
                group by rh.final_position
            """)
    result = db.session.execute(statement, {"horseID": horseId})
    data = [{'final_position': r['final_position'], 'times': r['times']} for r in result]

    timesFirst = 0
    timesSecond = 0
    timesThird = 0
    timesNotCelebrated = 0
    for d in data:
        if d.get('final_position') == 1: timesFirst = d.get('times')
        if d.get('final_position') == 2: timesSecond = d.get('times')
        if d.get('final_position') == 3: timesThird = d.get('times')
        if d.get('final_position') is None: timesNotCelebrated = d.get('times')
    horseData['timesFirst'] = timesFirst
    horseData['timesSecond'] = timesSecond
    horseData['timesThird'] = timesThird
    horseData['timesNotCelebrated'] = timesNotCelebrated
    horseData['timesOtherPosition'] = horseData.get(
        'total_runs') - timesFirst - timesSecond - timesThird - timesNotCelebrated

    return horseData


# Client endopoints
@api_horse.route("/detail/<horse_id>", doc=False)
class HorseController(Resource):
    @flask_praetorian.auth_required
    def get(self, horse_id):
        return getHorseWins(horse_id)


# Admin endopoints
@api_horse.route("/Horse/<EquineID>")
class HorseController(Resource):
    @apiKey_required
    def get(self, EquineID):
        """Shows a detailed horse from given EquineID."""
        horse = Horse.query.filter(Horse.equineID == EquineID).first()
        if horse:
            return HorseSchema().dump(horse), 200
        return "Horse not found", 404

    @apiKey_required
    @api_horse.doc(
        description='*Try it out* and introduce a horse id you want to delete; then, hit *Execute* button to '
                    'delete the desired horse from your database. In *Code* section you will see the '
                    'deleted horse (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, EquineID):
        """Deletes a run from given EquineID."""
        horse = Horse.query.filter(Horse.equineID == EquineID).first()
        if horse:
            horseData = HorseSchema().dump(horse)
            db.session.delete(horse)
            db.session.commit()
            return horseData, 200
        return "Horse not found", 404


@api_horse.route("/<Horse_id>")
class HorseController(Resource):
    @apiKey_required
    @api_horse.expect(parserPUT, validate=True)
    @api_horse.doc(description='*Try it out* and introduce the horse data and stud id you want to modify; then, '
                               'hit *Execute* button to apply your changes. In *Code* section you will see the '
                               'modified horse (*Code*) and a code for a succeded or failed operation.')
    def put(self, Horse_id):
        """Updates a horse with entry data and given id."""
        horse = Horse.query.get_or_404(Horse_id)

        if request.form.get("EquineID"): horse.equineID = request.form.get("EquineID")
        if request.form.get("Name"): horse.name = request.form.get("Name")
        if request.form.get("Breed"): horse.breed = request.form.get("Breed")
        if request.form.get("Age"): horse.age = request.form.get("Age")
        if 'Image' in request.files:
            newImage = request.files['Image']
            folder = current_app.root_path + "/static/images/"
            if horse.image != "default_horse.jpg": os.unlink(os.path.join(folder + horse.image))
            filename = str(uuid.uuid4().hex) + "_" + secure_filename(newImage.filename)
            newImage.save(folder + filename)
            horse.image = filename
        if request.form.get("New Stud (name)"):
            newStud = Stud.query.filter(Stud.name == request.form.get("New Stud (name)")).first()
            horse.stud_id = newStud.id

        db.session.commit()
        return HorseSchema().dump(horse), 200


@api_horse.route("/")
class HorseListController(Resource):
    @apiKey_required
    @api_horse.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                               'horses stored in your database (*Response body*) and a code for a succeded or failed '
                               'operation.')
    def get(self):
        """Shows a detailed list of horses."""
        return HorseSchema(many=True).dump(Horse.query.all()), 200

    @apiKey_required
    @api_horse.expect(parserPOST, validate=True)
    @api_horse.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                               'create a new horse in your database. In *Code* section you will see your new '
                               'horse (*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new horse from entry data."""
        horseRequest = {
            "equineID": request.form.get("EquineID"),
            "name": request.form.get("Name"),
            "breed": request.form.get("Breed"),
            "age": request.form.get("Age")
        }
        horse = HorseSchema().load(horseRequest)
        db.session.add(horse)

        if 'Image' in request.files:
            image = request.files['Image']
            filename = str(uuid.uuid4().hex) + "_" + secure_filename(image.filename)
            folder = current_app.root_path + "/static/images/"
            image.save(folder + filename)
            horse.image = filename

        if request.form.get("Stud Name") not in [r.name for r in db.session.query(Stud.name)]:
            studRequest = {
                "name": request.form.get("Stud Name"),
                "location": request.form.get("Stud Location"),
                "email": request.form.get("Stud E-mail")
            }
            stud = StudSchema().load(studRequest)
            db.session.add(stud)
        else:
            stud = Stud.query.filter(Stud.name == request.form.get("Stud Name")).first()
        stud.horses.append(horse)

        db.session.commit()
        return HorseSchema().dump(horse), 200
