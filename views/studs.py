import flask_praetorian
from flask import request
from flask_restx import abort, Resource, Namespace
from model import Stud, db
from schema import StudSchema

api_stud = Namespace("Studs", "Studs management")


@api_stud.route("/<stud_id>")
class StudController(Resource):
    @flask_praetorian.auth_required
    def get(self, stud_id):
        stud = Stud.query.get_or_404(stud_id)
        return StudSchema().dump(stud)

    @flask_praetorian.roles_required("admin")
    def delete(self, stud_id):
        stud = Stud.query.get_or_404(stud_id)
        db.session.delete(stud)
        db.session.commit()
        return f"Deleted stud {stud_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, stud_id):
        new_stud = StudSchema().load(request.json)
        if str(new_stud.id) != stud_id:
            abort(400, "id mismatch")
        db.session.commit()
        return StudSchema().dump(new_stud)


@api_stud.route("/")
class StudListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return StudSchema(many=True).dump(Stud.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        stud = StudSchema().load(request.json)
        db.session.add(stud)
        db.session.commit()
        return StudSchema().dump(stud), 201
