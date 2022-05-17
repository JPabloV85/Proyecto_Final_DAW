# from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from model import db, User, Role, Client, Stud, Horse, Run, Runs_Horses, Bets


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        ordered = True

    roles = fields.Nested(lambda: RoleSchema(exclude=["users"]), many=True)
    client = fields.Nested(lambda: ClientSchema(exclude=["user"]), load_only=True)


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True
        sqla_session = db.session
        ordered = True

    users = fields.Nested(UserSchema(exclude=["roles"]), many=True)


class StudSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Stud
        load_instance = True
        sqla_session = db.session
        ordered = True

    horses = fields.Nested(lambda: HorseSchema(exclude=["stud"]), many=True)


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
