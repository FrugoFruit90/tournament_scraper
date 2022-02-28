from datetime import date, datetime
import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from config import config
from chess_calendar.chess_calendar.constants import FULL_DATA_PATH, TOURNAMENT_DATA_PATH
from chess_calendar.chess_calendar.crawler_main import crawl
from models import setup_db, Tournament, Player, db_drop_and_create_all

root = logging.getLogger()
root.setLevel(logging.INFO)


def create_app(app_environment=None):
    app = Flask(__name__)
    if app_environment is None:
        app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
    else:
        app.config.from_object(config[app_environment])
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
            Tournament(
                title=tournament["name"],
                url=tournament["url"],
                time_control=tournament["type"],
                status=tournament["status"],
                start_date=date(datetime.now().year, month, day),
                end_date=date(datetime.now().year, month, day)
            ).insert()

        players = pd.read_csv(FULL_DATA_PATH)
        for i, player in players.iterrows():
            Player(
                tournament_id=player['id'],
                name=player['name'],
                title=player['title'],
                rating=player['rating'],
                year_of_birth=player['year_of_birth']
            ).insert()

    @app.route('/')
    def index():
        player_data = pd.read_sql_table(table_name='player', con=db.engine)
        agg_data = player_data.groupby('tournament_id')['rating'].agg(['mean', 'count'])
        tournament_metadata = pd.read_sql_table(table_name='tournament', con=db.engine)
        agg_data = agg_data.merge(tournament_metadata, left_index=True, right_index=True)
        planned_classical = agg_data[(agg_data['time_control'] == 'klasyczne') & (agg_data['status'] == 'planowany')]
        best_with_k_people = planned_classical[planned_classical['count'] >= 10].sort_values('mean', ascending=False)
        return best_with_k_people.iloc[:10]['url'].to_dict()

    return app


if __name__ == "__main__":
    app = create_app(os.getenv('FLASK_ENV', 'dev'))
    app.run()
