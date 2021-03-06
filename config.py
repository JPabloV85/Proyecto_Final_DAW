""""
App configuration
"""
import os
from functools import wraps
from flask import request


###
# develop ApiKey
API_KEY = 'alberti'


###
# custom decorators
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


###
# keep declaration order on json dicts
JSON_SORT_KEYS = False

###
# database configuration
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.curdir)}/proyecto.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

###
# praetorian configuration
SECRET_KEY = "latch"
JWT_ACCESS_LIFESPAN = {"hours": 24}
JWT_REFRESH_LIFESPAN = {"days": 30}

###
# gitHub OAuth config
GITHUB_CLIENT_ID = "de3719ce10145f958512"
GITHUB_CLIENT_SECRET = "ebb4e8244e0fbb4a47f4c4e519d39bbeb8e3b3b0"
