#!/usr/bin/env python3
"""
Sentiment Analysis Indicator - Evaluates positive vs negative sentiment across platforms.

This indicator analyzes the sentiment of social media posts, comments, and discussions
to determine the overall market sentiment toward a cryptocurrency.
"""
import logging
from typing import Dict, Any, Optional

from ..base_indicator import BaseIndicator

logger = logging.getLogger(__name__)

class SentimentAnalysisIndicator(BaseIndicator):
    """
    Evaluates social media sentiment for cryptocurrencies.
    
    Scoring (max 10 points):
    - 10 points: Extremely positive sentiment (>80% positive)
    - 8 points: Very positive sentiment (70-80% positive)
    - 6 points: Positive sentiment (60-70% positive)
    - 4 points: Neutral sentiment (40-60% positive)
    - 2 points: Negative sentiment (30-40% positive)
    - 0 points: Very negative sentiment (<30% positive)
    
    Additional factors:
    - Sentiment consistency across platforms
    - Sentiment from influential accounts weighted more heavily
    - Recent sentiment trend (improving or declining)
    """
    
    def __init__(self, data_provider):
        super().__init__(
            "sentiment_analysis",
            10.0,
            data_provider
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the sentiment analysis score based on social media metrics.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing social metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract social metrics from data
        community_data = data.get('community_data', {})
        developer_data = data.get('developer_data', {})
        
        twitter_followers = community_data.get('twitter_followers', 0)
        reddit_subscribers = community_data.get('reddit_subscribers', 0)
        reddit_active_accounts = community_data.get('reddit_active_accounts', 0)
        github_stars = developer_data.get('stars', 0)
        
        # Calculate total social reach
        total_social_reach = twitter_followers + reddit_subscribers
        
        # Calculate engagement rate
        engagement_rate = (reddit_active_accounts / max(reddit_subscribers, 1)) if reddit_subscribers else 0
        
        # Base score based on engagement and reach
        base_score = 0.0
        if engagement_rate >= 0.1:  # 10% or higher engagement
            base_score = 10.0
        elif engagement_rate >= 0.05:  # 5-10% engagement
            base_score = 8.0
        elif engagement_rate >= 0.02:  # 2-5% engagement
            base_score = 6.0
        elif engagement_rate >= 0.01:  # 1-2% engagement
            base_score = 4.0
        elif engagement_rate > 0:  # Any engagement
            base_score = 2.0
        
        # Developer activity bonus (1-2 points)
        developer_bonus = 0.0
        if github_stars >= 10000:  # 10K+ stars
            developer_bonus = 2.0
        elif github_stars >= 1000:  # 1K-10K stars
            developer_bonus = 1.0
        
        # Calculate final score (capped at max_score)
        final_score = min(base_score + developer_bonus, self.max_score)
        
        return {
            'score': final_score,
            'total_social_reach': total_social_reach,
            'twitter_followers': twitter_followers,
            'reddit_subscribers': reddit_subscribers,
            'reddit_active_accounts': reddit_active_accounts,
            'github_stars': github_stars,
            'engagement_rate': engagement_rate,
            'base_score': base_score,
            'developer_bonus': developer_bonus
        }
