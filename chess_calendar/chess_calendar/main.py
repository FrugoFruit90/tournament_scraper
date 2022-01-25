from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scrapy.crawler import CrawlerRunner
from spiders.player_data import TournamentSpider
from spiders.tournament_list import ChessarbiterMainWebsiteSpider

configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(ChessarbiterMainWebsiteSpider)
    yield runner.crawl(TournamentSpider)
    reactor.stop()


crawl()
reactor.run()
