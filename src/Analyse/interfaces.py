"""
Core interfaces for the indicator system.
Following SOLID principles with clear interface segregation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


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
    def calculate(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate the indicator score for a given cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary containing score and calculation details
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


class IIndicatorResult(ABC):
    """Interface for indicator results"""
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Get the symbol this result is for"""
        pass
    
    @property
    @abstractmethod
    def indicator_name(self) -> str:
        """Get the name of the indicator"""
        pass
    
    @property
    @abstractmethod
    def score(self) -> float:
        """Get the calculated score"""
        pass
    
    @property
    @abstractmethod
    def max_score(self) -> float:
        """Get the maximum possible score"""
        pass
    
    @property
    @abstractmethod
    def details(self) -> Dict[str, Any]:
        """Get detailed information about the calculation"""
        pass


class IIndicatorRunner(ABC):
    """Interface for running indicators"""
    
    @abstractmethod
    def run_indicator(self, indicator: IIndicator, symbol: str) -> IIndicatorResult:
        """
        Run a single indicator for a cryptocurrency
        
        Args:
            indicator: The indicator to run
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Result of the indicator calculation
        """
        pass
    
    @abstractmethod
    def run_all_indicators(self, indicators: List[IIndicator], symbol: str) -> List[IIndicatorResult]:
        """
        Run multiple indicators for a cryptocurrency
        
        Args:
            indicators: List of indicators to run
            symbol: Symbol of the cryptocurrency
            
        Returns:
            List of results from all indicator calculations
        """
        pass
