"""
Base data provider implementation that follows SOLID principles.
Separates concerns into distinct components.
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from .interfaces import IDataProvider, ICache, IRateLimiter, IApiRequester
from ..errors import DataProviderError


class BaseDataProvider(IDataProvider):
    """
    Abstract base class for all data providers.
    Implements common functionality while requiring subclasses to implement
    the specific data fetching logic.
    
    Follows SOLID principles:
    - Single Responsibility: Each component has one clear responsibility
    - Open/Closed: Can be extended with new providers without modifying existing code
    - Interface Segregation: Clear interfaces for each component
    - Dependency Inversion: Depends on abstractions, not concrete implementations
    """
    
    def __init__(self, 
                 name: str, 
                 cache: ICache, 
                 rate_limiter: IRateLimiter, 
                 api_requester: IApiRequester):
        """
        Initialize the data provider
        
        Args:
            name: Name of the data provider
            cache: Cache implementation
            rate_limiter: Rate limiter implementation
            api_requester: API request handler
        """
        self._name = name
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._api_requester = api_requester
        self._logger = logging.getLogger(f"data_provider.{name}")
    
    @property
    def name(self) -> str:
        """Get the name of the data provider"""
        return self._name
    
    def get_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get data for a specific cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Dictionary containing all relevant data
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(symbol)
            if cached_data := self._cache.get(cache_key):
                self._logger.debug(f"Cache hit for {symbol}")
                return cached_data
            
            # Get fresh data
            data = self._fetch_data(symbol)
            
            # Cache the result
            self._cache.set(cache_key, data, self._get_cache_ttl())
            
            return data
            
        except Exception as e:
            self._logger.error(f"Error getting data for {symbol}: {str(e)}")
            raise DataProviderError(f"Failed to get data for {symbol}: {str(e)}")
    
    @abstractmethod
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch the actual data from the source
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Dictionary with all relevant data
        """
        pass
    
    def _generate_cache_key(self, symbol: str) -> str:
        """Generate a unique cache key for the symbol"""
        return f"{self._name}_{symbol}"
    
    def _get_cache_ttl(self) -> int:
        """Get the cache time-to-live in seconds"""
        return 3600  # Default 1 hour


class CoinGeckoDataProvider(BaseDataProvider):
    """Data provider that fetches data from CoinGecko API"""
    
    def __init__(self, 
                 cache: ICache, 
                 rate_limiter: IRateLimiter, 
                 api_requester: IApiRequester):
        super().__init__("coingecko", cache, rate_limiter, api_requester)
    
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from CoinGecko API"""
        # Implementation will be moved here from the old provider
        pass
