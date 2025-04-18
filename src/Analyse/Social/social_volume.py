#!/usr/bin/env python3
"""
Social Volume Indicator - Analyzes social media mentions and engagement.
Combines functionality from multiple social indicators in the old version.
"""
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider
from ..API.social_metrics_client import SocialMetricsClient

logger = logging.getLogger(__name__)

class SocialVolumeIndicator(BaseIndicator):
    """
    Evaluates social media volume and engagement for cryptocurrencies.
    
    Uses real-time data from Twitter, Reddit, and other sources.
    
    Scoring (max 10 points): Based on mention volume, engagement rate, and growth.
    """

    # Override cache TTL to 1 hour for social metrics
    CACHE_TTL = 3600

    def __init__(self, data_provider: IDataProvider):
        super().__init__(
            "social_volume",
            10.0,  # Max score is 10
            data_provider
        )
        
        # Initialize social metrics client
        # Get API keys from environment variables
        twitter_bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
        reddit_client_id = os.environ.get('REDDIT_CLIENT_ID')
        reddit_client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        # Create social metrics client
        self.social_metrics_client = SocialMetricsClient(
            twitter_bearer_token=twitter_bearer_token,
            reddit_client_id=reddit_client_id,
            reddit_client_secret=reddit_client_secret,
            cache_ttl=self.CACHE_TTL
        )
        
        # Check if real-time data sources are available
        self.use_real_data = (
            twitter_bearer_token is not None or 
            (reddit_client_id is not None and reddit_client_secret is not None)
        )
        
        if self.use_real_data:
            logger.info("Social volume analysis will use real-time data sources")
        else:
            logger.warning("No API keys provided. Social volume analysis will require API keys")

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the social volume score using real-time data.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id and social metrics).

        Returns:
            Dictionary with score and detailed social volume metrics.
        """
        coin_id = data.get('id')  # Assumes data provider returns coin_id like 'bitcoin'
        if not coin_id:
            coin_id = symbol.lower()
            logger.warning(f"Coin ID not found in data for {symbol}, using symbol '{coin_id}' as fallback.")

        # --- Caching Logic ---
        cache_key = f"social_volume_{coin_id}"
        cached_data = self._get_cached_result(cache_key)
        if cached_data:
            logger.info(f"Using cached social volume data for {coin_id}")
            # Recalculate score from cached processed data
            score = self._calculate_indicator_score(cached_data)
            cached_data['score'] = score
            return cached_data
        # --- End Caching Logic ---

        logger.info(f"Fetching/processing social volume data for {coin_id}")
        
        # Check if API keys are provided
        if not self.use_real_data:
            raise ValueError("No API keys provided for social metrics. Set TWITTER_BEARER_TOKEN, REDDIT_CLIENT_ID, and REDDIT_CLIENT_SECRET environment variables.")
        
        # Get social volume metrics from multiple sources
        volume_response = self.social_metrics_client.get_social_volume(
            query=coin_id,
            days=7
        )
        
        if not volume_response:
            raise ValueError(f"Failed to get social volume data for {coin_id}")
            
        # Extract metrics from response
        mention_count = volume_response.get('mention_count', 0)
        engagement_count = volume_response.get('engagement_count', 0)
        sentiment_ratio = volume_response.get('sentiment_ratio', 1.0)
        growth_rate = volume_response.get('growth_rate', 0.0)
        platforms = volume_response.get('platforms', {})
        
        # Format the data
        volume_data = {
            'mention_count': mention_count,
            'engagement_count': engagement_count,
            'engagement_rate': engagement_count / max(mention_count, 1) if mention_count else 0,
            'sentiment_ratio': sentiment_ratio,
            'growth_rate': growth_rate,
            'platforms': platforms,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': True
        }
        
        logger.info(f"Successfully fetched real-time social volume data for {coin_id}")

        # Calculate the final score from the processed data
        score = self._calculate_indicator_score(volume_data)
        volume_data['score'] = score  # Add score to the dictionary

        # Cache the processed data
        self._cache_result(cache_key, volume_data)

        return volume_data

    def _calculate_indicator_score(self, processed_data: Dict[str, Any]) -> float:
        """
        Calculate the final score based on social volume metrics.

        Args:
            processed_data: The dictionary with social volume metrics.

        Returns:
            float: Score between 0 and self.max_score (10.0).
        """
        if not processed_data:
            return 0.0

        mention_count = processed_data.get('mention_count', 0)
        engagement_rate = processed_data.get('engagement_rate', 0)
        growth_rate = processed_data.get('growth_rate', 0)
        sentiment_ratio = processed_data.get('sentiment_ratio', 1.0)

        # Calculate score components
        # Mention volume score (0-5 points)
        volume_score = min(5.0, (mention_count / 10000) * 5)
        
        # Engagement score (0-3 points)
        engagement_score = min(3.0, engagement_rate * 30)
        
        # Growth score (0-2 points)
        growth_score = min(2.0, growth_rate * 10)
        
        # Calculate final score
        score = volume_score + engagement_score + growth_score
        
        # Adjust based on sentiment ratio (positive to negative)
        sentiment_factor = min(1.2, max(0.8, sentiment_ratio / 2))
        score = score * sentiment_factor
        
        # Ensure score is within bounds (0 to max_score)
        score = max(0.0, min(score, self.max_score))

        return round(score, 1)
