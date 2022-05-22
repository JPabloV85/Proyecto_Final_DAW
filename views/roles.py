from functools import wraps
from flask import request
from flask_restx import Resource, Namespace
from config import API_KEY
from model import Role, db
from schema import RoleSchema

api_role = Namespace("Roles", "Roles management")

# SWAGGER FORM FIELDS
parser = api_role.parser()
parser.add_argument('Name', type=str, location='form', required=True, nullable=False)


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


# Admin endopoints
@api_role.route("/<int:role_id>")
class RoleController(Resource):
    @apiKey_required
    def get(self, role_id):
        """Shows a detailed role from given id."""
        role = Role.query.get_or_404(role_id)
        return RoleSchema().dump(role), 200

    @apiKey_required
    @api_role.doc(description='*Try it out* and introduce a role id you want to delete; then, hit *Execute* button to '
                              'delete the desired role from your database. In *Code* section you will see the '
                              'deleted role (*Response body*) and a code for a succeded or failed operation.')
    def delete(self, role_id):
        """Deletes a role from given id."""
        role = Role.query.get_or_404(role_id)
        db.session.delete(role)
        db.session.commit()
        return RoleSchema().dump(role), 200

    @apiKey_required
    @api_role.expect(parser, validate=True)
    @api_role.doc(description='*Try it out* and introduce the role data and role id you want to modify; then, '
                              'hit *Execute* button to apply your changes. In *Code* section you will see the '
                              'modified role (*Code*) and a code for a succeded or failed operation.')
    def put(self, role_id):
        """Updates a role with entry data and given id."""
        role = Role.query.get_or_404(role_id)
        role.name = request.form.get("Name")
        db.session.commit()
        return RoleSchema().dump(role), 200


@api_role.route("/")
class RoleListController(Resource):
    @apiKey_required
    @api_role.doc(description='*Try it out* and hit *Execute* button. In *Code* section you will see a list of '
                              'roles stored in your database (*Response body*) and a code for a succeded or failed '
                              'operation.')
    def get(self):
        """Shows a detailed list of roles."""
        return RoleSchema(many=True).dump(Role.query.all()), 200

    @apiKey_required
    @api_role.expect(parser, validate=True)
    @api_role.doc(description='*Try it out* and introduce some values in fields below; then, hit *Execute* button to '
                              'create a new role in your database. In *Code* section you will see your new '
                              'role (*Response body*) and a code for a succeded or failed operation.')
    def post(self):
        """Creates a new role from entry data."""
        roleRequest = {
            "name": request.form.get("Name")
        }
        role = RoleSchema().load(roleRequest)
        db.session.add(role)
        db.session.commit()
        return RoleSchema().dump(role), 200
