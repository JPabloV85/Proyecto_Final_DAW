###
# database configuration
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
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

