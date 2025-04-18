"""
Core interfaces for the indicator system.
Following SOLID principles with clear interface segregation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Protocol


class IDataProvider(ABC):
    """Interface for data providers that fetch cryptocurrency data"""
    
    @abstractmethod
    def get_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get data for a specific cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary containing all relevant data for the cryptocurrency
        """
        pass


class IIndicator(ABC):
    """Interface for all indicators"""
    
    @abstractmethod
    def calculate(self, symbol: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate the indicator score for a given cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data to use for calculation (optional)
            
        Returns:
            Dictionary with calculation results
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the indicator"""
        pass
    
    @property
    @abstractmethod
    def max_score(self) -> float:
        """Get the maximum possible score for this indicator"""
        pass


class ICache(Protocol):
    """Interface for caching system"""
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data by key"""
        pass
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set data in cache with TTL"""
        pass
    
    def clear(self) -> None:
        """Clear all cached data"""
        pass


class IRateLimiter(Protocol):
    """Interface for rate limiting system"""
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded"""
        pass
    
    def set_rate_limit(self, limit: int) -> None:
        """Set the rate limit"""
        pass


class IApiRequester(Protocol):
    """Interface for API request handling"""
    
    def make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make an API request"""
        pass
    
    def handle_error(self, error: Exception) -> None:
        """Handle API request errors"""
        pass
