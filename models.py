import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
    db.drop_all()
    db.create_all()


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    players = db.relationship("Player", backref="tournament", lazy='dynamic')
    description = Column(String(80))
    status = Column(String(80))
    start_date = Column(db.Date)
    end_date = Column(db.Date)

    def __init__(self, title, url, description, status, start_date, end_date):
        self.title = title
        self.url = url
        self.description = description
        self.status = status
        self.start_date = start_date
        self.end_date = end_date

    def details(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
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
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    name = Column(String(80))
    title = Column(String(80))
    rating = Column(Integer())
    year_of_birth = Column(db.Date)

    def __init__(self, tournament, name, title, rating, year_of_birth):
        self.tournament = tournament
        self.name = name
        self.title = title
        self.rating = rating
        self.year_of_birth = year_of_birth

    def details(self):
        return {
            'id': self.id,
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
