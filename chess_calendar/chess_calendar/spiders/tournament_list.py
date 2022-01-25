import pandas as pd
import scrapy

try:
    from constants import TOURNAMENT_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, GARBAGE_FIELD, URL_FIELD
except ModuleNotFoundError as s:
    from ..constants import TOURNAMENT_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, GARBAGE_FIELD, URL_FIELD


class ChessarbiterMainWebsiteSpider(scrapy.Spider):
    name = "tournament_list"
    start_urls = ["http://chessarbiter.com/"]

    def parse(self, response, **kwargs):
        tournament_dicts = []
        for table in response.xpath('//table')[14:]:
            for row in table.xpath('tr'):
                link = row.xpath('td//@href').extract()
                text_fields = row.xpath('td//text()').extract()
                tourney_data = {x: text_fields[i] for i, x in enumerate(CHESSARBITER_TOURNAMENT_FIELDS)}
                tourney_data[URL_FIELD] = link[0]
                del tourney_data[GARBAGE_FIELD]
                tournament_dicts.append(tourney_data)
        pd.DataFrame(tournament_dicts).to_csv(TOURNAMENT_DATA_PATH, index=False)
        self.log(f'Saved file {TOURNAMENT_DATA_PATH}')
