""""
App configuration
"""
import os

###
# develop ApiKey
API_KEY = 'alberti'

###
# keep declaration order on jason dicts
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
