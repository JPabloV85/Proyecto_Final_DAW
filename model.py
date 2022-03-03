from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import database_exists

db = SQLAlchemy()


def init_db(app, guard, testing=False):
    """
    Initializes database

    :param app: flask app
    :param guard: praetorian object for password hashing if seeding needed
    """
    db.init_app(app)
    if testing or not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        # if there is no database file
        # migrate model
        db.create_all(app=app)
        # seed data
        seed_db(app, guard)


def seed_db(app, guard):
    """
    Seeds database with test data

    :param app: flask app
    :param guard: praetorian object for password hashing
    """
    with app.app_context():
        roles = [
            Role(name="admin"),
            Role(name="client")
        ]
        users = [
            User(username="juan", email="juan@a.a",
                 hashed_password=guard.hash_password("pestillo"),
                 roles=[roles[1]]),
            User(username="paco", email="paco@a.a",
                 hashed_password=guard.hash_password("pestillo"),
                 roles=[roles[1]]),
            User(username="maria", email="maria@a.a",
                 hashed_password=guard.hash_password("pestillo"),
                 roles=[roles[1]]),
            User(username="pedro", email="pedro@a.a",
                 hashed_password=guard.hash_password("pestillo"),
                 roles=[roles[0]])
        ]
        studs = [
            Stud(name="yeguada1", address="direccion1", location="Cadiz",
                 owner="Antonio Perez", tlf="956020304", email="sfsofi@svsd.com"),
            Stud(name="yeguada2", address="direccion2", location="Sevilla",
                 owner="Juana Lopez", tlf="984532745", email="sfsohtygfi@svsd.com"),
            Stud(name="yeguada3", address="direccion3", location="Madrid",
                 owner="Lucia Gomez", tlf="687459821", email="wtgwergf@svsd.com")
        ]
        horses = [
            Horse(name="caballo1", race="Appaloosa", hair_cape="appaloosa",
                  win_ratio=30.4, stud=studs[0]),
            Horse(name="caballo2", race="Pura Sangre Inglés", hair_cape="negra",
                  win_ratio=50.4, stud=studs[1]),
            Horse(name="caballo3", race="Pura Sangre Inglés", hair_cape="castaño",
                  win_ratio=27.4, stud=studs[2])
        ]
        runs = [
            Run(date="25/05/2022", time="13.00"),
            Run(date="27/05/2022", time="17.00", horses=[horses[1], horses[2]]),
            Run(date="28/05/2022", time="14.00", horses=[horses[0]])
        ]
        clients = [
            Client(cif="58744698C", full_name="Juan Vázquez", user=users[0]),
            Client(cif="33799746I", full_name="Paco Perez", user=users[1]),
            Client(cif="77418462L", full_name="Maria García", user=users[2])
        ]

        for user in users:
            db.session.add(user)
        for stud in studs:
            db.session.add(stud)
        for horse in horses:
            db.session.add(horse)
        for run in runs:
            db.session.add(run)
        for client in clients:
            db.session.add(client)

        db.session.commit()


# tables for N:M relationship
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
                       )
"""
bets = db.Table('bets',
                db.Column('id', db.Integer, primary_key=True),
                db.Column('run_horse_id', db.Integer, db.ForeignKey('runs_horses.id')),
                db.Column('client_id', db.Integer, db.ForeignKey('client.id')),
                db.Column('bet_position', db.Integer, nullable=False, default=0),
                db.Column('bet_amount', db.Float, nullable=False, default=0),
                db.Column('win', db.Boolean),
                db.Column('benefit_ratio', db.Float),
                db.Column('payment_amount', db.Float)
                )
"""


# classes for model entities
class User(db.Model):
    """
    User entity

    Store user data
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.Text)

    client = db.relationship("Client", cascade="all, delete-orphan", backref="user")
    roles = db.relationship('Role', secondary=roles_users, back_populates='users', uselist=True)
    is_active = db.Column(db.Boolean, default=True, server_default="true")

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # this enables this entity as user entity in praetorian
    @property
    def identity(self):
        return self.id

    @property
    def rolenames(self):
        return [role.name for role in self.roles]

    @property
    def password(self):
        return self.hashed_password

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id_user):
        return cls.query.get(id_user)

    def is_valid(self):
        return self.is_active

    def __repr__(self):
        return f"<User {self.username}>"


class Role(db.Model):
    """
    Role entity

    Store roles data
    """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    users = db.relationship('User', secondary=roles_users, back_populates='roles', uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Role {self.name}>"


class Stud(db.Model):
    """
    Stud entity

    Store stud data
    """
    __tablename__ = 'stud'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80))
    location = db.Column(db.String(80))
    owner = db.Column(db.String(80), nullable=False)
    tlf = db.Column(db.String(80))
    email = db.Column(db.String(80))

    horses = db.relationship("Horse", cascade="all, delete-orphan", backref="stud", uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Stud: {self.name}>"


class Horse(db.Model):
    """
    Horse entity

    Store horse data
    """
    __tablename__ = 'horse'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    race = db.Column(db.String(80), nullable=False)
    hair_cape = db.Column(db.String(80))
    win_ratio = db.Column(db.Float)
    image = db.Column(db.String(255), default="not-found.png")

    stud_id = db.Column(db.Integer, db.ForeignKey('stud.id'))
    runs = db.relationship('Run', secondary="runs_horses", back_populates="horses")

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Horse: {self.name}>"


class Run(db.Model):
    """
    Run entity

    Store run data
    """
    __tablename__ = 'run'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)

    horses = db.relationship('Horse', secondary="runs_horses", back_populates="runs")

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Run: {self.name}>"


class Runs_Horses(db.Model):
    """
    Runs_Horses entity

    Store run_horse data
    """
    __tablename__ = 'runs_horses'
    id = db.Column(db.Integer, primary_key=True)
    final_position = db.Column(db.Integer, default=0)
    minimum_bet = db.Column(db.Float, default=0)
    total_bet = db.Column(db.Float, default=0)

    run_id = db.Column(db.Integer, db.ForeignKey('run.id'), nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horse.id'), nullable=False)
    UniqueConstraint(run_id, horse_id, name='run_horse')

    clients = db.relationship('Client', secondary='bets', back_populates='runs_horses', uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class Client(db.Model):
    """
    Client entity

    Store client data
    """
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    cif = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    cash = db.Column(db.Float, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    runs_horses = db.relationship('Runs_Horses', secondary='bets', back_populates='clients', uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Client: {self.full_name}>"


class Bets(db.Model):
    """
    Bets entity

    Store bet data
    """
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    bet_position = db.Column(db.Integer, nullable=False, default=0)
    bet_amount = db.Column(db.Float, nullable=False, default=0)
    win = db.Column(db.Boolean, default=False)
    benefit_ratio = db.Column(db.Float, default=0)
    payment_amount = db.Column(db.Float, default=0)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    run_horse_id = db.Column(db.Integer, db.ForeignKey('runs_horses.id'), nullable=False)
    UniqueConstraint(client_id, run_horse_id, name='client_run-horse')

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

