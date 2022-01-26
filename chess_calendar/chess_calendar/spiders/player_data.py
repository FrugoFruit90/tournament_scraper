from ast import literal_eval
import re

import numpy as np
import pandas as pd
import scrapy

try:
    from constants import TOURNAMENT_DATA_PATH, FULL_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, \
        URL_FIELD, CHESSARBITER_DATA_JS_FILENAME
except ModuleNotFoundError as s:
    from ..constants import TOURNAMENT_DATA_PATH, FULL_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, \
        URL_FIELD, CHESSARBITER_DATA_JS_FILENAME


def parse_rating(x):
    return int(x.lstrip("R ").lstrip("B "))


class TournamentSpider(scrapy.Spider):
    def __init__(self, update=False, **kwargs):
        super().__init__(**kwargs)
        self.data = None
        self.update = update

    name = "player_data"

    def start_requests(self):
        if not self.update:
            self.data = pd.read_csv(TOURNAMENT_DATA_PATH)
        else:
            self.data = pd.read_csv(FULL_DATA_PATH)
        urls = self.data[URL_FIELD].to_list()
        self.data['avg_rating'] = np.NaN
        self.data['median_rating'] = np.NaN
        self.data['median_rating'] = np.NaN
        self.data['no_players'] = np.NaN
        for i, url in enumerate(urls):
            url_elements = url.split("/")
            if len(url_elements) < 6:
                continue
            else:
                tourney_id = url_elements[-1].rstrip("&n=")
                year = url_elements[-2].lstrip("open.php?turn=")
                new_url = f"http://chessarbiter.com/turnieje/{year}/{tourney_id}/capro_tournament.js"
                yield scrapy.Request(new_url, callback=self.parse, meta={'index': i})

    def parse(self, response, **kwargs):
        rating_str = re.findall("var A14 = .*?;\r\n", response.body.decode("utf-8"), re.S)[0]
        ratings = list(map(parse_rating, literal_eval(rating_str.lstrip('var A14 = ').rstrip(";\r\n"))))
        self.data.loc[response.meta['index'], 'avg_rating'] = np.mean(ratings)
        self.data.loc[response.meta['index'], 'median_rating'] = np.median(ratings)
        self.data.loc[response.meta['index'], 'no_players'] = len(ratings)

    def closed(self, _):
        self.data.to_csv(FULL_DATA_PATH, index=False)
        self.log(f'Saved file {TOURNAMENT_DATA_PATH}')
