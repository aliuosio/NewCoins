"""
Social indicators for cryptocurrency analysis.

This module contains indicators that evaluate social metrics such as:
- Social media mentions and discussion volume
- Sentiment analysis across platforms (simulated)
- Developer activity and community engagement (simulated/hardcoded elements)
- Community growth and health (simulated/hardcoded elements)
- Google search trends (using pytrends or simulated)
"""

from .sentiment_analysis import SentimentAnalysisIndicator
from .developer_activity import DeveloperActivityIndicator
from .community_growth import CommunityGrowthIndicator # Added
from .google_trends import GoogleTrendsIndicator     # Added

__all__ = [
    'SentimentAnalysisIndicator',
    'DeveloperActivityIndicator',
    'CommunityGrowthIndicator', # Added
    'GoogleTrendsIndicator'     # Added
]
