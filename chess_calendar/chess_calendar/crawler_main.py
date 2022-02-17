from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from twisted.internet import defer, reactor

from chess_calendar.chess_calendar.spiders.player_data import TournamentSpider
from chess_calendar.chess_calendar.spiders.tournament_list import ChessarbiterMainWebsiteSpider


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
