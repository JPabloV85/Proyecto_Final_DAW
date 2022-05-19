import flask_praetorian
from flask import request
from flask_restx import Resource, Namespace
from flask_restx.inputs import email

from model import Stud, db
from schema import StudSchema

api_stud = Namespace("Studs", "Studs management")

# SWAGGER FORM FIELDS
parser = api_stud.parser()
parser.add_argument('name', type=str, location='form', required=True, nullable=False)
parser.add_argument('location', type=str, location='form', required=True, nullable=False)
parser.add_argument('email', type=email(), location='form', required=True, nullable=False)

# Form file uploads
# parser.add_argument('image', type=FileStorage, location='files', required=True)


# Admin endopoints
@api_stud.route("/<int:stud_id>")
class StudController(Resource):
    @flask_praetorian.auth_required
    def get(self, stud_id):
        """Shows a detailed stud from given id."""
        stud = Stud.query.get_or_404(stud_id)
        return StudSchema().dump(stud), 200

    @flask_praetorian.roles_required("admin")
    @api_stud.doc(description='*Try it out* and introduce a stud id you want to delete; then, hit *Execute* button to '
                              'delete the desired stud from your database. In *Code* section you will see the '
                              'deleted stud (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, stud_id):
        """Deletes a stud from given id."""
        stud = Stud.query.get_or_404(stud_id)
        db.session.delete(stud)
        db.session.commit()
        return StudSchema().dump(stud), 200

    @flask_praetorian.roles_required("admin")
    @api_stud.expect(parser, validate=True)
    @api_stud.doc(description='*Try it out* and introduce the stud data and stud id you want to modify; then, '
                              'hit *Execute* button to apply your changes. In *Code* section you will see the '
                              'modified stud (*Code*) and a code for a succeded or failed operation.')
    def put(self, stud_id):
        """Updates a stud with entry data and given id."""
        stud = Stud.query.get_or_404(stud_id)

        stud.name = request.form.get("name")
        stud.location = request.form.get("location")
        stud.email = request.form.get("email")

        db.session.commit()
        return StudSchema().dump(stud), 200


@api_stud.route("/")
class StudListController(Resource):
    @flask_praetorian.auth_required
    @api_stud.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                              'studs stored in your database (*Response body*) and a code for a succeded or failed '
                              'operation.')
    def get(self):
        """Shows a detailed list of studs."""
        return StudSchema(many=True).dump(Stud.query.all()), 200

    @flask_praetorian.roles_required("admin")
    @api_stud.expect(parser, validate=True)
    @api_stud.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                              'create a new entry in your database. In *Code* section you will see your new '
                              'object (*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new stud from entry data."""
        studRequest = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "email": request.form.get("email")
        }
        stud = StudSchema().load(studRequest)
        db.session.add(stud)
        db.session.commit()
        return StudSchema().dump(stud), 200
