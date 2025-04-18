#!/usr/bin/env python3
"""
Google Trends Indicator - Analyzes search interest for a cryptocurrency.
Replicates functionality from the old Indicator_Old version.
"""
import logging
import time
import random
import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

# Import PyTrends safely
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider # Assuming IDataProvider is in interfaces.py

logger = logging.getLogger(__name__)

class GoogleTrendsIndicator(BaseIndicator):
    """
    Analyzes Google search trends for a cryptocurrency, replicating old logic.

    Uses PyTrends library if available, otherwise falls back to simulation.
    Includes caching and specific scoring based on trend direction/intensity.

    Scoring (max 5 points): Based on trend direction and intensity.
    """

    # Override cache TTL for Google Trends (6 hours - less frequent updates)
    CACHE_TTL = 6 * 3600

    def __init__(self, data_provider: IDataProvider):
        # Max score is 5.0 as per the old indicator
        super().__init__(
            "google_trends",
            5.0,
            data_provider
        )
        if not PYTRENDS_AVAILABLE:
            logger.warning("Pytrends library not found. GoogleTrendsIndicator will run in simulation mode only.")
        
        # Set up cache directory
        self._cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'cache', 'google_trends')
        os.makedirs(self._cache_dir, exist_ok=True)
        self._cache_duration = 3600  # Cache duration in seconds (1 hour)
        logger.info(f"Using Google Trends cache directory: {self._cache_dir} with {self._cache_duration}s duration")
        
        # Rate limiting settings
        self._last_request_time = 0
        self._request_interval = 60  # Minimum interval between requests in seconds (1 minute)
        self._max_retries = 5
        self._base_delay = 2.0  # Start with 2 seconds delay
        self._max_delay = 60  # Maximum delay of 60 seconds
        # Note: The old version mapped this to 'google_trends' in the DB.

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the Google Trends score using cached data only.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id).

        Returns:
            Dictionary with score and detailed trends metrics.
        """
        coin_id = data.get('id') # Assumes data provider returns coin_id like 'bitcoin'
        if not coin_id:
            coin_id = symbol.lower()

        # Generate search term for Google Trends
        search_term = coin_id.replace('-', ' ').title() # e.g., "bitcoin" -> "Bitcoin"

        # Check if we have cached data
        cached_data = self._get_from_cache(search_term)
        if cached_data:
            logger.info(f"Found cached Google Trends data for {search_term}")
            # We have cached data, calculate the score and return it
            score = self._calculate_indicator_score(cached_data)
            cached_data['score'] = score
            return cached_data
        
        # No cached data available
        logger.info(f"No cached Google Trends data found for {search_term}. Attempting to populate cache...")
        
        # Try to populate the cache with real data
        if self._populate_cache(symbol, data):
            logger.info(f"Successfully populated cache for {search_term}")
            # Re-fetch from cache now that it's populated
            cached_data = self._get_from_cache(search_term)
            if cached_data:
                score = self._calculate_indicator_score(cached_data)
                cached_data['score'] = score
                return cached_data
        
        # If we still don't have data after trying to populate cache, return minimal data
        logger.info(f"Failed to get Google Trends data for {search_term}. Returning minimal data.")
        minimal_data = {
            'search_term': search_term,
            'simulated': True,  # Mark as simulated
            'trend_data': {
                'current_interest': 0,
                'previous_interest': 0,
                'percent_change': 0,
                'trend_direction': 0,
                'trend_intensity': 0,
                'trend_status': 'No Data Available'
            },
            'interest_history': [],
            'related_queries': [],
            'no_data': True,  # Flag to indicate no data is available
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Calculate a minimal score
        score = 0.0  # No data means zero score
        minimal_data['score'] = score
        
        return minimal_data
        
    def _populate_cache(self, symbol: str, data: Dict[str, Any]) -> bool:
        """
        Populate the cache with Google Trends data.
        This method should be called separately to fill the cache.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id).
            
        Returns:
            True if cache was successfully populated, False otherwise.
        """
        coin_id = data.get('id') # Assumes data provider returns coin_id like 'bitcoin'
        if not coin_id:
            coin_id = symbol.lower()

        # Generate search term for Google Trends
        search_term = coin_id.replace('-', ' ').title() # e.g., "bitcoin" -> "Bitcoin"
        
        # Check if PyTrends is available
        if not PYTRENDS_AVAILABLE:
            logger.error("PyTrends library is not installed. Cannot populate cache.")
            return False

        # Fetch real data
        logger.info(f"Fetching real Google Trends data for {search_term} to populate cache")
        try:
            processed_data = self._fetch_real_trends_data(search_term, coin_id)
            
            if not processed_data:
                logger.error(f"Failed to fetch Google Trends data for {search_term}")
                return False

            # Cache the processed data
            self._cache_response(search_term, processed_data)
            logger.info(f"Successfully cached Google Trends data for {search_term}")
            return True
        except Exception as e:
            logger.error(f"Error populating cache for {search_term}: {str(e)}")
            return False

    def _fetch_real_trends_data(self, search_term: str, coin_id: str) -> Dict[str, Any]:
        """Fetch real Google Trends data using PyTrends with enhanced retry logic."""
        if not PYTRENDS_AVAILABLE:
            raise ImportError("PyTrends library is not installed.")

        # Respect rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._request_interval:
            logger.debug(f"Waiting {self._request_interval - time_since_last:.1f} seconds to respect rate limits")
            time.sleep(self._request_interval - time_since_last)

        # There's a compatibility issue with the PyTrends library and newer versions of the requests library
        # The library uses 'method_whitelist' which has been renamed to 'allowed_methods' in newer versions
        # We'll try multiple approaches to handle this issue
        
        # First, try to monkey patch the urllib3.util.Retry class
        try:
            from urllib3.util import Retry
            if not hasattr(Retry, 'method_whitelist') and hasattr(Retry, 'allowed_methods'):
                # Add method_whitelist as an alias for allowed_methods
                Retry.method_whitelist = Retry.allowed_methods
                logger.debug("Patched Retry class to add method_whitelist alias")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to patch Retry class: {e}")
        
        # Second, try to monkey patch the pytrends.request module directly
        try:
            import pytrends.request
            original_get_data = pytrends.request.TrendReq._get_data
            
            def patched_get_data(self, url, method=None, trim_chars=0, **kwargs):
                """Patched version of _get_data that doesn't use method_whitelist"""
                return original_get_data(self, url, method, trim_chars, **kwargs)
            
            # Replace the method
            pytrends.request.TrendReq._get_data = patched_get_data
            logger.debug("Patched pytrends.request.TrendReq._get_data")
        except Exception as e:
            logger.warning(f"Failed to patch pytrends.request.TrendReq._get_data: {e}")
        
        # Fix the FutureWarning about fillna(False) by monkey patching pandas DataFrame methods
        try:
            import pandas as pd
            # Set pandas option to avoid the FutureWarning
            pd.set_option('future.no_silent_downcasting', True)
            
            logger.debug("Set pandas option to fix FutureWarning about fillna")
        except Exception as e:
            logger.warning(f"Failed to set pandas option: {e}")
        
        # Enhanced retry logic with exponential backoff
        for attempt in range(self._max_retries):
            try:
                # Now create the PyTrends instance with minimal parameters to reduce chance of errors
                pytrends = TrendReq(hl='en-US', tz=360)
                kw_list = [search_term, f"{search_term} crypto"] # Use base term and crypto-specific term
                timeframe = 'now 7-d'  # Last 7 days

                logger.debug(f"Attempt {attempt + 1}/{self._max_retries}: Requesting Google Trends for: {kw_list} timeframe: {timeframe}")
                pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='', gprop='')

                interest_over_time_df = pytrends.interest_over_time()
                
                if interest_over_time_df.empty or len(interest_over_time_df) < 2:
                    logger.warning(f"Insufficient Google Trends data points found for {search_term}")
                    raise ValueError(f"Insufficient Google Trends data points for {search_term}")

                return self._process_interest_data(interest_over_time_df, search_term)

            except Exception as e:
                if attempt == self._max_retries - 1:  # Last attempt
                    logger.error(f"Failed to fetch Google Trends data after {self._max_retries} attempts: {e}")
                    raise
                else:
                    # Calculate delay with exponential backoff, capped at max_delay
                    delay = min(self._max_delay, self._base_delay * (2 ** attempt))
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)

        return None

    def _process_interest_data(self, interest_over_time_df, search_term):
        """Process Google Trends interest data and return formatted results."""
        # Process interest over time
        interest_history = []
        for date, row in interest_over_time_df.iterrows():
            # Combine interest from both search terms (take max or sum?) - Max seems reasonable
            interest_value = 0
            if search_term in row: interest_value = max(interest_value, row[search_term])
            if f"{search_term} crypto" in row: interest_value = max(interest_value, row[f"{search_term} crypto"])
            # Skip 'isPartial' column if present
            if 'isPartial' in row and row['isPartial']:
                logger.debug(f"Skipping partial data point for {date}")
                continue
            interest_history.append({'date': date.strftime('%Y-%m-%d'), 'value': interest_value})

        if len(interest_history) < 2:
            raise ValueError(f"Insufficient non-partial Google Trends data points for {search_term}")

        # Calculate trend metrics from real data
        current_interest = interest_history[-1]['value']
        # Use first point as previous for 7-day trend calculation
        previous_interest = interest_history[0]['value']

        percent_change = ((current_interest - previous_interest) / max(previous_interest, 1)) * 100 # Avoid div by zero
        trend_direction = max(-1.0, min(1.0, percent_change / 50)) # Scale change to -1 to 1 (50% change = full trend)
        trend_intensity = min(1.0, abs(percent_change) / 50) # Intensity based on magnitude of change

        # Generate related queries (simplified simulation)
        related_queries = self._generate_related_queries(search_term)

        return {
            'search_term': search_term,
            'simulated': False,  # Mark as real data
            'trend_data': {
                'current_interest': current_interest,
                'previous_interest': previous_interest,
                'percent_change': percent_change,
                'trend_direction': trend_direction,
                'trend_intensity': trend_intensity,
                'trend_status': 'Real Data Available'
            },
            'interest_history': interest_history,
            'related_queries': related_queries,
            'no_data': False,  # Flag to indicate data is available
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if len(interest_history) < 2:
            raise ValueError(f"Insufficient non-partial Google Trends data points for {search_term}")

        # Calculate trend metrics from real data
        current_interest = interest_history[-1]['value']
        # Use first point as previous for 7-day trend calculation
        previous_interest = interest_history[0]['value']

        percent_change = ((current_interest - previous_interest) / max(previous_interest, 1)) * 100 # Avoid div by zero
        trend_direction = max(-1.0, min(1.0, percent_change / 50)) # Scale change to -1 to 1 (50% change = full trend)
        trend_intensity = min(1.0, abs(percent_change) / 50) # Intensity based on magnitude of change

        # Generate related queries (simplified simulation)
        related_queries = self._generate_related_queries(search_term)

        return {
            'search_term': search_term,
            'simulated': False,
            'trend_data': {
                'current_interest': current_interest,
                'previous_interest': previous_interest,
                'percent_change': round(percent_change, 1),
                'trend_direction': round(trend_direction, 2),
                'trend_intensity': round(trend_intensity, 2),
                'trend_status': self._get_trend_status(trend_direction, trend_intensity)
            },
            'interest_history': interest_history,
            'related_queries': related_queries, # Using simulated ones for now
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }



    def _get_cache_key(self, search_term: str) -> str:
        """
        Generate a unique cache key for a search term
        
        Args:
            search_term: The search term to generate a key for
            
        Returns:
            Cache key string
        """
        # Create a hash of the search term to use as the cache key
        hash_obj = hashlib.md5(search_term.lower().encode())
        return hash_obj.hexdigest()
    
    def _get_from_cache(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if it exists and is not expired
        
        Args:
            search_term: Search term to get cached data for
            
        Returns:
            Cached data or None if not found or expired
        """
        cache_key = self._get_cache_key(search_term)
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            logger.debug(f"No cache file found for {search_term}")
            return None
        
        try:
            # Check if the cache file is expired
            file_modified_time = os.path.getmtime(cache_file)
            current_time = time.time()
            
            if current_time - file_modified_time > self._cache_duration:
                logger.debug(f"Cache for {search_term} is expired")
                return None
            
            # Read the cache file
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(f"Using cached Google Trends data for {search_term} (cached {int((current_time - file_modified_time) / 60)} minutes ago)")
            return cached_data
        except Exception as e:
            logger.warning(f"Error reading cache for {search_term}: {str(e)}")
            return None
    
    def _cache_response(self, search_term: str, data: Dict[str, Any]) -> None:
        """
        Cache the response data
        
        Args:
            search_term: Search term
            data: Data to cache
        """
        cache_key = self._get_cache_key(search_term)
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Cached Google Trends data for {search_term}")
        except Exception as e:
            logger.warning(f"Error caching data for {search_term}: {str(e)}")
    
    def _simulate_trends_data(self, search_term: str, coin_id: str) -> Dict[str, Any]:
        """
        Simulate Google Trends data when the API fails or is rate limited.
        
        This provides realistic fallback data based on the cryptocurrency's popularity.
        
        Args:
            search_term: The search term used (e.g., "Bitcoin")
            coin_id: The coin ID (e.g., "bitcoin")
            
        Returns:
            Dictionary with simulated trend data
        """
        logger.info(f"Simulating Google Trends data for {search_term}")
        
        # Generate realistic interest values based on the coin
        # Well-known coins get higher interest values
        base_interest = 0
        if coin_id.lower() in ['bitcoin', 'btc']:
            base_interest = 70  # Bitcoin has high interest
        elif coin_id.lower() in ['ethereum', 'eth']:
            base_interest = 50  # Ethereum has medium-high interest
        elif coin_id.lower() in ['dogecoin', 'doge', 'solana', 'sol', 'ripple', 'xrp']:
            base_interest = 30  # Popular altcoins have medium interest
        else:
            base_interest = 15  # Other coins have lower interest
        
        # Add some randomness to make it look realistic
        current_interest = max(0, min(100, base_interest + random.randint(-10, 10)))
        previous_interest = max(0, min(100, base_interest + random.randint(-15, 15)))
        
        # Generate a realistic trend history (7 days)
        interest_history = []
        today = datetime.now()
        for i in range(7):
            day = today - timedelta(days=6-i)  # Start 6 days ago
            # Generate a value that's somewhat close to the base interest
            daily_interest = max(0, min(100, base_interest + random.randint(-20, 20)))
            interest_history.append({
                'date': day.strftime('%Y-%m-%d'),
                'value': daily_interest
            })
        
        # Calculate trend metrics
        percent_change = ((current_interest - previous_interest) / max(previous_interest, 1)) * 100
        trend_direction = max(-1.0, min(1.0, percent_change / 50))  # Scale to -1 to 1
        trend_intensity = min(1.0, abs(percent_change) / 50)  # Scale to 0 to 1
        
        # Generate related queries
        related_queries = self._generate_related_queries(search_term)
        
        return {
            'search_term': search_term,
            'simulated': True,  # Mark as simulated data
            'trend_data': {
                'current_interest': current_interest,
                'previous_interest': previous_interest,
                'percent_change': round(percent_change, 1),
                'trend_direction': round(trend_direction, 2),
                'trend_intensity': round(trend_intensity, 2),
                'trend_status': self._get_trend_status(trend_direction, trend_intensity)
            },
            'interest_history': interest_history,
            'related_queries': related_queries,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def _get_trend_status(self, direction: float, intensity: float) -> str:
        """Determine the trend status based on direction and intensity (old logic)."""
        if direction >= 0.5:
            return "Strong Uptrend" if intensity >= 0.7 else ("Moderate Uptrend" if intensity >= 0.3 else "Slight Uptrend")
        elif direction > -0.2: # Changed from >= to > to make stable less likely on exact -0.2
             # Stable range includes small fluctuations around zero
             return "Stable" if intensity < 0.3 else ("Slight Uptrend" if direction > 0 else "Slight Downtrend")
        # elif direction >= -0.5: # Covered by Stable or Slight Downtrend below
        #     return "Slight Downtrend" if intensity >= 0.3 else "Minimal Downtrend" # Old logic was a bit complex here
        else: # direction < -0.2
            return "Strong Downtrend" if intensity >= 0.7 else ("Moderate Downtrend" if intensity >= 0.3 else "Slight Downtrend")


    def _generate_related_queries(self, search_term: str) -> List[str]:
        """Generate sample related queries (old logic)."""
        query_templates = [
            "{} price", "How to buy {}", "{} wallet", "{} news", "{} prediction",
            "{} chart", "Is {} a good investment", "{} vs ethereum", "{} vs bitcoin",
            "What is {}", "{} mining", "{} staking", "{} reddit", "{} twitter"
        ]
        num_queries = random.randint(4, 6)
        selected_templates = random.sample(query_templates, min(num_queries, len(query_templates)))
        return [template.format(search_term) for template in selected_templates]

    def _calculate_indicator_score(self, processed_data: Dict[str, Any]) -> float:
        """
        Calculate the final score based on Google Trends metrics (old logic).

        Args:
            processed_data: The dictionary returned by fetching/simulation.

        Returns:
            float: Score between 0 and self.max_score (5.0).
        """
        if not processed_data or 'trend_data' not in processed_data:
            return 0.0

        trend_data = processed_data['trend_data']
        trend_direction = trend_data.get('trend_direction', 0)
        trend_intensity = trend_data.get('trend_intensity', 0)
        percent_change = trend_data.get('percent_change', 0)

        # Base score from trend direction (-1 to 1) scaled to max_points (0-5)
        base_score = ((trend_direction + 1) / 2) * self.max_score

        # Adjust based on intensity (0-1) - higher intensity gives more weight to the base score
        adjusted_score = base_score * (0.7 + (trend_intensity * 0.3))

        # Bonus for significant recent positive change (old logic)
        if percent_change > 20:
            adjusted_score += 0.5
        elif percent_change > 10:
            adjusted_score += 0.25

        # Ensure score is within bounds (0 to max_score)
        score = max(0.0, min(adjusted_score, self.max_score))

        return round(score, 1)
