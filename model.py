from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
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
        db.create_all(app=app)
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
            Stud(name="yeguada1", location="Cadiz", email="sfsofi@svsd.com"),
            Stud(name="yeguada2", location="Barcelona", email="ntytygfi@svsd.com"),
            Stud(name="yeguada3", location="Madrid", email="wtgwergf@svsd.com")
        ]
        horses = [
            Horse(equineID="03IT824", name="caballo1", breed="Appaloosa", age=8, stud=studs[0]),
            Horse(equineID="52ES456", name="caballo2", breed="American Quarter Horse", age=7, stud=studs[1]),
            Horse(equineID="42US957", name="caballo3", breed="Thoroughbred", age=10, stud=studs[2])
        ]
        runs = [
            Run(tag="20JAN-01", date="20/01/2022", time="13.00"),
            Run(tag="27MAY-12", date="27/05/2022", time="17.00", horses=[horses[1], horses[2]]),
            Run(tag="27MAY-11", date="27/05/2022", time="10.00", horses=[horses[0], horses[1]]),
            Run(tag="28MAY-06", date="28/05/2022", time="14.00", horses=[horses[0]]),
            Run(tag="28MAY-09", date="28/05/2022", time="18.00", horses=[horses[0], horses[2]])
        ]
        clients = [
            Client(cif="58744698C", cash=500, user=users[0]),
            Client(cif="33799746I", cash=400, user=users[1]),
            Client(cif="77418462L", cash=300, user=users[2])
        ]
        bets = [
            Bet(client_id=1, run_horse_id=1, payment_amount=30.7, bet_position=2, bet_amount=10.5, win=True),
            Bet(client_id=1, run_horse_id=2, bet_position=1, bet_amount=20),
            Bet(client_id=1, run_horse_id=4, payment_amount=50, bet_position=2, bet_amount=30.5, win=False),
            Bet(client_id=1, run_horse_id=5, payment_amount=10.5, bet_position=1, bet_amount=5, win=True)
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
        for bet in bets:
            db.session.add(bet)

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
    is_active = db.Column(db.Boolean, default=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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
    name = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship('User', secondary=roles_users, back_populates='roles', uselist=True)

    def __repr__(self):
        return f"<Role {self.name}>"


class Stud(db.Model):
    """
    Stud entity

    Store stud data
    """
    __tablename__ = 'stud'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    location = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)

    horses = db.relationship("Horse", cascade="all, delete-orphan", backref="stud", uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Stud: {self.name}>"


class Horse(db.Model):
    """
    Horse entity

    Store horse data
    """
    __tablename__ = 'horse'
    id = db.Column(db.Integer, primary_key=True)
    equineID = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    win_ratio = db.Column(db.Float, default=0)
    image = db.Column(db.String(255), default="default_horse.jpg")

    stud_id = db.Column(db.Integer, db.ForeignKey('stud.id', ondelete='SET NULL'), nullable=True)
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
    tag = db.Column(db.String(80), unique=True, nullable=False)
    date = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)

    horses = db.relationship('Horse', secondary="runs_horses", back_populates="runs")

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Run: {self.tag}>"


class Runs_Horses(db.Model):
    """
    Runs_Horses entity

    Store run_horse data
    """
    __tablename__ = 'runs_horses'
    id = db.Column(db.Integer, primary_key=True)
    final_position = db.Column(db.Integer)

    run_id = db.Column(db.Integer, db.ForeignKey('run.id'), nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horse.id'), nullable=False)
    UniqueConstraint(run_id, horse_id, name='run_horse')
    UniqueConstraint(run_id, final_position, name='run_position')

    clients = db.relationship('Client', secondary='bet', back_populates='runs_horses', uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class Client(db.Model):
    """
    Client entity

    Store client data
    """
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    cif = db.Column(db.String(80), nullable=False, unique=True)
    cifImage = db.Column(db.String(255), nullable=False, default="default_user.jpg")
    cash = db.Column(db.Float, default=0)
    image = db.Column(db.String(255), default="default_user.jpg")

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    runs_horses = db.relationship('Runs_Horses', secondary='bet', back_populates='clients', uselist=True)
    bets = db.relationship("Bet", backref="client", viewonly=True, uselist=True)

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Client: {self.id}>"


class Bet(db.Model):
    """
    Bet entity

    Store bet data
    """
    __tablename__ = 'bet'
    id = db.Column(db.Integer, primary_key=True)
    bet_position = db.Column(db.Integer, nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    win = db.Column(db.Boolean)
    benefit_ratio = db.Column(db.Float, default=0)
    payment_amount = db.Column(db.Float, default=0)
    claimed = db.Column(db.Boolean, default=False)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    run_horse_id = db.Column(db.Integer, db.ForeignKey('runs_horses.id'), nullable=False)
    UniqueConstraint(client_id, run_horse_id, name='client_run-horse')

    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())
