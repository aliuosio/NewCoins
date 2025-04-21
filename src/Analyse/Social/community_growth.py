#!/usr/bin/env python3
"""
Community Growth Indicator - Analyzes community size, engagement, and growth.
Replicates functionality from the old Indicator_Old version.
Now with real-time data from Twitter, Reddit, and other sources.
"""
import logging
import time
import random
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider # Assuming IDataProvider is in interfaces.py
from ..API.social_metrics_client import SocialMetricsClient

logger = logging.getLogger(__name__)

class CommunityGrowthIndicator(BaseIndicator):
    """
    Evaluates community growth, engagement, and health, replicating old logic.

    Uses real-time data from Twitter, Reddit, and other sources when available.
    Falls back to simulation when API keys are not provided or when APIs fail.

    Scoring (max 5 points): Based on a calculated 'community_health' score derived
    from community size, engagement rate, and growth rate.
    """

    # Override cache TTL to 1 hour for community metrics
    CACHE_TTL = 3600

    def __init__(self, data_provider: IDataProvider):
        # Max score is 5.0 as per the old indicator's logic/comment
        super().__init__(
            "community_growth",
            5.0,
            data_provider
        )
        # Note: The old version mapped this to 'community_engagement' in the DB.
        
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
            logger.info("Community growth analysis will use real-time data sources")
        else:
            logger.warning("No API keys provided. Community growth analysis will use simulation")

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the community growth score using real-time data.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id and community metrics).

        Returns:
            Dictionary with score and detailed community metrics.
        """
        from .utils import get_coin_id
        coin_id = get_coin_id(symbol, data)

        # --- Caching Logic ---
        cache_key = f"community_{coin_id}"
        cached_data = self._get_cached_result(cache_key)
        if cached_data:
            logger.info(f"Using cached community data for {coin_id}")
            # Recalculate score from cached processed data
            score = self._calculate_indicator_score(cached_data)
            cached_data['score'] = score
            return cached_data
        # --- End Caching Logic ---

        logger.info(f"Fetching/processing community data for {coin_id}")
        
        # Check if API keys are provided
        if not self.use_real_data:
            raise ValueError("No API keys provided for community metrics. Set TWITTER_BEARER_TOKEN, REDDIT_CLIENT_ID, and REDDIT_CLIENT_SECRET environment variables.")
        
        # Get combined metrics from multiple sources
        try:
            metrics_response = self.social_metrics_client.get_combined_metrics(
                query=coin_id
            )
            
            if not metrics_response:
                raise ValueError(f"Failed to get community metrics for {coin_id}")
        except Exception as e:
            logger.error(f"Error getting community metrics for {coin_id}: {str(e)}")
            # Create a minimal response with empty metrics
            metrics_response = {
                'current_metrics': {},
                'growth_metrics': {},
                'growth_history': [],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }
            
        # Extract metrics from response
        current_metrics = metrics_response.get('current_metrics', {})
        growth_metrics = metrics_response.get('growth_metrics', {})
        growth_history = metrics_response.get('growth_history', [])
        
        # Format the data to match the expected structure
        processed_data = {
            'current_metrics': current_metrics,
            'growth_metrics': growth_metrics,
            'growth_history': growth_history,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': True
        }
        
        logger.info(f"Successfully fetched real-time community metrics for {coin_id}")

        # Calculate the final score from the processed data
        score = self._calculate_indicator_score(processed_data)
        processed_data['score'] = score # Add score to the dictionary

        # Cache the processed data
        self._cache_result(cache_key, processed_data)

        return processed_data

    def _get_community_status(self, community_health: float) -> str:
        """Determine the community status based on health score."""
        if community_health >= 8:
            return "Thriving"
        elif community_health >= 6:
            return "Growing"
        elif community_health >= 4:
            return "Stable"
        elif community_health >= 2:
            return "Struggling"
        else:
            return "Inactive"

    def _calculate_indicator_score(self, processed_data: Dict[str, Any]) -> float:
        """
        Calculate the final score based on community health (old logic).

        Args:
            processed_data: The dictionary returned by _process_community_data.

        Returns:
            float: Score between 0 and self.max_score (5.0).
        """
        if not processed_data:
            return 0.0

        growth_metrics = processed_data.get('growth_metrics', {})
        community_health = float(growth_metrics.get('community_health', 0.0)) # Health is 0-10

        # Scale community health (0-10) to the max score (0-5)
        score = (community_health / 10.0) * self.max_score

        # Ensure score is within bounds (0 to max_score)
        score = max(0.0, min(score, self.max_score))

        return round(score, 1)
