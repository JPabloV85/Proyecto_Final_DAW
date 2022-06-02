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
    with app.app_context():
        roles = [
            Role(name="admin"),
            Role(name="client")
        ]
        users = [
            User(username="pablo", email="pablo@a.a",
                 hashed_password=guard.hash_password("alberti"),
                 roles=[roles[1]]),
            User(username="maria", email="maria@a.a",
                 hashed_password=guard.hash_password("alberti"),
                 roles=[roles[1]]),
            User(username="pedro", email="pedro@a.a",
                 hashed_password=guard.hash_password("alberti"),
                 roles=[roles[0]])
        ]
        clients = [
            Client(cif="58744698C", cash=460, image="mifoto.jpg", user=users[0]),
            Client(cif="33799746I", cash=500, user=users[1])
        ]
        studs = [
            Stud(name="El Chaparral", location="Cádiz", email="sfsofi@svsd.com"),
            Stud(name="Torreluna", location="Sevilla", email="ntytygfi@svsd.com"),
            Stud(name="Hnos. Díaz", location="Madrid", email="wtgwergf@svsd.com")
        ]
        horses = [
            Horse(equineID="A12345", name="Rocinante", breed="Appaloosa", age=8, image='caballo1.jpg', win_ratio=100,
                  stud=studs[0]),
            Horse(equineID="A54321", name="Trueno", breed="American Quarter Horse", age=7, image='caballo2.jpg',
                  win_ratio=57, stud=studs[1]),
            Horse(equineID="B12345", name="Flash", breed="Thoroughbred", age=10, image='caballo3.jpg', win_ratio=16,
                  stud=studs[2]),
            Horse(equineID="B54321", name="Babieca", breed="Appaloosa", age=8, image='caballo4.jpg', win_ratio=22,
                  stud=studs[0]),
            Horse(equineID="C12345", name="Duque", breed="American Quarter Horse", age=7, image='caballo5.jpg', win_ratio=0,
                  stud=studs[1]),
            Horse(equineID="C54321", name="Gamora", breed="Thoroughbred", age=10, image='caballo6.jpg', win_ratio=22,
                  stud=studs[2]),
            Horse(equineID="D12345", name="Marquesa", breed="Appaloosa", age=8, image='caballo7.jpg', win_ratio=0,
                  stud=studs[0]),
            Horse(equineID="D54321", name="Furia", breed="American Quarter Horse", age=7, image='caballo8.jpg', win_ratio=0,
                  stud=studs[1]),
            Horse(equineID="E12345", name="Pegasus", breed="Thoroughbred", age=10, image='caballo9.jpg', win_ratio=0,
                  stud=studs[2]),
            Horse(equineID="E54321", name="Bucéfalo", breed="Appaloosa", age=8, image='caballo10.jpg', win_ratio=0,
                  stud=studs[0])
        ]
        runs = [
            Run(tag="08JUN-01", date="08/06/2022", time="16:00"),
            Run(tag="08JUN-02", date="08/06/2022", time="17:00"),
            Run(tag="08JUN-03", date="08/06/2022", time="18:00"),
            Run(tag="08JUN-04", date="08/06/2022", time="19:00"),
            Run(tag="08JUN-05", date="08/06/2022", time="20:00"),
            Run(tag="09JUN-01", date="09/06/2022", time="16:00"),
            Run(tag="09JUN-02", date="09/06/2022", time="17:00"),
            Run(tag="09JUN-03", date="09/06/2022", time="18:00"),
            Run(tag="09JUN-04", date="09/06/2022", time="19:00"),
            Run(tag="09JUN-05", date="09/06/2022", time="20:00"),
            Run(tag="10JUN-01", date="10/06/2022", time="16:00"),
            Run(tag="10JUN-02", date="10/06/2022", time="17:00"),
            Run(tag="10JUN-03", date="10/06/2022", time="18:00"),
            Run(tag="10JUN-04", date="10/06/2022", time="19:00"),
            Run(tag="10JUN-05", date="10/06/2022", time="20:00"),
            Run(tag="20JUN-01", date="20/06/2022", time="16:00",
                horses=[horses[2], horses[5], horses[7], horses[3], horses[9]]),
            Run(tag="20JUN-02", date="20/06/2022", time="17:00",
                horses=[horses[1], horses[3], horses[5], horses[7], horses[9]]),
            Run(tag="20JUN-03", date="20/06/2022", time="18:00",
                horses=[horses[0], horses[2], horses[4], horses[6], horses[8]]),
            Run(tag="20JUN-04", date="20/06/2022", time="19:00",
                horses=[horses[1], horses[2], horses[5], horses[8], horses[9]]),
            Run(tag="20JUN-05", date="20/06/2022", time="20:00",
                horses=[horses[0], horses[3], horses[4], horses[6], horses[7]]),
            Run(tag="21JUN-01", date="21/06/2022", time="16:00",
                horses=[horses[0], horses[1], horses[4], horses[7], horses[8]]),
            Run(tag="21JUN-02", date="21/06/2022", time="17:00",
                horses=[horses[2], horses[3], horses[5], horses[6], horses[9]]),
            Run(tag="21JUN-03", date="21/06/2022", time="18:00",
                horses=[horses[0], horses[1], horses[3], horses[4], horses[7]]),
            Run(tag="21JUN-04", date="21/06/2022", time="19:00",
                horses=[horses[2], horses[5], horses[6], horses[8], horses[9]]),
            Run(tag="21JUN-05", date="21/06/2022", time="20:00",
                horses=[horses[0], horses[1], horses[2], horses[8], horses[9]])
        ]

        for user in users: db.session.add(user)
        for client in clients: db.session.add(client)
        for stud in studs: db.session.add(stud)
        for horse in horses: db.session.add(horse)
        for run in runs: db.session.add(run)
        db.session.commit()

        runs_horses = [
            Runs_Horses(run_id=runs[0].id, horse_id=horses[3].id, final_position=1),
            Runs_Horses(run_id=runs[0].id, horse_id=horses[4].id, final_position=2),
            Runs_Horses(run_id=runs[0].id, horse_id=horses[5].id, final_position=3),
            Runs_Horses(run_id=runs[0].id, horse_id=horses[6].id, final_position=4),
            Runs_Horses(run_id=runs[0].id, horse_id=horses[7].id, final_position=5),
            Runs_Horses(run_id=runs[1].id, horse_id=horses[1].id, final_position=1),
            Runs_Horses(run_id=runs[1].id, horse_id=horses[2].id, final_position=2),
            Runs_Horses(run_id=runs[1].id, horse_id=horses[3].id, final_position=3),
            Runs_Horses(run_id=runs[1].id, horse_id=horses[6].id, final_position=4),
            Runs_Horses(run_id=runs[1].id, horse_id=horses[8].id, final_position=5),
            Runs_Horses(run_id=runs[2].id, horse_id=horses[1].id, final_position=1),
            Runs_Horses(run_id=runs[2].id, horse_id=horses[3].id, final_position=2),
            Runs_Horses(run_id=runs[2].id, horse_id=horses[4].id, final_position=3),
            Runs_Horses(run_id=runs[2].id, horse_id=horses[6].id, final_position=4),
            Runs_Horses(run_id=runs[2].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[3].id, horse_id=horses[5].id, final_position=1),
            Runs_Horses(run_id=runs[3].id, horse_id=horses[6].id, final_position=2),
            Runs_Horses(run_id=runs[3].id, horse_id=horses[7].id, final_position=3),
            Runs_Horses(run_id=runs[3].id, horse_id=horses[8].id, final_position=4),
            Runs_Horses(run_id=runs[3].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[4].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[4].id, horse_id=horses[1].id, final_position=2),
            Runs_Horses(run_id=runs[4].id, horse_id=horses[2].id, final_position=3),
            Runs_Horses(run_id=runs[4].id, horse_id=horses[3].id, final_position=4),
            Runs_Horses(run_id=runs[4].id, horse_id=horses[4].id, final_position=5),
            Runs_Horses(run_id=runs[5].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[5].id, horse_id=horses[1].id, final_position=2),
            Runs_Horses(run_id=runs[5].id, horse_id=horses[2].id, final_position=3),
            Runs_Horses(run_id=runs[5].id, horse_id=horses[3].id, final_position=4),
            Runs_Horses(run_id=runs[5].id, horse_id=horses[4].id, final_position=5),
            Runs_Horses(run_id=runs[6].id, horse_id=horses[5].id, final_position=1),
            Runs_Horses(run_id=runs[6].id, horse_id=horses[6].id, final_position=2),
            Runs_Horses(run_id=runs[6].id, horse_id=horses[7].id, final_position=3),
            Runs_Horses(run_id=runs[6].id, horse_id=horses[8].id, final_position=4),
            Runs_Horses(run_id=runs[6].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[7].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[7].id, horse_id=horses[2].id, final_position=2),
            Runs_Horses(run_id=runs[7].id, horse_id=horses[4].id, final_position=3),
            Runs_Horses(run_id=runs[7].id, horse_id=horses[5].id, final_position=4),
            Runs_Horses(run_id=runs[7].id, horse_id=horses[7].id, final_position=5),
            Runs_Horses(run_id=runs[8].id, horse_id=horses[1].id, final_position=1),
            Runs_Horses(run_id=runs[8].id, horse_id=horses[3].id, final_position=2),
            Runs_Horses(run_id=runs[8].id, horse_id=horses[6].id, final_position=3),
            Runs_Horses(run_id=runs[8].id, horse_id=horses[8].id, final_position=4),
            Runs_Horses(run_id=runs[8].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[9].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[9].id, horse_id=horses[1].id, final_position=2),
            Runs_Horses(run_id=runs[9].id, horse_id=horses[5].id, final_position=3),
            Runs_Horses(run_id=runs[9].id, horse_id=horses[6].id, final_position=4),
            Runs_Horses(run_id=runs[9].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[10].id, horse_id=horses[2].id, final_position=1),
            Runs_Horses(run_id=runs[10].id, horse_id=horses[3].id, final_position=2),
            Runs_Horses(run_id=runs[10].id, horse_id=horses[4].id, final_position=3),
            Runs_Horses(run_id=runs[10].id, horse_id=horses[7].id, final_position=4),
            Runs_Horses(run_id=runs[10].id, horse_id=horses[8].id, final_position=5),
            Runs_Horses(run_id=runs[11].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[11].id, horse_id=horses[4].id, final_position=2),
            Runs_Horses(run_id=runs[11].id, horse_id=horses[5].id, final_position=3),
            Runs_Horses(run_id=runs[11].id, horse_id=horses[7].id, final_position=4),
            Runs_Horses(run_id=runs[11].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[12].id, horse_id=horses[3].id, final_position=1),
            Runs_Horses(run_id=runs[12].id, horse_id=horses[4].id, final_position=2),
            Runs_Horses(run_id=runs[12].id, horse_id=horses[7].id, final_position=3),
            Runs_Horses(run_id=runs[12].id, horse_id=horses[8].id, final_position=4),
            Runs_Horses(run_id=runs[12].id, horse_id=horses[9].id, final_position=5),
            Runs_Horses(run_id=runs[13].id, horse_id=horses[1].id, final_position=1),
            Runs_Horses(run_id=runs[13].id, horse_id=horses[3].id, final_position=2),
            Runs_Horses(run_id=runs[13].id, horse_id=horses[6].id, final_position=3),
            Runs_Horses(run_id=runs[13].id, horse_id=horses[7].id, final_position=4),
            Runs_Horses(run_id=runs[13].id, horse_id=horses[8].id, final_position=5),
            Runs_Horses(run_id=runs[14].id, horse_id=horses[0].id, final_position=1),
            Runs_Horses(run_id=runs[14].id, horse_id=horses[2].id, final_position=2),
            Runs_Horses(run_id=runs[14].id, horse_id=horses[4].id, final_position=3),
            Runs_Horses(run_id=runs[14].id, horse_id=horses[5].id, final_position=4),
            Runs_Horses(run_id=runs[14].id, horse_id=horses[9].id, final_position=5)
        ]
        for run_horse in runs_horses: db.session.add(run_horse)
        db.session.commit()

        bets = [
            Bet(client_id=1, run_horse_id=runs_horses[1].id, payment_amount=30.7, bet_position=2, bet_amount=10, win=True),
            Bet(client_id=1, run_horse_id=runs_horses[5].id, payment_amount=50.2, bet_position=1, bet_amount=20, win=True),
            Bet(client_id=1, run_horse_id=runs_horses[7].id, payment_amount=15.3, bet_position=3, bet_amount=5, win=False),
            Bet(client_id=1, run_horse_id=runs_horses[50].id, payment_amount=500, bet_position=1, bet_amount=5, win=False)
        ]
        for bet in bets: db.session.add(bet)
        db.session.commit()


# table for N:M relationship
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
                       )


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
