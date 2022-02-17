from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging

from scrapy.crawler import CrawlerRunner
from spiders.player_data import TournamentSpider
from spiders.tournament_list import ChessarbiterMainWebsiteSpider


@defer.inlineCallbacks
def crawl(runner):
    yield runner.crawl(ChessarbiterMainWebsiteSpider)
    yield runner.crawl(TournamentSpider)
    reactor.stop()


if __name__ == "__main__":
    configure_logging()
    crawl_runner = CrawlerRunner()
    crawl(crawl_runner)
    reactor.run()
