from flask import Blueprint
from flask_restx import Api
import flask_praetorian

# import namespaces
from .studs import api_stud
from .horses import api_horse
from .runs import api_run
from .users import api_user
from .roles import api_role
from .clients import api_client
from .runs_horses import api_run_horse
from .bets import api_bet

# one blueprint (Flask) for all the resources
blueprint = Blueprint('Click Championship', __name__)
api = Api(blueprint, title="Click Championship", version="1.0", description="Not the best way to train your finger ;)", doc="/docs")
flask_praetorian.PraetorianError.register_error_handler_with_flask_restx(api_client)

# every resource in a namespace (RestX)
api.add_namespace(api_stud, path='/stud')
api.add_namespace(api_horse, path='/horse')
api.add_namespace(api_run, path='/run')
api.add_namespace(api_run_horse, path='/run_horse')
api.add_namespace(api_user, path='/user')
api.add_namespace(api_role, path='/role')
api.add_namespace(api_client, path='/client')
api.add_namespace(api_bet, path='/bet')
