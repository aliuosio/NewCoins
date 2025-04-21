from interfaces import CoinFetcher, CoinRepository, CoinAnalyzer, RecommendationService, CronJobManager
from implementations import DefaultCoinFetcher, PostgresCoinRepository, DefaultCoinAnalyzer, PostgresRecommendationService, PrintCronJobManager

class Scheduler:
    def __init__(self,
                 fetcher: CoinFetcher,
                 repo: CoinRepository,
                 analyzer: CoinAnalyzer,
                 recommender: RecommendationService,
                 cronjob_mgr: CronJobManager):
        self.fetcher = fetcher
        self.repo = repo
        self.analyzer = analyzer
        self.recommender = recommender
        self.cronjob_mgr = cronjob_mgr

    def run(self):
        self.fetcher.fetch()
        # Get new coins with launch times
        new_coin_times = self.repo.get_new_symbols_with_time()
        # Analyze only the symbols (not times)
        new_symbols = [symbol for symbol, _ in new_coin_times]
        self.analyzer.analyze(new_symbols)
        # Filter new_coin_times to only those that are qualified for trading
        qualified_symbols = set(self.recommender.get_qualified())
        qualified_coin_times = [(symbol, time_start) for symbol, time_start in new_coin_times if symbol in qualified_symbols]
        self.cronjob_mgr.create_jobs(qualified_coin_times)


if __name__ == "__main__":
    scheduler = Scheduler(
        fetcher=DefaultCoinFetcher(),
        repo=PostgresCoinRepository(),
        analyzer=DefaultCoinAnalyzer(),
        recommender=PostgresRecommendationService(),
        cronjob_mgr=PrintCronJobManager()
    )
    scheduler.run()
