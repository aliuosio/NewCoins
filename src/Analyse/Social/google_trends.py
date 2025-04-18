#!/usr/bin/env python3
"""
Google Trends Indicator - Analyzes search interest for a cryptocurrency.
Replicates functionality from the old Indicator_Old version.
"""
import logging
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

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
        # Note: The old version mapped this to 'google_trends' in the DB.

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the Google Trends score using real data.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            data: Raw data from the data provider (contains coin_id).

        Returns:
            Dictionary with score and detailed trends metrics.
        """
        coin_id = data.get('id') # Assumes data provider returns coin_id like 'bitcoin'
        if not coin_id:
            coin_id = symbol.lower()
            logger.warning(f"Coin ID not found in data for {symbol}, using symbol '{coin_id}' as fallback.")
            # return self._create_error_response(symbol, "Coin ID missing in provided data")

        # Use coin_id for cache key and search term generation
        cache_key = f"trends_{coin_id}"
        search_term = coin_id.replace('-', ' ').title() # e.g., "bitcoin" -> "Bitcoin"

        # --- Caching Logic ---
        cached_data = self._get_cached_result(cache_key)
        if cached_data:
            logger.info(f"Using cached Google Trends data for {coin_id}")
            # Recalculate score from cached processed data
            score = self._calculate_indicator_score(cached_data)
            cached_data['score'] = score
            return cached_data
        # --- End Caching Logic ---

        # Check if PyTrends is available
        if not PYTRENDS_AVAILABLE:
            raise ImportError("PyTrends library is not installed. Install it with 'pip install pytrends'.")

        # Fetch real data
        logger.info(f"Fetching real Google Trends data for {search_term}")
        processed_data = self._fetch_real_trends_data(search_term, coin_id)
        
        if not processed_data:
            raise ValueError(f"Failed to fetch Google Trends data for {search_term}")

        # Calculate the final score from the processed data
        score = self._calculate_indicator_score(processed_data)
        processed_data['score'] = score # Add score to the dictionary

        # Cache the processed data
        self._cache_result(cache_key, processed_data)

        return processed_data

    def _fetch_real_trends_data(self, search_term: str, coin_id: str) -> Dict[str, Any]:
        """Fetch real Google Trends data using PyTrends."""
        if not PYTRENDS_AVAILABLE:
            raise ImportError("PyTrends library is not installed.")

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
        
        # Now create the PyTrends instance with minimal parameters to reduce chance of errors
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
        except Exception as e:
            logger.error(f"Failed to create PyTrends instance: {e}")
            raise
        kw_list = [search_term, f"{search_term} crypto"] # Use base term and crypto-specific term
        timeframe = 'now 7-d'  # Last 7 days

        logger.debug(f"Requesting Google Trends for: {kw_list} timeframe: {timeframe}")
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='', gprop='')

        interest_over_time_df = pytrends.interest_over_time()
        # related_queries_dict = pytrends.related_queries() # Fetching related queries can be slow/error-prone

        if interest_over_time_df.empty or len(interest_over_time_df) < 2:
             logger.warning(f"Insufficient Google Trends data points found for {search_term}")
             # Fallback to simulation within this function if needed, or raise error
             # For simplicity, we'll let the main _calculate handle fallback
             raise ValueError(f"Insufficient Google Trends data points for {search_term}")


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
