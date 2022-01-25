import pandas as pd
import scrapy

try:
    from constants import TOURNAMENT_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, URL_FIELD
except ModuleNotFoundError as s:
    from ..constants import TOURNAMENT_DATA_PATH, CHESSARBITER_TOURNAMENT_FIELDS, URL_FIELD


def remove_stuff_from_list(arr, stuff):
    arr_str = '#$&'.join(arr)
    return multi_replace(arr_str, stuff, '').split('#$&')


def multi_replace(text, chars_to_replace, what_to_replace_with):
    for ch in chars_to_replace:
        if ch in text:
            text = text.replace(ch, what_to_replace_with)
    return text


class ChessarbiterMainWebsiteSpider(scrapy.Spider):
    name = "tournament_list"
    start_urls = ["http://chessarbiter.com/"]

    def parse(self, response, **kwargs):
        tournament_dicts = []
        field_no = []
        for table in response.xpath('//table')[14:]:
            for row in table.xpath('tr'):
                link = row.xpath('td//@href').extract()
                txt_fields = row.xpath('td//text()').extract()
                if txt_fields[-1] == 'FIDE':
                    txt_fields = txt_fields[:-1]
                if len(txt_fields) == 7:
                    txt_fields = txt_fields[:3] + txt_fields[4:]
                elif len(txt_fields) == 8:
                    txt_fields = txt_fields[:3] + txt_fields[5:]
                elif len(txt_fields) == 9:
                    txt_fields = txt_fields[:3] + txt_fields[5:]
                elif len(txt_fields) == 10:
                    txt_fields = txt_fields[:3] + [txt_fields[5] + txt_fields[6] + txt_fields[7]] + txt_fields[8:]
                else:
                    raise ValueError("Wrong number of fields for the tournament!")
                if len(txt_fields) != 6:
                    raise ValueError("Wrong number of fields for the tournament!")
                field_no.append(len(txt_fields))
                tourney_data = {x: txt_fields[i] for i, x in
                                enumerate(CHESSARBITER_TOURNAMENT_FIELDS)}
                tourney_data[URL_FIELD] = link[0]
                tournament_dicts.append(tourney_data)
        pd.DataFrame(tournament_dicts).to_csv(TOURNAMENT_DATA_PATH, index=False)
        self.log(f'Saved file {TOURNAMENT_DATA_PATH}')
