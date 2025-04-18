"""
Base API client for making requests to external APIs.
"""
import logging
import time
import json
import requests
from typing import Dict, Any, Optional, Union, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAPIClient(ABC):
    """
    Abstract base class for API clients.
    Provides common functionality for making API requests, handling rate limits,
    caching responses, and error handling.
    """
    
    # Default cache TTL (1 hour)
    CACHE_TTL = 3600
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: Optional[int] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: API key for authentication (if required)
            cache_ttl: Cache time-to-live in seconds (defaults to CACHE_TTL)
        """
        self.api_key = api_key
        self.cache_ttl = cache_ttl or self.CACHE_TTL
        self.cache = {}
        self.cache_expiry = {}
        self.session = requests.Session()
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        
    def make_request(self, 
                    url: str, 
                    method: str = 'GET', 
                    params: Optional[Dict[str, Any]] = None,
                    data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    auth: Optional[Any] = None,
                    timeout: int = 30,
                    cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an API request with caching and rate limit handling.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            headers: HTTP headers
            auth: Authentication
            timeout: Request timeout in seconds
            cache_key: Key to use for caching (if None, caching is disabled)
            
        Returns:
            Response data as a dictionary
        """
        # Check cache if cache_key is provided
        if cache_key and self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]
        
        # Check rate limits before making request
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 0:
            wait_time = max(0, self.rate_limit_reset - time.time())
            if wait_time > 0:
                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f} seconds.")
                time.sleep(wait_time)
        
        # Prepare headers
        request_headers = {'Accept': 'application/json'}
        if self.api_key:
            request_headers['Authorization'] = f'Bearer {self.api_key}'
        if headers:
            request_headers.update(headers)
        
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                auth=auth,
                timeout=timeout
            )
            
            # Update rate limit information if available
            self._update_rate_limits(response)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            if response.content:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON response: {response.text[:100]}...")
                    response_data = {'text': response.text}
            else:
                response_data = {}
            
            # Cache response if cache_key is provided
            if cache_key:
                self._cache_result(cache_key, response_data)
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text[:200]}...")
            raise
    
    def _update_rate_limits(self, response: requests.Response) -> None:
        """
        Update rate limit information from response headers.
        
        Args:
            response: Response object
        """
        # Different APIs use different header names for rate limits
        # This is a generic implementation that should be overridden by subclasses
        remaining_header = response.headers.get('X-RateLimit-Remaining')
        reset_header = response.headers.get('X-RateLimit-Reset')
        
        if remaining_header:
            try:
                self.rate_limit_remaining = int(remaining_header)
            except (ValueError, TypeError):
                pass
                
        if reset_header:
            try:
                self.rate_limit_reset = int(reset_header)
            except (ValueError, TypeError):
                pass
    
    def _is_cache_valid(self, key: str) -> bool:
        """
        Check if a cached item is still valid.
        
        Args:
            key: Cache key
            
        Returns:
            True if cache is valid, False otherwise
        """
        if key not in self.cache or key not in self.cache_expiry:
            return False
        return time.time() < self.cache_expiry.get(key, 0)
    
    def _cache_result(self, key: str, result: Any, ttl: Optional[int] = None) -> Any:
        """
        Cache a result with expiration time.
        
        Args:
            key: Cache key
            result: Result to cache
            ttl: Time to live in seconds (defaults to self.cache_ttl)
            
        Returns:
            The cached result
        """
        if ttl is None:
            ttl = self.cache_ttl
        self.cache[key] = result
        self.cache_expiry[key] = time.time() + ttl
        return result
    
    @abstractmethod
    def get_data(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Get data from the API.
        
        Args:
            query: Query string or identifier
            **kwargs: Additional parameters
            
        Returns:
            Response data as a dictionary
        """
        pass
