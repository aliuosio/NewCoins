"""
Domain-specific repositories for database operations.
Each repository is responsible for a specific domain entity.
"""

from .analysis import AnalysisRepository
from .social import SocialRepository
from .cron import CronRepository
from .coins import CoinRepository

__all__ = [
    'AnalysisRepository',
    'SocialRepository',
    'CronRepository',
    'CoinRepository',
]
