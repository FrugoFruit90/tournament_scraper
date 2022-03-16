import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, inspect
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropTable

db = SQLAlchemy()


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


def get_database_uri(username, password, port, db_name):
    return f"postgresql://{username}:{password}@{port}/{db_name}"


def setup_db(app):
    """
    setup_db(app):
        binds a flask application and a SQLAlchemy service
    """
    database_name = 'tournaments'
    default_database_path = get_database_uri('jim_potato', os.environ.get("PASSWORD"), 'localhost:5432', database_name)
    database_path = os.getenv('DATABASE_URL', default_database_path)
    database_path = database_path.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_initialize_db():
    db.create_all()


def db_drop_and_create_all():
    """
        drops the database tables and starts fresh
        can be used to initialize a clean database
    """
    inspector_gadget = inspect(db.engine)
    if inspector_gadget.has_table("player"):
        db.session.query(Player).delete()
        db.session.query(Tournament).delete()
    db.session.commit()
    db.create_all()


class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    url = Column(String(80), unique=True)
    time_control = Column(String(80))
    status = Column(String(80))
    start_date = Column(db.Date)
    end_date = Column(db.Date)

    def __init__(self, title, url, time_control, status, start_date, end_date):
        self.title = title
        self.url = url
        self.time_control = time_control
        self.status = status
        self.start_date = start_date
        self.end_date = end_date

    def details(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'time_control': self.time_control,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Player(db.Model):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    name = Column(String(80))
    title = Column(String(80))
    rating = Column(Integer())
    year_of_birth = Column(Integer())

    def __init__(self, tournament_id, name, title, rating, year_of_birth):
        self.id = self.id
        self.tournament_id = tournament_id
        self.name = name
        self.title = title
        self.rating = rating
        self.year_of_birth = year_of_birth

    def details(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'name': self.name,
            'title': self.title,
            'rating': self.rating,
            'year_of_birth': self.year_of_birth,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
