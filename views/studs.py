from flask import request
from flask_restx import Resource, Namespace, inputs
from config import apiKey_required
from model import Stud, db
from schema import StudSchema

api_stud = Namespace("Studs", "Studs management")

# SWAGGER POST FORM FIELDS
parserPOST = api_stud.parser()
parserPOST.add_argument('Name', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('Location', type=str, location='form', required=True, nullable=False)
parserPOST.add_argument('E-mail', type=inputs.email(), location='form', required=True, nullable=False)

# SWAGGER PUT FORM FIELDS
parserPUT = api_stud.parser()
parserPUT.add_argument('Name', type=str, location='form', nullable=False)
parserPUT.add_argument('Location', type=str, location='form', nullable=False)
parserPUT.add_argument('E-mail', type=inputs.email(), location='form', nullable=False)


# Admin endopoints
@api_stud.route("/<Stud_id>")
class StudController(Resource):
    @apiKey_required
    def get(self, Stud_id):
        """Shows a detailed stud from given id."""
        stud = Stud.query.get_or_404(Stud_id)
        return StudSchema().dump(stud), 200

    @apiKey_required
    @api_stud.doc(description='*Try it out* and introduce a stud id you want to delete; then, hit *Execute* button to '
                              'delete the desired stud from your database. In *Code* section you will see the '
                              'deleted stud (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, Stud_id):
        """Deletes a stud from given id."""
        stud = Stud.query.get_or_404(Stud_id)
        db.session.delete(stud)
        db.session.commit()
        return StudSchema().dump(stud), 200

    @apiKey_required
    @api_stud.expect(parserPUT, validate=True)
    @api_stud.doc(description='*Try it out* and introduce the stud data and stud id you want to modify; then, '
                              'hit *Execute* button to apply your changes. In *Code* section you will see the '
                              'modified stud (*Code*) and a code for a succeded or failed operation.')
    def put(self, Stud_id):
        """Updates a stud with entry data and given id."""
        stud = Stud.query.get_or_404(Stud_id)

        if request.form.get("Name"): stud.name = request.form.get("Name")
        if request.form.get("Location"): stud.location = request.form.get("Location")
        if request.form.get("E-mail"): stud.email = request.form.get("E-mail")

        db.session.commit()
        return StudSchema().dump(stud), 200


@api_stud.route("/")
class StudListController(Resource):
    @apiKey_required
    @api_stud.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                              'studs stored in your database (*Response body*) and a code for a succeded or failed '
                              'operation.')
    def get(self):
        """Shows a detailed list of studs."""
        return StudSchema(many=True).dump(Stud.query.all()), 200

    @apiKey_required
    @api_stud.expect(parserPOST, validate=True)
    @api_stud.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                              'create a new stud in your database. In *Code* section you will see your new '
                              'stud (*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new stud from entry data."""
        studRequest = {
            "name": request.form.get("Name"),
            "location": request.form.get("Location"),
            "email": request.form.get("E-mail")
        }
        stud = StudSchema().load(studRequest)
        db.session.add(stud)
        db.session.commit()
        return StudSchema().dump(stud), 200
