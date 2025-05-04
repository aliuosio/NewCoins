"""
Trading Volume Indicator implementation.
Measures trading volume over 24 hours.
"""
from typing import Dict, Any
from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider


class TradingVolumeIndicator(BaseIndicator):
    """
    Indicator that measures trading volume over 24 hours.
    Awards up to 10 points for having at least $1M in 24h trading volume.
    Based on the original PumpAndDump implementation.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the trading volume indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("trading_volume", 10.0, data_provider)
        self._target_volume = 1_000_000  # $1M in USD
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the trading volume score
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results
        """
        # Extract volume data
        total_volume = data.get('total_volume_24h', 0)
        
        # Calculate score based on volume
        if total_volume >= self._target_volume:
            score = self.max_score
        else:
            score = (total_volume / self._target_volume) * self.max_score
        
        # Return result with details
        return {
            'score': score,
            'details': {
                'total_volume_24h': total_volume,
                'target_volume': self._target_volume,
                'percentage_of_target': (total_volume / self._target_volume) * 100 if self._target_volume > 0 else 0
            }
        }
