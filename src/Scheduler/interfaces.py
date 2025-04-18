from typing import List, Protocol

class CoinFetcher(Protocol):
    def fetch(self) -> None:
        ...

class CoinRepository(Protocol):
    def get_new_symbols(self) -> List[str]:
        ...

class CoinAnalyzer(Protocol):
    def analyze(self, symbols: List[str]) -> None:
        ...

class RecommendationService(Protocol):
    def get_qualified(self) -> List[str]:
        ...

class CronJobManager(Protocol):
    def create_jobs(self, symbols: List[str]) -> None:
        ...
