from datetime import date, datetime
import logging
import os

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from chess_calendar.chess_calendar.constants import FULL_DATA_PATH, TOURNAMENT_DATA_PATH
from chess_calendar.chess_calendar.crawler_main import crawl
from models import setup_db, Tournament, Player, db_initialize_db, db_drop_and_create_all

root = logging.getLogger()
root.setLevel(logging.INFO)

app = Flask(__name__)

setup_db(app)
CORS(app)
db_drop_and_create_all()
db = SQLAlchemy(app)


@app.before_first_request
def before_first_request():
    if not os.path.exists(FULL_DATA_PATH):
        logging.info("Crawling for tournaments.")
        configure_logging()
        crawl_runner = CrawlerRunner()
        crawl(crawl_runner)
        reactor.run()

    tournaments = pd.read_csv(TOURNAMENT_DATA_PATH)
    for i, tournament in tournaments.iterrows():
        day, month = tournament.start.split('-')
        day, month = int(day), int(month)
        db.session.add(Tournament(
            title=tournament.name,
            url=tournament.url,
            description='',
            status=tournament.status,
            start_date=date(datetime.now().year, month, day),
            end_date=date(datetime.now().year, month, day)
        ))
    db.session.commit()

    @app.route('/')
    def index():
        df = pd.read_csv("full_data.csv")
        df = df[df['type'] == 'klasyczne']

        return df.dropna().sort_values("avg_rating").iloc[-5:]['url'].to_dict()

    if __name__ == "__main__":
        app.run()
