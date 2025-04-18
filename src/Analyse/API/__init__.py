"""
API clients for fetching real-time data from various sources.
"""

from .base_client import BaseAPIClient
from .sentiment_client import SentimentAnalysisClient
from .social_metrics_client import SocialMetricsClient
from .github_client import GitHubClient

__all__ = [
    'BaseAPIClient',
    'SentimentAnalysisClient',
    'SocialMetricsClient',
    'GitHubClient'
]
