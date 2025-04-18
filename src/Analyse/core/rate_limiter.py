"""
Rate limiter implementation that follows SOLID principles.
Separates concerns into distinct components.
"""
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from .interfaces import IRateLimiter


class BaseRateLimiter(IRateLimiter):
    """
    Base rate limiter implementation.
    Follows SOLID principles:
    - Single Responsibility: Handles rate limiting
    - Open/Closed: Can be extended with new rate limiting strategies
    - Interface Segregation: Implements IRateLimiter interface
    - Dependency Inversion: Can be replaced with other implementations
    """
    
    def __init__(self, rate_limit: int = 1.5):
        """
        Initialize the rate limiter
        
        Args:
            rate_limit: Time in seconds between requests
        """
        self.rate_limit = rate_limit
        self._last_request_time = 0
    
    def wait_if_needed(self) -> None:
        """
        Wait if rate limit would be exceeded
        
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        current_time = time.time()
        if current_time - self._last_request_time < self.rate_limit:
            wait_time = self.rate_limit - (current_time - self._last_request_time)
            time.sleep(wait_time)
        self._last_request_time = time.time()
    
    def set_rate_limit(self, limit: int) -> None:
        """Set the rate limit in seconds"""
        self.rate_limit = limit


class CoinGeckoRateLimiter(BaseRateLimiter):
    """Rate limiter specifically for CoinGecko API"""
    
    def __init__(self):
        # CoinGecko free tier rate limit is 10 requests/minute
        # We use 1.5s delay to stay well under this limit
        super().__init__(1.5)
    
    def handle_error(self, error: Exception) -> None:
        """Handle rate limit errors from CoinGecko API"""
        if hasattr(error, 'response') and error.response.status_code == 429:
            # If we get rate limited, increase the delay
            self.rate_limit *= 2
            self._logger.warning(f"Rate limit exceeded. Increasing delay to {self.rate_limit}s")
