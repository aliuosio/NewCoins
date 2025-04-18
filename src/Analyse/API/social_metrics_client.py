"""
Social metrics client for fetching social media metrics from various sources.
"""
import logging
import os
import re
from typing import Dict, Any, Optional, List, Tuple, Union
import time
from datetime import datetime, timedelta
import requests

# Import Twitter API client
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# Import Reddit API client
try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)

class SocialMetricsClient(BaseAPIClient):
    """
    Client for fetching social media metrics from various sources.
    
    Supports:
    - Twitter metrics (followers, engagement)
    - Reddit metrics (subscribers, active users)
    - Telegram metrics (channel members)
    - External social metrics APIs
    """
    
    # Override cache TTL (1 hour for social metrics)
    CACHE_TTL = 3600
    
    # Social metrics sources
    SOURCE_TWITTER = 'twitter'
    SOURCE_REDDIT = 'reddit'
    SOURCE_TELEGRAM = 'telegram'
    SOURCE_EXTERNAL_API = 'external_api'
    
    def __init__(self, 
                api_key: Optional[str] = None, 
                api_secret: Optional[str] = None,
                twitter_bearer_token: Optional[str] = None,
                reddit_client_id: Optional[str] = None,
                reddit_client_secret: Optional[str] = None,
                telegram_api_id: Optional[str] = None,
                telegram_api_hash: Optional[str] = None,
                external_api_url: Optional[str] = None,
                cache_ttl: Optional[int] = None):
        """
        Initialize the social metrics client.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            twitter_bearer_token: Twitter API bearer token
            reddit_client_id: Reddit API client ID
            reddit_client_secret: Reddit API client secret
            telegram_api_id: Telegram API ID
            telegram_api_hash: Telegram API hash
            external_api_url: URL for external social metrics API
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(api_key, cache_ttl)
        self.api_secret = api_secret
        self.twitter_bearer_token = twitter_bearer_token
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.telegram_api_id = telegram_api_id
        self.telegram_api_hash = telegram_api_hash
        self.external_api_url = external_api_url
        
        # Initialize clients
        self.twitter_client = None
        self.reddit_client = None
        
        # Initialize Twitter client if credentials are provided
        if TWITTER_AVAILABLE and twitter_bearer_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=twitter_bearer_token)
                logger.info("Twitter client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {str(e)}")
        
        # Initialize Reddit client if credentials are provided
        if REDDIT_AVAILABLE and reddit_client_id and reddit_client_secret:
            try:
                self.reddit_client = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent="crypto_social_metrics/1.0"
                )
                logger.info("Reddit client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {str(e)}")
    
    def get_data(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Get social metrics data for a query.
        
        Args:
            query: Query string (e.g., "bitcoin", "ethereum")
            **kwargs: Additional parameters
                - source: Social metrics source (twitter, reddit, telegram, external_api)
                
        Returns:
            Social metrics data as a dictionary
        """
        source = kwargs.get('source', self.SOURCE_TWITTER)
        
        # Generate cache key
        cache_key = f"social_metrics_{source}_{query}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Get social metrics data based on source
        if source == self.SOURCE_TWITTER:
            metrics_data = self._get_twitter_metrics(query)
        elif source == self.SOURCE_REDDIT:
            metrics_data = self._get_reddit_metrics(query)
        elif source == self.SOURCE_TELEGRAM:
            metrics_data = self._get_telegram_metrics(query)
        elif source == self.SOURCE_EXTERNAL_API:
            metrics_data = self._get_external_api_metrics(query)
        else:
            # Default to Twitter metrics
            metrics_data = self._get_twitter_metrics(query)
        
        # Cache the result
        self._cache_result(cache_key, metrics_data)
        
        return metrics_data
    
    def _get_twitter_metrics(self, query: str) -> Dict[str, Any]:
        """
        Get Twitter metrics for a query.
        
        Args:
            query: Query string
            
        Returns:
            Twitter metrics as a dictionary
        """
        if not TWITTER_AVAILABLE or not self.twitter_client:
            logger.warning("Twitter API is not available. Using simulated metrics.")
            return self._get_simulated_metrics(query, source=self.SOURCE_TWITTER)
        
        try:
            # Try to find the Twitter username for the query
            # This is a simplified approach - in a real implementation,
            # you would use a more robust method to find the correct Twitter account
            username = query.lower()
            if username == 'bitcoin':
                username = 'bitcoin'
            elif username == 'ethereum':
                username = 'ethereum'
            elif username == 'binancecoin' or username == 'bnb':
                username = 'binance'
            elif username == 'ripple' or username == 'xrp':
                username = 'Ripple'
            elif username == 'cardano' or username == 'ada':
                username = 'Cardano'
            elif username == 'solana' or username == 'sol':
                username = 'solana'
            elif username == 'polkadot' or username == 'dot':
                username = 'Polkadot'
            elif username == 'dogecoin' or username == 'doge':
                username = 'dogecoin'
            
            # Get user information
            user = self.twitter_client.get_user(username=username, user_fields=['public_metrics', 'description', 'created_at'])
            
            if user.data:
                user_data = user.data
                metrics = user_data.public_metrics
                
                return {
                    'query': query,
                    'source': self.SOURCE_TWITTER,
                    'username': user_data.username,
                    'name': user_data.name,
                    'description': user_data.description,
                    'followers_count': metrics['followers_count'],
                    'following_count': metrics['following_count'],
                    'tweet_count': metrics['tweet_count'],
                    'listed_count': metrics['listed_count'],
                    'created_at': user_data.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                logger.warning(f"No Twitter user found for {query}")
                return self._get_simulated_metrics(query, source=self.SOURCE_TWITTER)
                
        except Exception as e:
            logger.error(f"Error getting Twitter metrics: {str(e)}")
            return self._get_simulated_metrics(query, source=self.SOURCE_TWITTER)
    
    def _get_reddit_metrics(self, query: str) -> Dict[str, Any]:
        """
        Get Reddit metrics for a query.
        
        Args:
            query: Query string
            
        Returns:
            Reddit metrics as a dictionary
        """
        if not REDDIT_AVAILABLE or not self.reddit_client:
            logger.warning("Reddit API is not available. Using simulated metrics.")
            return self._get_simulated_metrics(query, source=self.SOURCE_REDDIT)
        
        try:
            # Try to find the subreddit for the query
            # This is a simplified approach - in a real implementation,
            # you would use a more robust method to find the correct subreddit
            subreddit_name = query.lower()
            if subreddit_name == 'bitcoin':
                subreddit_name = 'Bitcoin'
            elif subreddit_name == 'ethereum':
                subreddit_name = 'ethereum'
            elif subreddit_name == 'binancecoin' or subreddit_name == 'bnb':
                subreddit_name = 'binance'
            elif subreddit_name == 'ripple' or subreddit_name == 'xrp':
                subreddit_name = 'XRP'
            elif subreddit_name == 'cardano' or subreddit_name == 'ada':
                subreddit_name = 'cardano'
            elif subreddit_name == 'solana' or subreddit_name == 'sol':
                subreddit_name = 'solana'
            elif subreddit_name == 'polkadot' or subreddit_name == 'dot':
                subreddit_name = 'Polkadot'
            elif subreddit_name == 'dogecoin' or subreddit_name == 'doge':
                subreddit_name = 'dogecoin'
            
            # Get subreddit information
            subreddit = self.reddit_client.subreddit(subreddit_name)
            
            # Get recent posts and comments for activity metrics
            recent_posts = list(subreddit.new(limit=100))
            recent_comments = list(subreddit.comments(limit=100))
            
            # Calculate posts and comments in the last 48 hours
            now = datetime.now()
            posts_48h = sum(1 for post in recent_posts if (now - datetime.fromtimestamp(post.created_utc)).total_seconds() < 48 * 3600)
            comments_48h = sum(1 for comment in recent_comments if (now - datetime.fromtimestamp(comment.created_utc)).total_seconds() < 48 * 3600)
            
            return {
                'query': query,
                'source': self.SOURCE_REDDIT,
                'subreddit': subreddit_name,
                'subscribers': subreddit.subscribers,
                'active_accounts': subreddit.accounts_active,
                'description': subreddit.description[:200] + '...' if len(subreddit.description) > 200 else subreddit.description,
                'posts_48h': posts_48h,
                'comments_48h': comments_48h,
                'created_at': datetime.fromtimestamp(subreddit.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
                
        except Exception as e:
            logger.error(f"Error getting Reddit metrics: {str(e)}")
            return self._get_simulated_metrics(query, source=self.SOURCE_REDDIT)
    
    def _get_telegram_metrics(self, query: str) -> Dict[str, Any]:
        """
        Get Telegram metrics for a query.
        
        Args:
            query: Query string
            
        Returns:
            Telegram metrics as a dictionary
        """
        # Telegram API requires a more complex setup with a client session
        # For simplicity, we'll use simulated metrics
        logger.warning("Telegram API is not implemented. Using simulated metrics.")
        return self._get_simulated_metrics(query, source=self.SOURCE_TELEGRAM)
    
    def _get_external_api_metrics(self, query: str) -> Dict[str, Any]:
        """
        Get social metrics from an external API.
        
        Args:
            query: Query string
            
        Returns:
            Social metrics as a dictionary
        """
        if not self.external_api_url:
            logger.warning("External API URL is not set. Using simulated metrics.")
            return self._get_simulated_metrics(query, source=self.SOURCE_EXTERNAL_API)
        
        try:
            # Make request to external API
            response = self.make_request(
                url=self.external_api_url,
                method='GET',
                params={'query': query},
                cache_key=f"external_metrics_{query}"
            )
            
            # Process response
            if 'metrics' in response:
                return response
            else:
                logger.warning(f"Unexpected response format from external API: {response}")
                return self._get_simulated_metrics(query, source=self.SOURCE_EXTERNAL_API)
            
        except Exception as e:
            logger.error(f"Error getting external API metrics: {str(e)}")
            return self._get_simulated_metrics(query, source=self.SOURCE_EXTERNAL_API)
    
    def _get_simulated_metrics(self, query: str, source: str) -> Dict[str, Any]:
        """
        Generate simulated social metrics.
        
        Args:
            query: Query string
            source: Social metrics source
            
        Returns:
            Simulated social metrics as a dictionary
        """
        # Map well-known coins to fixed metrics for consistency
        known_coins = {
            'bitcoin': {
                'twitter': {'followers': 5000000, 'following': 1000, 'tweets': 15000},
                'reddit': {'subscribers': 4500000, 'active': 10000, 'posts_48h': 100, 'comments_48h': 1000},
                'telegram': {'members': 200000, 'online': 5000, 'messages_48h': 5000}
            },
            'ethereum': {
                'twitter': {'followers': 3000000, 'following': 800, 'tweets': 12000},
                'reddit': {'subscribers': 1500000, 'active': 5000, 'posts_48h': 50, 'comments_48h': 500},
                'telegram': {'members': 150000, 'online': 3000, 'messages_48h': 3000}
            },
            'binancecoin': {
                'twitter': {'followers': 1000000, 'following': 500, 'tweets': 8000},
                'reddit': {'subscribers': 700000, 'active': 3000, 'posts_48h': 30, 'comments_48h': 300},
                'telegram': {'members': 300000, 'online': 8000, 'messages_48h': 8000}
            },
            'ripple': {
                'twitter': {'followers': 2000000, 'following': 600, 'tweets': 10000},
                'reddit': {'subscribers': 350000, 'active': 2000, 'posts_48h': 20, 'comments_48h': 200},
                'telegram': {'members': 100000, 'online': 2000, 'messages_48h': 2000}
            },
            'cardano': {
                'twitter': {'followers': 1200000, 'following': 400, 'tweets': 9000},
                'reddit': {'subscribers': 700000, 'active': 4000, 'posts_48h': 40, 'comments_48h': 400},
                'telegram': {'members': 120000, 'online': 2500, 'messages_48h': 2500}
            },
            'solana': {
                'twitter': {'followers': 900000, 'following': 300, 'tweets': 7000},
                'reddit': {'subscribers': 300000, 'active': 2000, 'posts_48h': 30, 'comments_48h': 300},
                'telegram': {'members': 150000, 'online': 3000, 'messages_48h': 3000}
            },
            'polkadot': {
                'twitter': {'followers': 700000, 'following': 200, 'tweets': 5000},
                'reddit': {'subscribers': 250000, 'active': 1500, 'posts_48h': 20, 'comments_48h': 200},
                'telegram': {'members': 90000, 'online': 1800, 'messages_48h': 1800}
            },
            'dogecoin': {
                'twitter': {'followers': 3500000, 'following': 1200, 'tweets': 20000},
                'reddit': {'subscribers': 2200000, 'active': 8000, 'posts_48h': 80, 'comments_48h': 800},
                'telegram': {'members': 200000, 'online': 4000, 'messages_48h': 4000}
            },
            'shiba-inu': {
                'twitter': {'followers': 3200000, 'following': 1000, 'tweets': 18000},
                'reddit': {'subscribers': 1800000, 'active': 7000, 'posts_48h': 70, 'comments_48h': 700},
                'telegram': {'members': 250000, 'online': 5000, 'messages_48h': 5000}
            }
        }
        
        # Check if query matches any known coin
        query_lower = query.lower()
        metrics = None
        for coin, values in known_coins.items():
            if coin in query_lower or query_lower in coin:
                metrics = values
                break
        
        # Generate random metrics if not a known coin
        if not metrics:
            # Generate metrics based on hash of query for consistency
            hash_value = sum(ord(c) for c in query)
            
            metrics = {
                'twitter': {
                    'followers': 5000 + (hash_value % 100000),
                    'following': 100 + (hash_value % 1000),
                    'tweets': 1000 + (hash_value % 10000)
                },
                'reddit': {
                    'subscribers': 2000 + (hash_value % 50000),
                    'active': 100 + (hash_value % 1000),
                    'posts_48h': 5 + (hash_value % 50),
                    'comments_48h': 50 + (hash_value % 500)
                },
                'telegram': {
                    'members': 1000 + (hash_value % 20000),
                    'online': 100 + (hash_value % 1000),
                    'messages_48h': 500 + (hash_value % 5000)
                }
            }
        
        # Return metrics based on source
        if source == self.SOURCE_TWITTER:
            return {
                'query': query,
                'source': self.SOURCE_TWITTER,
                'username': query_lower,
                'name': query.replace('-', ' ').title(),
                'description': f"Official Twitter account for {query.replace('-', ' ').title()}",
                'followers_count': metrics['twitter']['followers'],
                'following_count': metrics['twitter']['following'],
                'tweet_count': metrics['twitter']['tweets'],
                'listed_count': metrics['twitter']['followers'] // 100,
                'created_at': (datetime.now() - timedelta(days=1000 + (hash(query) % 1000))).strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'simulated': True
            }
        elif source == self.SOURCE_REDDIT:
            return {
                'query': query,
                'source': self.SOURCE_REDDIT,
                'subreddit': query_lower,
                'subscribers': metrics['reddit']['subscribers'],
                'active_accounts': metrics['reddit']['active'],
                'description': f"Official subreddit for {query.replace('-', ' ').title()} - Discuss price, news, and technology.",
                'posts_48h': metrics['reddit']['posts_48h'],
                'comments_48h': metrics['reddit']['comments_48h'],
                'created_at': (datetime.now() - timedelta(days=1000 + (hash(query) % 1000))).strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'simulated': True
            }
        elif source == self.SOURCE_TELEGRAM:
            return {
                'query': query,
                'source': self.SOURCE_TELEGRAM,
                'channel_name': query_lower,
                'title': query.replace('-', ' ').title() + " Official",
                'members_count': metrics['telegram']['members'],
                'online_count': metrics['telegram']['online'],
                'messages_48h': metrics['telegram']['messages_48h'],
                'description': f"Official Telegram channel for {query.replace('-', ' ').title()} - News, updates, and community discussion.",
                'created_at': (datetime.now() - timedelta(days=500 + (hash(query) % 500))).strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'simulated': True
            }
        else:  # External API or fallback
            return {
                'query': query,
                'source': source,
                'twitter': {
                    'followers': metrics['twitter']['followers'],
                    'following': metrics['twitter']['following'],
                    'tweets': metrics['twitter']['tweets']
                },
                'reddit': {
                    'subscribers': metrics['reddit']['subscribers'],
                    'active_accounts': metrics['reddit']['active'],
                    'posts_48h': metrics['reddit']['posts_48h'],
                    'comments_48h': metrics['reddit']['comments_48h']
                },
                'telegram': {
                    'members': metrics['telegram']['members'],
                    'online': metrics['telegram']['online'],
                    'messages_48h': metrics['telegram']['messages_48h']
                },
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'simulated': True
            }
    
    def get_combined_metrics(self, query: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get combined social metrics from multiple sources.
        
        Args:
            query: Query string
            sources: List of sources to use (defaults to all available)
                
        Returns:
            Combined social metrics as a dictionary
        """
        if sources is None:
            sources = []
            if TWITTER_AVAILABLE and self.twitter_client:
                sources.append(self.SOURCE_TWITTER)
            if REDDIT_AVAILABLE and self.reddit_client:
                sources.append(self.SOURCE_REDDIT)
            sources.append(self.SOURCE_TELEGRAM)  # Always include Telegram (simulated)
            if self.external_api_url:
                sources.append(self.SOURCE_EXTERNAL_API)
            
            # If no API clients are available, use simulated data
            if not sources:
                sources = [self.SOURCE_TWITTER, self.SOURCE_REDDIT, self.SOURCE_TELEGRAM]
        
        # Generate cache key
        cache_key = f"combined_metrics_{query}_{'-'.join(sources)}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Get metrics from each source
        metrics_data = {}
        for source in sources:
            metrics_data[source] = self.get_data(query, source=source)
        
        # Extract metrics from each source
        twitter_followers = metrics_data.get(self.SOURCE_TWITTER, {}).get('followers_count', 0)
        reddit_subscribers = metrics_data.get(self.SOURCE_REDDIT, {}).get('subscribers', 0)
        reddit_active = metrics_data.get(self.SOURCE_REDDIT, {}).get('active_accounts', 0)
        telegram_members = metrics_data.get(self.SOURCE_TELEGRAM, {}).get('members_count', 0)
        
        # Calculate total social reach
        total_social_reach = twitter_followers + reddit_subscribers + telegram_members
        
        # Calculate engagement metrics
        reddit_engagement_rate = (reddit_active / max(reddit_subscribers, 1)) if reddit_subscribers else 0
        
        # Calculate growth metrics (simulated)
        # In a real implementation, you would compare with historical data
        growth_rate = 0.05  # Default 5% monthly growth
        
        # Use known coin data if available
        known_coins_growth = {
            'bitcoin': 0.05,
            'ethereum': 0.07,
            'binancecoin': 0.08,
            'ripple': 0.03,
            'cardano': 0.06,
            'solana': 0.12,
            'polkadot': 0.05,
            'dogecoin': 0.15,
            'shiba-inu': 0.18
        }
        
        query_lower = query.lower()
        for coin, rate in known_coins_growth.items():
            if coin in query_lower or query_lower in coin:
                growth_rate = rate
                break
        
        # Generate growth history (simulated)
        growth_history = []
        for i in range(6, 0, -1):
            month_total = int(total_social_reach / ((1 + growth_rate) ** i))
            month_date = (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d')
            growth_history.append({
                'date': month_date,
                'total_social_reach': month_total
            })
        
        # Add current month
        growth_history.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_social_reach': total_social_reach
        })
        
        # Calculate community health score
        community_size_score = min(10, (total_social_reach / 1000000) * 5)
        engagement_score = min(10, reddit_engagement_rate * 100)
        growth_score = min(10, growth_rate * 50)
        
        community_health = (community_size_score * 0.4) + (engagement_score * 0.4) + (growth_score * 0.2)
        
        result = {
            'query': query,
            'sources': sources,
            'current_metrics': {
                'twitter_followers': twitter_followers,
                'reddit_subscribers': reddit_subscribers,
                'reddit_active_accounts': reddit_active,
                'telegram_users': telegram_members,
                'total_social_reach': total_social_reach,
                'reddit_engagement_rate': round(reddit_engagement_rate, 3)
            },
            'growth_metrics': {
                'estimated_monthly_growth_rate': round(growth_rate, 3),
                'estimated_monthly_growth': int(total_social_reach * growth_rate),
                'community_size_score': round(community_size_score, 1),
                'engagement_score': round(engagement_score, 1),
                'growth_score': round(growth_score, 1),
                'community_health': round(community_health, 1),
                'community_status': self._get_community_status(community_health)
            },
            'growth_history': growth_history,
            'source_data': metrics_data,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Cache the result
        self._cache_result(cache_key, result)
        
        return result
    
    def _get_community_status(self, community_health: float) -> str:
        """
        Determine the community status based on health score.
        
        Args:
            community_health: Community health score (0-10)
            
        Returns:
            Community status as a string
        """
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
