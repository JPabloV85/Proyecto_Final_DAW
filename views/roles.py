import flask_praetorian
from flask import request
from flask_restx import abort, Resource, Namespace
from model import Role, db
from schema import RoleSchema

api_role = Namespace("Roles", "Roles management")


# Admin endopoints
@api_role.route("/<role_id>")
class RoleController(Resource):
    @flask_praetorian.auth_required
    def get(self, role_id):
        role = Role.query.get_or_404(role_id)
        return RoleSchema().dump(role)

    @flask_praetorian.roles_required("admin")
    def delete(self, role_id):
        role = Role.query.get_or_404(role_id)
        db.session.delete(role)
        db.session.commit()
        return f"Deleted role {role_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, role_id):
        new_role = RoleSchema().load(request.json)
        if str(new_role.id) != role_id:
            abort(400, "id mismatch")
        db.session.commit()
        return RoleSchema().dump(new_role)


@api_role.route("/")
class RoleListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return RoleSchema(many=True).dump(Role.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        role = RoleSchema().load(request.json)
        db.session.add(role)
        db.session.commit()
        return RoleSchema().dump(role), 201
