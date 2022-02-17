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

output_data = []


# By Deafult Flask will come into this when we run the file
@app.route('/')
def index():
    df = pd.read_csv("chess_calendar/full_data.csv")
    df = df[df['type'] == 'klasyczne']
    return df.dropna().sort_values("avg_rating").iloc[-5:]['url'].to_dict()


if __name__ == "__main__":
    if not os.path.exists(FULL_DATA_PATH):
        configure_logging()
        crawl_runner = CrawlerRunner()
        crawl(crawl_runner)
        reactor.run()
    app.run(debug=True)
