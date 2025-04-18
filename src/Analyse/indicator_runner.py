"""
Indicator runner implementation for executing indicators and collecting results.
"""
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .interfaces import IIndicator, IIndicatorResult, IIndicatorRunner


class IndicatorResult(IIndicatorResult):
    """Implementation of indicator result"""
    
    def __init__(self, symbol: str, indicator_name: str, score: float, max_score: float, 
                 details: Dict[str, Any], execution_time_ms: Optional[int] = None,
                 success: bool = True, error: Optional[str] = None):
        self._symbol = symbol
        self._indicator_name = indicator_name
        self._score = score
        self._max_score = max_score
        self._details = details
        self._execution_time_ms = execution_time_ms
        self._success = success
        self._error = error
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @property
    def indicator_name(self) -> str:
        return self._indicator_name
    
    @property
    def score(self) -> float:
        return self._score
    
    @property
    def max_score(self) -> float:
        return self._max_score
    
    @property
    def details(self) -> Dict[str, Any]:
        return self._details
    
    @property
    def execution_time_ms(self) -> Optional[int]:
        return self._execution_time_ms
    
    @property
    def success(self) -> bool:
        return self._success
    
    @property
    def error(self) -> Optional[str]:
        return self._error


class IndicatorRunner(IIndicatorRunner):
    """
    Runs indicators and collects results.
    This implementation doesn't write to the database.
    """
    
    def __init__(self):
        """Initialize the indicator runner"""
        self._logger = logging.getLogger("indicator_runner")
    
    def run_indicator(self, indicator: IIndicator, symbol: str) -> IIndicatorResult:
        """
        Run a single indicator for a cryptocurrency
        
        Args:
            indicator: The indicator to run
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Result of the indicator calculation
        """
        start_time = time.time()
        self._logger.info(f"Running {indicator.name} for {symbol}")
        
        try:
            # Fetch data from data provider
            data = indicator._data_provider.get_data(symbol)
            self._logger.debug(f"Fetched data for {symbol}: {data}")
            
            # Calculate indicator with data
            result = indicator.calculate(symbol, data)
            
            # Log detailed results for debugging
            self._logger.debug(f"Indicator {indicator.name} results for {symbol}:")
            self._logger.debug(f"Raw result: {result}")
            
            # Extract execution time if available, otherwise calculate it
            execution_time = result.get('calculation_time_ms')
            if execution_time is None:
                execution_time = int((time.time() - start_time) * 1000)
            
            # Check for error
            if 'error' in result:
                self._logger.error(f"Error in {indicator.name} for {symbol}: {result['error']}")
                return IndicatorResult(
                    symbol=symbol,
                    indicator_name=indicator.name,
                    score=0.0,
                    max_score=indicator.max_score,
                    details=result.get('details', {}),
                    execution_time_ms=execution_time,
                    success=False,
                    error=result['error']
                )
            
            # Create result object
            return IndicatorResult(
                symbol=symbol,
                indicator_name=indicator.name,
                score=result['score'],
                max_score=indicator.max_score,
                details=result.get('details', {}),
                execution_time_ms=execution_time,
                success=True
            )
            
        except Exception as e:
            self._logger.error(f"Error running {indicator.name} for {symbol}: {str(e)}")
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create error result
            return IndicatorResult(
                symbol=symbol,
                indicator_name=indicator.name,
                score=0.0,
                max_score=indicator.max_score,
                details={},
                execution_time_ms=execution_time,
                success=False,
                error=str(e)
            )
    
    def run_all_indicators(self, indicators: List[IIndicator], symbol: str) -> List[IIndicatorResult]:
        """
        Run multiple indicators for a cryptocurrency
        
        Args:
            indicators: List of indicators to run
            symbol: Symbol of the cryptocurrency
            
        Returns:
            List of results from all indicator calculations
        """
        results = []
        
        for indicator in indicators:
            result = self.run_indicator(indicator, symbol)
            results.append(result)
        
        return results
