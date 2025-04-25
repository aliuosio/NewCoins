import os
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file from the project root

def is_cache_enabled():
    """
    Returns True if caching is enabled via .env, False otherwise.
    """
    return os.getenv("API_CACHE_ENABLED", "false").lower() == "true"

def get_cache_duration():
    """
    Returns the cache duration in seconds from .env, or default value (3600) if not set.
    """
    try:
        duration = int(os.getenv("API_CACHE_DURATION", "3600"))
        return max(1, duration)  # Ensure minimum of 1 second
    except (ValueError, TypeError):
        # If the value is not a valid integer, return the default
        return 3600
