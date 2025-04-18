from .interfaces import CoinFetcher, CoinRepository, CoinAnalyzer, RecommendationService, CronJobManager
from .implementations import DefaultCoinFetcher, PostgresCoinRepository, DefaultCoinAnalyzer, PostgresRecommendationService, PrintCronJobManager

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
        new_coins = self.repo.get_new_symbols()
        self.analyzer.analyze(new_coins)
        qualified = self.recommender.get_qualified()
        self.cronjob_mgr.create_jobs(qualified)

if __name__ == "__main__":
    scheduler = Scheduler(
        fetcher=DefaultCoinFetcher(),
        repo=PostgresCoinRepository(),
        analyzer=DefaultCoinAnalyzer(),
        recommender=PostgresRecommendationService(),
        cronjob_mgr=PrintCronJobManager()
    )
    scheduler.run()
