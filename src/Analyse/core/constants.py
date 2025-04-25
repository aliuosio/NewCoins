"""
Constants and configuration parameters for the Analyse module.
"""
import os

# API Configuration
DEFAULT_CURRENCY = 'usd'
DEFAULT_DAYS = 1
MAX_LOG_CONTENT_LENGTH = 500  # Maximum length of API response to log

# Volume Data Configuration
MINIMUM_VALID_VOLUME = 0.0  # Minimum volume to be considered valid
MARKET_CHART_MIN_DATA_POINTS = 2  # Minimum number of data points needed for market chart volume calculation

# Cache Configuration
DEFAULT_CACHE_DURATION = 3600  # Default cache duration in seconds
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'cache')

# Environment Variables
ENV_CACHE_DIR = os.getenv('API_CACHE_DIR', DEFAULT_CACHE_DIR)
ENV_CACHE_DURATION = int(os.getenv('COINGECKO_CACHE_DURATION', str(DEFAULT_CACHE_DURATION)))
