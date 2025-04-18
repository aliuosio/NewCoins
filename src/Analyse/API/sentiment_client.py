"""
Sentiment analysis client for analyzing text sentiment from various sources.
"""
import logging
import os
import re
from typing import Dict, Any, Optional, List, Tuple, Union
import time
from datetime import datetime, timedelta
import requests

# Import TextBlob for local sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

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

class SentimentAnalysisClient(BaseAPIClient):
    """
    Client for analyzing sentiment from various sources.
    
    Supports:
    - Local sentiment analysis using TextBlob
    - Twitter sentiment analysis
    - Reddit sentiment analysis
    - External sentiment analysis APIs
    """
    
    # Override cache TTL (2 hours for sentiment data)
    CACHE_TTL = 7200
    
    # Sentiment analysis sources
    SOURCE_LOCAL = 'local'
    SOURCE_TWITTER = 'twitter'
    SOURCE_REDDIT = 'reddit'
    SOURCE_EXTERNAL_API = 'external_api'
    
    def __init__(self, 
                api_key: Optional[str] = None, 
                api_secret: Optional[str] = None,
                twitter_bearer_token: Optional[str] = None,
                reddit_client_id: Optional[str] = None,
                reddit_client_secret: Optional[str] = None,
                external_api_url: Optional[str] = None,
                cache_ttl: Optional[int] = None):
        """
        Initialize the sentiment analysis client.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            twitter_bearer_token: Twitter API bearer token
            reddit_client_id: Reddit API client ID
            reddit_client_secret: Reddit API client secret
            external_api_url: URL for external sentiment analysis API
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(api_key, cache_ttl)
        self.api_secret = api_secret
        self.twitter_bearer_token = twitter_bearer_token
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
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
                    user_agent="crypto_sentiment_analyzer/1.0"
                )
                logger.info("Reddit client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {str(e)}")
    
    def get_data(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Get sentiment data for a query.
        
        Args:
            query: Query string (e.g., "bitcoin", "ethereum")
            **kwargs: Additional parameters
                - source: Sentiment source (local, twitter, reddit, external_api)
                - limit: Maximum number of items to analyze
                - days: Number of days to look back
                
        Returns:
            Sentiment data as a dictionary
        """
        source = kwargs.get('source', self.SOURCE_LOCAL)
        limit = kwargs.get('limit', 100)
        days = kwargs.get('days', 7)
        
        # Generate cache key
        cache_key = f"sentiment_{source}_{query}_{limit}_{days}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Get sentiment data based on source
        if source == self.SOURCE_TWITTER:
            sentiment_data = self._get_twitter_sentiment(query, limit, days)
        elif source == self.SOURCE_REDDIT:
            sentiment_data = self._get_reddit_sentiment(query, limit, days)
        elif source == self.SOURCE_EXTERNAL_API:
            sentiment_data = self._get_external_api_sentiment(query, limit, days)
        else:
            # Default to local sentiment analysis
            sentiment_data = self._get_local_sentiment(query, limit, days)
        
        # Cache the result
        self._cache_result(cache_key, sentiment_data)
        
        return sentiment_data
    
    def _get_local_sentiment(self, query: str, limit: int, days: int) -> Dict[str, Any]:
        """
        Perform local sentiment analysis using TextBlob.
        
        Args:
            query: Query string
            limit: Maximum number of items to analyze
            days: Number of days to look back
            
        Returns:
            Sentiment data as a dictionary
        """
        if not TEXTBLOB_AVAILABLE:
            logger.warning("TextBlob is not available. Using simulated sentiment.")
            return self._get_simulated_sentiment(query)
        
        # Since we don't have a source of text to analyze locally,
        # we'll use a combination of the query and some common phrases
        # This is just for demonstration purposes
        phrases = [
            f"{query} is a great investment",
            f"{query} has a lot of potential",
            f"{query} is the future of finance",
            f"{query} is overvalued",
            f"{query} is a risky investment",
            f"{query} might crash soon",
            f"I'm bullish on {query}",
            f"I'm bearish on {query}",
            f"{query} has strong fundamentals",
            f"{query} lacks real-world adoption"
        ]
        
        # Analyze sentiment for each phrase
        sentiments = []
        for phrase in phrases:
            blob = TextBlob(phrase)
            polarity = blob.sentiment.polarity  # -1.0 to 1.0
            subjectivity = blob.sentiment.subjectivity  # 0.0 to 1.0
            
            # Map polarity to sentiment category
            if polarity > 0.3:
                sentiment = 'positive'
            elif polarity < -0.3:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            sentiments.append({
                'text': phrase,
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity
            })
        
        # Calculate overall sentiment
        total_polarity = sum(s['polarity'] for s in sentiments)
        avg_polarity = total_polarity / len(sentiments) if sentiments else 0
        
        # Map average polarity to sentiment percentages
        if avg_polarity > 0:
            positive_pct = 0.5 + (avg_polarity / 2)  # 0.5 to 1.0
            negative_pct = 1 - positive_pct - 0.1  # 0.0 to 0.4
            neutral_pct = 0.1  # Fixed at 10%
        else:
            negative_pct = 0.5 + (abs(avg_polarity) / 2)  # 0.5 to 1.0
            positive_pct = 1 - negative_pct - 0.1  # 0.0 to 0.4
            neutral_pct = 0.1  # Fixed at 10%
        
        return {
            'query': query,
            'source': self.SOURCE_LOCAL,
            'sentiment': {
                'positive': round(positive_pct, 2),
                'negative': round(negative_pct, 2),
                'neutral': round(neutral_pct, 2)
            },
            'sentiment_ratio': round(positive_pct / max(negative_pct, 0.01), 2),
            'samples': sentiments,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_twitter_sentiment(self, query: str, limit: int, days: int) -> Dict[str, Any]:
        """
        Get sentiment data from Twitter.
        
        Args:
            query: Query string
            limit: Maximum number of tweets to analyze
            days: Number of days to look back
            
        Returns:
            Sentiment data as a dictionary
        """
        if not TWITTER_AVAILABLE or not self.twitter_client:
            logger.warning("Twitter API is not available. Using simulated sentiment.")
            return self._get_simulated_sentiment(query, source=self.SOURCE_TWITTER)
        
        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(days=days)
            
            # Search for tweets
            tweets = []
            for tweet in tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=f"{query} -is:retweet lang:en",
                max_results=100,
                start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                tweet_fields=['created_at', 'public_metrics']
            ).flatten(limit=limit):
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'like_count': tweet.public_metrics['like_count']
                })
            
            # Analyze sentiment for each tweet
            sentiments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for tweet in tweets:
                if TEXTBLOB_AVAILABLE:
                    # Use TextBlob for sentiment analysis
                    blob = TextBlob(tweet['text'])
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity
                    
                    # Map polarity to sentiment category
                    if polarity > 0.3:
                        sentiment = 'positive'
                        positive_count += 1
                    elif polarity < -0.3:
                        sentiment = 'negative'
                        negative_count += 1
                    else:
                        sentiment = 'neutral'
                        neutral_count += 1
                else:
                    # Simple keyword-based sentiment analysis as fallback
                    text = tweet['text'].lower()
                    positive_keywords = ['bullish', 'moon', 'great', 'good', 'buy', 'up', 'gain', 'profit', 'win', 'success']
                    negative_keywords = ['bearish', 'crash', 'bad', 'sell', 'down', 'loss', 'fail', 'scam', 'risk', 'dump']
                    
                    positive_matches = sum(1 for keyword in positive_keywords if keyword in text)
                    negative_matches = sum(1 for keyword in negative_keywords if keyword in text)
                    
                    if positive_matches > negative_matches:
                        sentiment = 'positive'
                        polarity = 0.5
                        positive_count += 1
                    elif negative_matches > positive_matches:
                        sentiment = 'negative'
                        polarity = -0.5
                        negative_count += 1
                    else:
                        sentiment = 'neutral'
                        polarity = 0
                        neutral_count += 1
                    
                    subjectivity = 0.5  # Default subjectivity
                
                sentiments.append({
                    'text': tweet['text'],
                    'sentiment': sentiment,
                    'polarity': polarity,
                    'subjectivity': subjectivity,
                    'created_at': tweet['created_at'],
                    'platform': 'Twitter'
                })
            
            # Calculate sentiment percentages
            total_count = len(sentiments)
            if total_count > 0:
                positive_pct = positive_count / total_count
                negative_pct = negative_count / total_count
                neutral_pct = neutral_count / total_count
            else:
                positive_pct = 0.33
                negative_pct = 0.33
                neutral_pct = 0.34
            
            return {
                'query': query,
                'source': self.SOURCE_TWITTER,
                'sentiment': {
                    'positive': round(positive_pct, 2),
                    'negative': round(negative_pct, 2),
                    'neutral': round(neutral_pct, 2)
                },
                'sentiment_ratio': round(positive_pct / max(negative_pct, 0.01), 2),
                'samples': sentiments[:10],  # Include only a few samples
                'total_analyzed': total_count,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error getting Twitter sentiment: {str(e)}")
            return self._get_simulated_sentiment(query, source=self.SOURCE_TWITTER)
    
    def _get_reddit_sentiment(self, query: str, limit: int, days: int) -> Dict[str, Any]:
        """
        Get sentiment data from Reddit.
        
        Args:
            query: Query string
            limit: Maximum number of posts/comments to analyze
            days: Number of days to look back
            
        Returns:
            Sentiment data as a dictionary
        """
        if not REDDIT_AVAILABLE or not self.reddit_client:
            logger.warning("Reddit API is not available. Using simulated sentiment.")
            return self._get_simulated_sentiment(query, source=self.SOURCE_REDDIT)
        
        try:
            # Search for submissions
            subreddits = ['CryptoCurrency', 'CryptoMarkets', query.lower()]
            submissions = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit_client.subreddit(subreddit_name)
                    for submission in subreddit.search(query, sort='new', time_filter='week', limit=limit//3):
                        created_time = datetime.fromtimestamp(submission.created_utc)
                        if (datetime.now() - created_time).days <= days:
                            submissions.append({
                                'id': submission.id,
                                'title': submission.title,
                                'text': submission.selftext,
                                'created_at': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'score': submission.score,
                                'num_comments': submission.num_comments,
                                'url': submission.url
                            })
                except Exception as e:
                    logger.warning(f"Error searching subreddit {subreddit_name}: {str(e)}")
                    continue
            
            # Analyze sentiment for each submission
            sentiments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for submission in submissions:
                text = f"{submission['title']} {submission['text']}"
                
                if TEXTBLOB_AVAILABLE:
                    # Use TextBlob for sentiment analysis
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity
                    
                    # Map polarity to sentiment category
                    if polarity > 0.3:
                        sentiment = 'positive'
                        positive_count += 1
                    elif polarity < -0.3:
                        sentiment = 'negative'
                        negative_count += 1
                    else:
                        sentiment = 'neutral'
                        neutral_count += 1
                else:
                    # Simple keyword-based sentiment analysis as fallback
                    text_lower = text.lower()
                    positive_keywords = ['bullish', 'moon', 'great', 'good', 'buy', 'up', 'gain', 'profit', 'win', 'success']
                    negative_keywords = ['bearish', 'crash', 'bad', 'sell', 'down', 'loss', 'fail', 'scam', 'risk', 'dump']
                    
                    positive_matches = sum(1 for keyword in positive_keywords if keyword in text_lower)
                    negative_matches = sum(1 for keyword in negative_keywords if keyword in text_lower)
                    
                    if positive_matches > negative_matches:
                        sentiment = 'positive'
                        polarity = 0.5
                        positive_count += 1
                    elif negative_matches > positive_matches:
                        sentiment = 'negative'
                        polarity = -0.5
                        negative_count += 1
                    else:
                        sentiment = 'neutral'
                        polarity = 0
                        neutral_count += 1
                    
                    subjectivity = 0.5  # Default subjectivity
                
                sentiments.append({
                    'text': submission['title'],
                    'sentiment': sentiment,
                    'polarity': polarity,
                    'subjectivity': subjectivity,
                    'created_at': submission['created_at'],
                    'platform': 'Reddit'
                })
            
            # Calculate sentiment percentages
            total_count = len(sentiments)
            if total_count > 0:
                positive_pct = positive_count / total_count
                negative_pct = negative_count / total_count
                neutral_pct = neutral_count / total_count
            else:
                positive_pct = 0.33
                negative_pct = 0.33
                neutral_pct = 0.34
            
            return {
                'query': query,
                'source': self.SOURCE_REDDIT,
                'sentiment': {
                    'positive': round(positive_pct, 2),
                    'negative': round(negative_pct, 2),
                    'neutral': round(neutral_pct, 2)
                },
                'sentiment_ratio': round(positive_pct / max(negative_pct, 0.01), 2),
                'samples': sentiments[:10],  # Include only a few samples
                'total_analyzed': total_count,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment: {str(e)}")
            return self._get_simulated_sentiment(query, source=self.SOURCE_REDDIT)
    
    def _get_external_api_sentiment(self, query: str, limit: int, days: int) -> Dict[str, Any]:
        """
        Get sentiment data from an external API.
        
        Args:
            query: Query string
            limit: Maximum number of items to analyze
            days: Number of days to look back
            
        Returns:
            Sentiment data as a dictionary
        """
        if not self.external_api_url:
            logger.warning("External API URL is not set. Using simulated sentiment.")
            return self._get_simulated_sentiment(query, source=self.SOURCE_EXTERNAL_API)
        
        try:
            # Make request to external API
            response = self.make_request(
                url=self.external_api_url,
                method='GET',
                params={
                    'query': query,
                    'limit': limit,
                    'days': days
                },
                cache_key=f"external_sentiment_{query}_{limit}_{days}"
            )
            
            # Process response
            if 'sentiment' in response:
                return response
            else:
                logger.warning(f"Unexpected response format from external API: {response}")
                return self._get_simulated_sentiment(query, source=self.SOURCE_EXTERNAL_API)
            
        except Exception as e:
            logger.error(f"Error getting external API sentiment: {str(e)}")
            return self._get_simulated_sentiment(query, source=self.SOURCE_EXTERNAL_API)
    
    def _get_simulated_sentiment(self, query: str, source: str = SOURCE_LOCAL) -> Dict[str, Any]:
        """
        Generate simulated sentiment data.
        
        Args:
            query: Query string
            source: Sentiment source
            
        Returns:
            Simulated sentiment data as a dictionary
        """
        # Map well-known coins to fixed sentiment values for consistency
        known_coins = {
            'bitcoin': {'positive': 0.65, 'negative': 0.15, 'neutral': 0.20},
            'ethereum': {'positive': 0.60, 'negative': 0.20, 'neutral': 0.20},
            'binancecoin': {'positive': 0.55, 'negative': 0.25, 'neutral': 0.20},
            'ripple': {'positive': 0.50, 'negative': 0.30, 'neutral': 0.20},
            'cardano': {'positive': 0.55, 'negative': 0.25, 'neutral': 0.20},
            'solana': {'positive': 0.60, 'negative': 0.20, 'neutral': 0.20},
            'polkadot': {'positive': 0.50, 'negative': 0.25, 'neutral': 0.25},
            'dogecoin': {'positive': 0.70, 'negative': 0.20, 'neutral': 0.10},
            'shiba-inu': {'positive': 0.65, 'negative': 0.25, 'neutral': 0.10},
        }
        
        # Check if query matches any known coin
        query_lower = query.lower()
        sentiment = None
        for coin, values in known_coins.items():
            if coin in query_lower or query_lower in coin:
                sentiment = values
                break
        
        # Generate random sentiment if not a known coin
        if not sentiment:
            positive = round(0.4 + (hash(query) % 100) / 500, 2)  # 0.4 to 0.6
            negative = round(0.4 - (hash(query) % 100) / 500, 2)  # 0.2 to 0.4
            neutral = round(1 - positive - negative, 2)  # 0.0 to 0.4
            sentiment = {'positive': positive, 'negative': negative, 'neutral': neutral}
        
        # Generate sample posts
        samples = []
        coin_name = query.replace('-', ' ').title()
        
        # Templates for different sentiment categories
        positive_templates = [
            f"{coin_name} looking bullish today! 🚀",
            f"Just bought more {coin_name}, feeling good about this investment!",
            f"The {coin_name} community is growing stronger every day.",
            f"New partnerships for {coin_name} are really promising.",
            f"{coin_name} technical analysis shows strong support levels."
        ]
        
        negative_templates = [
            f"Not sure about {coin_name} right now, might sell soon.",
            f"{coin_name} price action looks concerning.",
            f"Too much hype around {coin_name}, be careful.",
            f"The {coin_name} team missed another deadline...",
            f"Regulatory concerns might impact {coin_name} negatively."
        ]
        
        neutral_templates = [
            f"Interesting developments in the {coin_name} ecosystem.",
            f"Anyone following the {coin_name} updates?",
            f"How does {coin_name} compare to other similar projects?",
            f"What's the consensus on {coin_name} for long-term holding?",
            f"New to {coin_name}, still researching."
        ]
        
        # Generate posts based on sentiment distribution
        total_samples = 10
        positive_count = round(total_samples * sentiment['positive'])
        negative_count = round(total_samples * sentiment['negative'])
        neutral_count = total_samples - positive_count - negative_count
        
        # Ensure at least one of each type if possible
        if positive_count == 0 and sentiment['positive'] > 0:
            positive_count = 1
            if neutral_count > 1:
                neutral_count -= 1
            elif negative_count > 1:
                negative_count -= 1
                
        if negative_count == 0 and sentiment['negative'] > 0:
            negative_count = 1
            if neutral_count > 1:
                neutral_count -= 1
            elif positive_count > 1:
                positive_count -= 1
        
        # Generate positive samples
        for i in range(positive_count):
            text = positive_templates[i % len(positive_templates)]
            samples.append({
                'text': text,
                'sentiment': 'positive',
                'polarity': 0.7,
                'subjectivity': 0.6,
                'created_at': (datetime.now() - timedelta(hours=i*3)).strftime('%Y-%m-%d %H:%M:%S'),
                'platform': source.capitalize()
            })
        
        # Generate negative samples
        for i in range(negative_count):
            text = negative_templates[i % len(negative_templates)]
            samples.append({
                'text': text,
                'sentiment': 'negative',
                'polarity': -0.7,
                'subjectivity': 0.6,
                'created_at': (datetime.now() - timedelta(hours=i*3+1)).strftime('%Y-%m-%d %H:%M:%S'),
                'platform': source.capitalize()
            })
        
        # Generate neutral samples
        for i in range(neutral_count):
            text = neutral_templates[i % len(neutral_templates)]
            samples.append({
                'text': text,
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.3,
                'created_at': (datetime.now() - timedelta(hours=i*3+2)).strftime('%Y-%m-%d %H:%M:%S'),
                'platform': source.capitalize()
            })
        
        # Sort by created_at (newest first)
        samples.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            'query': query,
            'source': source,
            'sentiment': sentiment,
            'sentiment_ratio': round(sentiment['positive'] / max(sentiment['negative'], 0.01), 2),
            'samples': samples,
            'total_analyzed': len(samples),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'simulated': True
        }
    
    def get_combined_sentiment(self, query: str, sources: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Get combined sentiment data from multiple sources.
        
        Args:
            query: Query string
            sources: List of sources to use (defaults to all available)
            **kwargs: Additional parameters
                
        Returns:
            Combined sentiment data as a dictionary
        """
        if sources is None:
            sources = [self.SOURCE_LOCAL]
            if TWITTER_AVAILABLE and self.twitter_client:
                sources.append(self.SOURCE_TWITTER)
            if REDDIT_AVAILABLE and self.reddit_client:
                sources.append(self.SOURCE_REDDIT)
            if self.external_api_url:
                sources.append(self.SOURCE_EXTERNAL_API)
        
        # Generate cache key
        cache_key = f"combined_sentiment_{query}_{'-'.join(sources)}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Get sentiment data from each source
        sentiment_data = {}
        for source in sources:
            sentiment_data[source] = self.get_data(query, source=source, **kwargs)
        
        # Calculate combined sentiment
        positive_sum = sum(data['sentiment']['positive'] for data in sentiment_data.values())
        negative_sum = sum(data['sentiment']['negative'] for data in sentiment_data.values())
        neutral_sum = sum(data['sentiment']['neutral'] for data in sentiment_data.values())
        
        total_sources = len(sentiment_data)
        if total_sources > 0:
            combined_sentiment = {
                'positive': round(positive_sum / total_sources, 2),
                'negative': round(negative_sum / total_sources, 2),
                'neutral': round(neutral_sum / total_sources, 2)
            }
            sentiment_ratio = round(combined_sentiment['positive'] / max(combined_sentiment['negative'], 0.01), 2)
        else:
            combined_sentiment = {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
            sentiment_ratio = 1.0
        
        # Combine samples from all sources
        all_samples = []
        for source, data in sentiment_data.items():
            for sample in data.get('samples', []):
                all_samples.append(sample)
        
        # Sort by created_at (newest first)
        all_samples.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Determine trend
        trend = 'stable'
        if sentiment_ratio > 2.0:
            trend = 'improving'
        elif sentiment_ratio < 0.5:
            trend = 'declining'
        
        result = {
            'query': query,
            'sources': sources,
            'sentiment': combined_sentiment,
            'sentiment_ratio': sentiment_ratio,
            'trend': trend,
            'trend_value': 0.1 if trend == 'improving' else (-0.1 if trend == 'declining' else 0),
            'samples': all_samples[:10],  # Include only a few samples
            'source_data': sentiment_data,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Cache the result
        self._cache_result(cache_key, result)
        
        return result
