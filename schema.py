from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from model import db, User, Role, Client, Stud, Horse, Run, Runs_Horses, Bets


class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Nested(lambda: RoleSchema(only=["name"], exclude=["users"]), many=True)
    client = fields.Nested(lambda: ClientSchema(exclude=["user"]), load_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "hashed_password", "created_on", "roles", "client"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class RoleSchema(SQLAlchemyAutoSchema):
    users = fields.Nested(UserSchema(exclude=["roles"]), many=True, load_only=True)

    class Meta:
        model = Role
        load_instance = True
        sqla_session = db.session
        ordered = True


class StudSchema(SQLAlchemyAutoSchema):
    horses = fields.Nested(lambda: HorseSchema(exclude=["stud"]), many=True, load_only=True)

    class Meta:
        model = Stud
        load_instance = True
        sqla_session = db.session
        ordered = True


class HorseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Horse
        load_instance = True
        sqla_session = db.session
        ordered = True

    stud = fields.Nested(StudSchema(exclude=["horses"]))
    runs = fields.Nested(lambda: RunSchema(exclude=["horses"]), many=True)


class RunSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Run
        load_instance = True
        sqla_session = db.session
        ordered = True

    horses = fields.Nested(HorseSchema, exclude=["runs"], many=True)


class Runs_HorsesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Runs_Horses
        load_instance = True
        sqla_session = db.session
        ordered = True

    clients = fields.Nested(lambda: ClientSchema(exclude=["user", "runs_horses"]), many=True)


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        load_instance = True
        sqla_session = db.session
        ordered = True

    user = fields.Nested(UserSchema(exclude=["client"]))
    runs_horses = fields.Nested(Runs_HorsesSchema, exclude=["clients"], many=True)


class BetsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Bets
        load_instance = True
        sqla_session = db.session
        ordered = True

    client = fields.Nested(ClientSchema(exclude=["user", "runs_horses"]), load_only=True)
    run_horse = fields.Nested(Runs_HorsesSchema, exclude=["clients"], load_only=True)
