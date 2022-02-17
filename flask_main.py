import logging
import os
import time

from flask import Flask
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from chess_calendar.chess_calendar.constants import FULL_DATA_PATH
from chess_calendar.chess_calendar.crawler_main import crawl

app = Flask(__name__)
root = logging.getLogger()
root.setLevel(logging.INFO)

output_data = []


@app.before_first_request
def before_first_request():
    if not os.path.exists(FULL_DATA_PATH):
        logging.info("Crawling for tournaments.")
        configure_logging()
        crawl_runner = CrawlerRunner()
        crawl(crawl_runner)
        reactor.run()


@app.route('/')
def index():
    df = pd.read_csv("full_data.csv")
    df = df[df['type'] == 'klasyczne']

    return df.dropna().sort_values("avg_rating").iloc[-5:]['url'].to_dict()


if __name__ == "__main__":
    app.run(debug=True)
