import os
import uuid
from functools import wraps
import flask_praetorian
from flask import request, current_app
from flask_restx import Resource, Namespace, inputs
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import API_KEY
from model import Horse, db, Runs_Horses, Stud
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
@api_horse.route("/detail/<horse_id>", doc=False)
class HorseController(Resource):
    @flask_praetorian.auth_required
    def get(self, horse_id):
        horse = Horse.query.get_or_404(horse_id)
        horseData = HorseSchema().dump(horse)

        timesFirst = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id, Runs_Horses.final_position == 1).count()
        timesSecond = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id,
                                               Runs_Horses.final_position == 2).count()
        timesThird = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id, Runs_Horses.final_position == 3).count()

        horseData['timesFirst'] = timesFirst
        horseData['timesSecond'] = timesSecond
        horseData['timesThird'] = timesThird

        return horseData


# Admin endopoints
@api_horse.route("/<horse_id>")
class HorseController(Resource):
    @apiKey_required
    def get(self, horse_id):
        """Shows a detailed horse from given id."""
        horse = Horse.query.get_or_404(horse_id)
        return HorseSchema().dump(horse), 200

    @apiKey_required
    @api_horse.doc(
        description='*Try it out* and introduce a horse id you want to delete; then, hit *Execute* button to '
                    'delete the desired horse from your database. In *Code* section you will see the '
                    'deleted horse (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, horse_id):
        """Deletes a run from given id."""
        horse = Horse.query.get_or_404(horse_id)
        horseData = HorseSchema().dump(horse)
        db.session.delete(horse)
        db.session.commit()
        return horseData, 200

    @apiKey_required
    @api_horse.expect(parserPUT, validate=True)
    @api_horse.doc(description='*Try it out* and introduce the horse data and stud id you want to modify; then, '
                               'hit *Execute* button to apply your changes. In *Code* section you will see the '
                               'modified horse (*Code*) and a code for a succeded or failed operation.')
    def put(self, horse_id):
        """Updates a horse with entry data and given id."""
        horse = Horse.query.get_or_404(horse_id)

        if request.form.get("EquineID"):
            horse.equineID = request.form.get("EquineID")
        if request.form.get("Name"):
            horse.name = request.form.get("Name")
        if request.form.get("Breed"):
            horse.breed = request.form.get("Breed")
        if request.form.get("Age"):
            horse.age = request.form.get("Age")
        if 'Image' in request.files:
            newImage = request.files['Image']
            folder = current_app.root_path + "/static/images/"
            if horse.image != "default_horse.jpg":
                os.unlink(os.path.join(folder + horse.image))
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
