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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tournament_df = None
        self.player_df = pd.DataFrame(columns=['id', 'name', 'title', 'rating', 'year_of_birth'])

    name = "player_data"

    def start_requests(self):
        self.tournament_df = pd.read_csv(TOURNAMENT_DATA_PATH)
        urls = self.tournament_df[URL_FIELD].to_list()

        for i, url in enumerate(urls):
            url_elements = url.split("/")
            if len(url_elements) < 6:
                continue
            else:
                tourney_id = url_elements[-1].rstrip("&n=")
                year = url_elements[-2].lstrip("open.php?turn=")
                new_url = f"http://chessarbiter.com/turnieje/{year}/{tourney_id}/capro_tournament.js"
                yield scrapy.Request(new_url, callback=self.parse, meta={'index': i, 'url': new_url})

    def parse(self, response, **kwargs):
        name_str = re.findall("var A11 = .*?;\r\n", response.body.decode("utf-8"), re.S)[0]
        title_str = re.findall("var A12 = .*?;\r\n", response.body.decode("utf-8"), re.S)[0]
        rating_str = re.findall("var A14 = .*?;\r\n", response.body.decode("utf-8"), re.S)[0]
        birth_str = re.findall("var A18 = .*?;\r\n", response.body.decode("utf-8"), re.S)[0]

        names = literal_eval(name_str.lstrip('var A11 = ').rstrip(";\r\n"))
        titles = literal_eval(title_str.lstrip('var A12 = ').rstrip(";\r\n"))
        ratings = list(map(parse_rating, literal_eval(rating_str.lstrip('var A14 = ').rstrip(";\r\n"))))
        birthdays = literal_eval(birth_str.lstrip('var A18 = ').rstrip(";\r\n"))

        df = pd.DataFrame({'rating': ratings, 'name': names, 'title': titles, 'year_of_birth': birthdays})
        df['id'] = response.meta['index']
        df['year_of_birth'] = df['year_of_birth'].astype(int)
        self.player_df = pd.concat([self.player_df, df])

    def closed(self, _):
        self.tournament_df.to_csv(TOURNAMENT_DATA_PATH, index=False)
        self.player_df.to_csv(FULL_DATA_PATH, index=False)
        self.log(f'Saved file {FULL_DATA_PATH}')
