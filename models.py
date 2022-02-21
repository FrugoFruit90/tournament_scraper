import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy

from password import PASSWORD

db = SQLAlchemy()


def get_database_uri(username, password, port, db_name):
    return f"postgresql://{username}:{password}@{port}/{db_name}"


def setup_db(app):
    """
    setup_db(app):
        binds a flask application and a SQLAlchemy service
    """
    database_name = 'tournaments'
    default_database_path = get_database_uri('jim_potato', PASSWORD, 'localhost:5432', database_name)
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
    first_name = Column(String(80))
    last_name = Column(String(80))
    title = Column(String(80))
    rating = Column(Integer())
    date_of_birth = Column(db.Date)

    def __init__(self, first_name, last_name, title, rating, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.rating = rating
        self.date_of_birth = date_of_birth

    def details(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title,
            'rating': self.rating,
            'date_of_birth': self.date_of_birth,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
