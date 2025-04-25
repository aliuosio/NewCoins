#!/usr/bin/env python3
"""
Sentiment Analysis Indicator - Evaluates positive vs negative sentiment.
Replicates functionality from the old Indicator_Old version (social_media_sentiment.py).
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
from ..API.sentiment_client import SentimentAnalysisClient

logger = logging.getLogger(__name__)

class SentimentAnalysisIndicator(BaseIndicator):
    """
    Evaluates social media sentiment for cryptocurrencies, replicating old logic.

    Uses real-time data from Twitter, Reddit, and other sources when available.
    Falls back to simulation when API keys are not provided or when APIs fail.

    Scoring (max 10 points): Based on positive sentiment percentage,
    adjusted by positive/negative ratio and trend factor.
    """

    # Override cache TTL to 2 hours for sentiment data
    CACHE_TTL = 7200

    def __init__(self, data_provider: IDataProvider):
        super().__init__(
            "sentiment_analysis",
            10.0, # Max score remains 10
            data_provider
        )
        # Note: The old version mapped this to 'sentiment_analysis' in the DB.
        
        # Initialize sentiment analysis client
        # Get API keys from environment variables
        twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        # Create sentiment analysis client
        self.sentiment_client = SentimentAnalysisClient(
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
            logger.info("Sentiment analysis will use real-time data sources")
        else:
            logger.warning("No API keys provided. Sentiment analysis will use simulation")

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the sentiment analysis score using real-time data.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id and social metrics).

        Returns:
            Dictionary with score and detailed sentiment metrics.
        """
        # Check if data is None
        if data is None:
            logger.error(f"Data is None for {symbol}")
            return self._create_empty_sentiment_data(symbol)
            
        try:
            from .utils import get_coin_id
            try:
                coin_id = get_coin_id(symbol, data)
            except Exception as e:
                logger.error(f"Error getting coin_id for {symbol}: {str(e)}")
                return self._create_empty_sentiment_data(symbol)

            # --- Caching Logic ---
            cache_key = f"sentiment_{coin_id}"
            cached_data = self._get_cached_result(cache_key)
            if cached_data:
                logger.info(f"Using cached sentiment data for {coin_id}")
                # Recalculate score from cached processed data
                score = self._calculate_indicator_score(cached_data)
                cached_data['score'] = score
                return cached_data
            # --- End Caching Logic ---
        except Exception as e:
            logger.error(f"Unexpected error in sentiment analysis for {symbol}: {str(e)}")
            return self._create_empty_sentiment_data(symbol)

            logger.info(f"Fetching/processing sentiment data for {coin_id}")
            
            # Check if API keys are provided
            if not self.use_real_data:
                logger.warning("No API keys provided for sentiment analysis. Using simulated data.")
                return self._create_simulated_sentiment_data(coin_id)
            
            try:
                # Get combined sentiment from multiple sources
                sentiment_response = self.sentiment_client.get_combined_sentiment(
                    query=coin_id,
                    days=7,
                    limit=100
                )
                
                if not sentiment_response:
                    logger.warning(f"Failed to get sentiment data for {coin_id}. Using simulated data.")
                    return self._create_simulated_sentiment_data(coin_id)
                    
                # Ensure sentiment_response is not None
                if sentiment_response is None:
                    logger.warning(f"Sentiment response is None for {coin_id}. Using simulated data.")
                    return self._create_simulated_sentiment_data(coin_id)
            except Exception as e:
                logger.error(f"Error getting sentiment data for {coin_id}: {str(e)}")
                return self._create_simulated_sentiment_data(coin_id)
                
            # Extract sentiment data from response
            sentiment = sentiment_response.get('sentiment', {})
            if sentiment is None:
                sentiment = {}
                logger.warning(f"Sentiment data is None for {coin_id}, using empty dictionary")
                
            sentiment_ratio = sentiment_response.get('sentiment_ratio', 1.0)
            trend = sentiment_response.get('trend', 'stable')
            trend_value = sentiment_response.get('trend_value', 0)
            samples = sentiment_response.get('samples', [])
            
            # Extract community data from the data provider
            community_data = data.get('community_data', {})
            if community_data is None:
                community_data = {}
                logger.warning(f"Community data is None for {coin_id}, using empty dictionary")
                
            developer_data = data.get('developer_data', {})
            if developer_data is None:
                developer_data = {}
                logger.warning(f"Developer data is None for {coin_id}, using empty dictionary")
            
            twitter_followers = community_data.get('twitter_followers', 0)
            reddit_subscribers = community_data.get('reddit_subscribers', 0)
            reddit_active_accounts = community_data.get('reddit_active_accounts_48h', 0)
            github_stars = developer_data.get('stars', 0)
        
        # Format the data to match the expected structure
        sentiment_data = {
            'sentiment': sentiment,
            'sentiment_ratio': sentiment_ratio,
            'trend': trend,
            'trend_value': trend_value,
            'engagement': {
                'twitter_followers': twitter_followers,
                'reddit_subscribers': reddit_subscribers,
                'reddit_active_ratio': round((reddit_active_accounts / max(reddit_subscribers, 1)), 3) if reddit_subscribers else 0,
                'github_stars': github_stars,
                'total_social_reach': twitter_followers + reddit_subscribers
            },
            'recent_posts': [
                {
                    'text': sample.get('text', ''),
                    'sentiment': sample.get('sentiment', 'neutral'),
                    'platform': sample.get('platform', 'Unknown'),
                    'timestamp': sample.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                }
                for sample in samples[:5]  # Include up to 5 samples
            ],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': True
        }
        
        logger.info(f"Successfully fetched real-time sentiment data for {coin_id}")

        # Calculate the final score from the processed data
        score = self._calculate_indicator_score(sentiment_data)
        sentiment_data['score'] = score # Add score to the dictionary

        # Cache the processed data
        self._cache_result(cache_key, sentiment_data)

        return sentiment_data


    def _calculate_indicator_score(self, processed_data: Dict[str, Any]) -> float:
        """
        Calculate the final score based on simulated sentiment metrics (old logic).

        Args:
            processed_data: The dictionary returned by _generate_sentiment_metrics.

        Returns:
            float: Score between 0 and self.max_score (10.0).
        """
        if not processed_data:
            return 0.0

        sentiment = processed_data.get('sentiment', {})
        sentiment_ratio = processed_data.get('sentiment_ratio', 1)
        trend_value = processed_data.get('trend_value', 0)

        # Ensure sentiment is not None before accessing its attributes
        if sentiment is None:
            sentiment = {}
            logger.warning("Sentiment data is None, using empty dictionary instead")

        # Base score from positive sentiment percentage (old logic)
        base_score = sentiment.get('positive', 0) * 10

        # Adjust based on sentiment ratio (positive to negative)
        ratio_factor = min(sentiment_ratio / 3, 1) # Cap at 1

        # Adjust based on trend
        trend_adjustment = trend_value * 2 # Scale trend impact

        # Calculate final score using old weighting/formula
        score = base_score * (0.7 + (ratio_factor * 0.2) + (trend_adjustment * 0.1))

        # Ensure score is within bounds (0 to max_score)
        score = max(0.0, min(score, self.max_score))

        return round(score, 1)
        
    def _create_empty_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """
        Create an empty sentiment data structure with default values.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Dictionary with empty sentiment data and zero score
        """
        logger.info(f"Creating empty sentiment data for {symbol}")
        
        sentiment_data = {
            'sentiment': {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            },
            'sentiment_ratio': 1.0,
            'trend': 'stable',
            'trend_value': 0,
            'engagement': {
                'twitter_followers': 0,
                'reddit_subscribers': 0,
                'reddit_active_ratio': 0,
                'github_stars': 0,
                'total_social_reach': 0
            },
            'recent_posts': [],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': False,
            'simulated': False,
            'error': True
        }
        
        # Calculate score (will be 0)
        score = self._calculate_indicator_score(sentiment_data)
        sentiment_data['score'] = score
        
        return sentiment_data
        
    def _create_simulated_sentiment_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Create simulated sentiment data when real data is not available.
        
        Args:
            coin_id: Cryptocurrency ID
            
        Returns:
            Dictionary with simulated sentiment data
        """
        logger.info(f"Creating simulated sentiment data for {coin_id}")
        
        # Generate hash from coin_id for consistent random values
        import hashlib
        hash_value = int(hashlib.md5(coin_id.encode()).hexdigest(), 16) % 10000
        
        # Generate sentiment distribution (positive, negative, neutral)
        # Make it somewhat realistic but generally positive
        positive = 0.4 + (hash_value % 40) / 100  # 0.4 to 0.8
        negative = 0.1 + (hash_value % 20) / 100  # 0.1 to 0.3
        neutral = 1.0 - positive - negative
        
        # Generate sentiment ratio (positive to negative)
        sentiment_ratio = positive / max(0.01, negative)  # Avoid division by zero
        
        # Generate trend value (-1 to 1)
        trend_value = -0.5 + (hash_value % 100) / 100  # -0.5 to 0.5
        
        # Determine trend description
        if trend_value > 0.2:
            trend = 'improving'
        elif trend_value < -0.2:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Generate engagement metrics
        twitter_followers = 1000 + (hash_value % 10000)
        reddit_subscribers = 500 + (hash_value % 5000)
        reddit_active_ratio = 0.05 + (hash_value % 20) / 100  # 0.05 to 0.25
        github_stars = 100 + (hash_value % 1000)
        
        # Generate sample posts
        sample_posts = [
            {
                'text': f"Really excited about the future of {coin_id}! #crypto",
                'sentiment': 'positive',
                'platform': 'Twitter',
                'timestamp': (datetime.now() - timedelta(hours=hash_value % 24)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'text': f"Just bought some more {coin_id}. The tech looks promising.",
                'sentiment': 'positive',
                'platform': 'Reddit',
                'timestamp': (datetime.now() - timedelta(hours=hash_value % 48)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'text': f"Not sure about {coin_id}, waiting to see more development.",
                'sentiment': 'neutral',
                'platform': 'Twitter',
                'timestamp': (datetime.now() - timedelta(hours=hash_value % 72)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        # Create the sentiment data structure
        sentiment_data = {
            'sentiment': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            },
            'sentiment_ratio': sentiment_ratio,
            'trend': trend,
            'trend_value': trend_value,
            'engagement': {
                'twitter_followers': twitter_followers,
                'reddit_subscribers': reddit_subscribers,
                'reddit_active_ratio': reddit_active_ratio,
                'github_stars': github_stars,
                'total_social_reach': twitter_followers + reddit_subscribers
            },
            'recent_posts': sample_posts,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': False,
            'simulated': True
        }
        
        # Calculate score
        score = self._calculate_indicator_score(sentiment_data)
        sentiment_data['score'] = score
        
        return sentiment_data
