from datetime import date, datetime
import logging
import os

from flask import Flask, render_template_string
from flask_cors import CORS
import pandas as pd
from sqlalchemy.orm import Session
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from sqlalchemy import update
from twisted.internet import reactor

from config import config
from chess_calendar.chess_calendar.constants import FULL_DATA_PATH, TOURNAMENT_DATA_PATH
from chess_calendar.chess_calendar.crawler_main import crawl
from models import setup_db, Tournament, Player, db

root = logging.getLogger()
logging.basicConfig(level=logging.INFO)
root.setLevel(logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

pd.set_option('chained_assignment', None)


def create_app(app_environment=None):
    app = Flask(__name__)
    if app_environment is None:
        app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
    else:
        app.config.from_object(config[app_environment])
    setup_db(app)
    CORS(app)

    @app.before_first_request
    def before_first_request():
        if not os.path.exists(FULL_DATA_PATH):
            logging.info("Crawling for tournaments.")
            configure_logging()
            crawl_runner = CrawlerRunner()
            crawl(crawl_runner)
            reactor.run()
        db.app.logger.info(f"rows in tournament: {db.session.query(Tournament).count()}")
        with Session(db.engine) as session, session.begin():
            if session.query(Tournament).first() is None:
                tournaments = pd.read_csv(TOURNAMENT_DATA_PATH).drop_duplicates(subset=['url'])
                players = pd.read_csv(FULL_DATA_PATH)
                for i, tournament_row in tournaments.iterrows():
                    day, month = tournament_row.start.split('-')
                    day, month = int(day), int(month)
                    tournament = Tournament(
                        title=tournament_row["name"],
                        url=tournament_row["url"],
                        time_control=tournament_row["type"],
                        status=tournament_row["status"],
                        start_date=date(datetime.now().year, month, day),
                        end_date=date(datetime.now().year, month, day)
                    )
                    session.add(tournament)
                    session.flush()

                    for j, player in players[players['id'] == i].iterrows():
                        player = (Player(
                            tournament_id=tournament.id,
                            name=player['name'],
                            title=player['title'],
                            rating=player['rating'],
                            year_of_birth=player['year_of_birth']
                        ))
                        session.add(player)

    @app.route('/')
    def index():
        player_data = pd.read_sql_table(table_name='player', con=db.engine)
        agg_data = player_data.groupby('tournament_id')['rating'].agg(['mean', 'count'])
        tournament_metadata = pd.read_sql_table(table_name='tournament', con=db.engine)
        agg_data = agg_data.merge(tournament_metadata, left_index=True, right_on='id')
        planned_classical = agg_data[(agg_data['time_control'] == 'klasyczne') & (agg_data['status'] == 'planowany')]
        best_with_k_people = planned_classical[planned_classical['count'] >= 10].sort_values('mean', ascending=False)
        best_with_k_people = best_with_k_people.round({'mean': 1}).drop(['time_control', 'end_date', 'id'], axis=1)
        best_with_k_people = best_with_k_people.rename({"count": '#players', 'mean': 'mean rating'}, axis=1)
        df = best_with_k_people.iloc[:10]
        df["url"] = '<a href=' + df['url'] + '><div>' + df['title'] + '</div></a>'
        df = df.drop(['title'], axis=1)
        return render_template_string(df.to_html(render_links=True, escape=False, index=False))

    return app


if __name__ == "__main__":
    app = create_app(os.getenv('FLASK_ENV', 'dev'))
    app.run()
