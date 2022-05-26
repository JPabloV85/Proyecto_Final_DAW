import marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from model import db, User, Role, Client, Stud, Horse, Run, Runs_Horses, Bet


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
        fields = ["id", "name", "location", "email", "created_on", "horses"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class HorseSchema(SQLAlchemyAutoSchema):
    stud = fields.Nested(StudSchema(only=["name", "location", "email"], exclude=["horses"]))
    runs = fields.Nested(lambda: RunSchema(exclude=["horses"]), load_only=True, many=True)
    total_runs = marshmallow.fields.Function(lambda obj: len(obj.runs))

    class Meta:
        model = Horse
        fields = ["id", "equineID", "name", "age", "breed", "runs", "total_runs", "image", "stud"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class RunSchema(SQLAlchemyAutoSchema):
    horses = fields.Nested(HorseSchema, only=["name", "equineID"], exclude=["runs", "stud"], many=True)

    class Meta:
        model = Run
        fields = ["id", "tag", "date", "time", "horses"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class Runs_HorsesSchema(SQLAlchemyAutoSchema):
    clients = fields.Nested(lambda: ClientSchema(exclude=["user", "runs_horses"]), load_only=True, many=True)

    class Meta:
        model = Runs_Horses
        fields = ["final_position", "clients"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class ClientSchema(SQLAlchemyAutoSchema):
    user = fields.Nested(UserSchema(only=['username', 'email', 'hashed_password'], exclude=["client"]))
    bets = fields.Nested(lambda: BetSchema(exclude=["client"]), many=True, load_only=True)
    runs_horses = fields.Nested(Runs_HorsesSchema, exclude=["clients"], many=True, load_only=True)
    number_of_bets = marshmallow.fields.Function(lambda obj: len(obj.runs_horses))

    class Meta:
        model = Client
        fields = ["id", "user", "cif", "cash", "image", "runs_horses", "number_of_bets", "bets"]
        load_instance = True
        sqla_session = db.session
        ordered = True


class BetSchema(SQLAlchemyAutoSchema):
    client = fields.Nested(ClientSchema(only=["user.username"], exclude=["runs_horses"]))
    run_horse = fields.Nested(Runs_HorsesSchema, exclude=["clients"], load_only=True)

    class Meta:
        model = Bet
        fields = ["id", "run_horse_id", "bet_position", "bet_amount", "win", "benefit_ratio", "payment_amount",
                  "claimed", "client"]
        load_instance = True
        sqla_session = db.session
        ordered = True
