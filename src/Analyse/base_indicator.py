"""
Base indicator implementation that follows SOLID principles.
Includes caching functionality.
"""
import time
import logging
from abc import abstractmethod, ABC
from typing import Dict, Any, Optional

from .interfaces import IIndicator, IDataProvider


class BaseIndicator(IIndicator):
    """
    Abstract base class for all indicators.
    Implements common functionality like caching and calculation structure,
    while requiring subclasses to implement the specific calculation logic.
    """
    # Standard cache duration (1 hour) - can be overridden by subclasses
    CACHE_TTL = 3600

    def __init__(self, name: str, max_score: float, data_provider: IDataProvider):
        """
        Initialize the indicator

        Args:
            name: Name of the indicator
            max_score: Maximum possible score for this indicator
            data_provider: Data provider to use for fetching data
        """
        self._name = name
        self._max_score = max_score
        self._data_provider = data_provider
        self._logger = logging.getLogger(f"indicator.{name}")
        # Cache storage
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, float] = {}

    @property
    def name(self) -> str:
        """Get the name of the indicator"""
        return self._name
    
    @property
    def max_score(self) -> float:
        """Get the maximum possible score for this indicator"""
        return self._max_score
    
    def calculate(self, symbol: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate the indicator score for a given cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data to use for calculation (optional)
            
        Returns:
            Dictionary with calculation results
        """
        start_time = time.time()

        try:
            # Check cache first
            cache_key = f"{self._name}_{symbol}"
            current_time = time.time()
            
            # Check if we have cached data that hasn't expired
            if cache_key in self._cache and current_time < self._cache_expiry[cache_key]:
                self._logger.debug(f"Using cached data for {symbol}")
                return self._cache[cache_key]
            
            # Get data from provider if not provided
            if data is None:
                data = self._data_provider.get_data(symbol)

            # Perform the calculation - this is where subclasses implement logic
            result = self._calculate(symbol, data)

            # Ensure score is present and within bounds
            if 'score' not in result:
                raise ValueError("Calculation result must include a 'score' key.")
            result['score'] = max(0.0, min(float(result['score']), self.max_score))

            # Add metadata
            result.update({
                'symbol': symbol,
                'indicator': self.name,
                'max_score': self.max_score,
                'calculation_time_ms': int((time.time() - start_time) * 1000)
            })
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error calculating {self.name} for {symbol}: {str(e)}")
            return self._create_error_response(symbol, str(e))
    
    @abstractmethod
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the actual indicator calculation
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results including at least a 'score' key
        """
        pass

    # --- Caching Methods ---

    def _is_cache_valid(self, key: str) -> bool:
        """
        Check if a cached item is still valid.

        Args:
            key (str): Cache key

        Returns:
            bool: True if cache is valid, False otherwise
        """
        if key not in self._cache or key not in self._cache_expiry:
            return False
        is_valid = time.time() < self._cache_expiry.get(key, 0)
        if is_valid:
            self._logger.debug(f"Cache hit for key: {key}")
        else:
            self._logger.debug(f"Cache expired or miss for key: {key}")
        return is_valid

    def _cache_result(self, key: str, result: Any, ttl: Optional[int] = None) -> Any:
        """
        Cache a result with expiration time.

        Args:
            key (str): Cache key
            result (Any): Result to cache
            ttl (int, optional): Time to live in seconds. Defaults to self.CACHE_TTL.

        Returns:
            Any: The cached result
        """
        if ttl is None:
            ttl = self.CACHE_TTL
        self._cache[key] = result
        self._cache_expiry[key] = time.time() + ttl
        self._logger.debug(f"Cached result for key: {key} with TTL: {ttl}s")
        return result

    def _get_cached_result(self, key: str) -> Optional[Any]:
        """
        Get a result from the cache if it's valid.

        Args:
            key (str): Cache key

        Returns:
            Optional[Any]: The cached result if valid, otherwise None
        """
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None

    # --- Error Handling ---

    def _create_error_response(self, symbol: str, error_message: str) -> Dict[str, Any]:
        """
        Create a standardized error response

        Args:
            symbol: Symbol of the cryptocurrency
            error_message: Error message to include

        Returns:
            Standardized error response dictionary
        """
        return {
            'symbol': symbol,
            'indicator': self.name,
            'score': 0.0, # Ensure score is float
            'max_score': self.max_score,
            'error': error_message,
            'success': False
        }
