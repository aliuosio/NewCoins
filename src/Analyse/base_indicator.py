"""
Base indicator implementation that follows SOLID principles.
"""
import time
import logging
from abc import abstractmethod
from typing import Dict, Any, Optional

from .interfaces import IIndicator, IDataProvider


class BaseIndicator(IIndicator):
    """
    Abstract base class for all indicators.
    Implements common functionality while requiring subclasses to implement
    the specific calculation logic.
    """
    
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
    
    @property
    def name(self) -> str:
        """Get the name of the indicator"""
        return self._name
    
    @property
    def max_score(self) -> float:
        """Get the maximum possible score for this indicator"""
        return self._max_score
    
    def calculate(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate the indicator score for a given cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary containing score and calculation details
        """
        start_time = time.time()
        
        try:
            # Get data from provider
            data = self._data_provider.get_data(symbol)
            
            # Perform the calculation
            result = self._calculate(symbol, data)
            
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
            'score': 0,
            'max_score': self.max_score,
            'error': error_message,
            'success': False
        }
