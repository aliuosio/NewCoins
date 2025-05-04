"""
Liquidity Indicator implementation.
Measures liquidity based on spread and market depth.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider


class LiquidityIndicator(BaseIndicator):
    """
    Indicator that measures liquidity based on spread and market depth.
    Awards up to 10 points for having tight spread (<0.5%) and deep order book.
    Enhanced with volatility-adjusted spread and market impact analysis.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the liquidity indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("liquidity", 10.0, data_provider)
        self._target_spread = 0.005  # 0.5%
        self._volatility_window = 14  # Days to calculate volatility
        self._market_impact_threshold = 0.01  # 1% price impact
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the liquidity score based solely on 24h trading volume.
        Awards up to 15 points for having at least $1M in 24h trading volume.
        """
        import numbers
        def safe_float(val, name):
            if isinstance(val, numbers.Real):
                return float(val)
            elif isinstance(val, complex):
                print(f"[DEBUG][LiquidityIndicator] {name} is complex ({val}), using real part only.")
                return float(val.real)
            try:
                return float(val)
            except Exception as e:
                print(f"[DEBUG][LiquidityIndicator] Could not convert {name}={val} to float: {e}")
                return 0.0
        total_volume = safe_float(data.get('total_volume_24h', 0), 'total_volume_24h')
        target_volume = 1_000_000  # $1M USD
        if total_volume >= target_volume:
            score = self.max_score
        else:
            score = (total_volume / target_volume) * self.max_score
        score = max(0.0, min(self.max_score, score))
        warning = None
        if not total_volume:
            warning = 'WARNING: No 24h volume data available from API. Liquidity score may be invalid.'
        return {
            'score': round(score, 2),
            'details': {
                'total_volume_24h': total_volume,
                'target_volume': target_volume,
                'warning': warning
            }
        }
        
    def _calculate_volatility(self, prices: List) -> float:
        """
        Calculate price volatility using standard deviation of returns
        
        Args:
            prices: List of price data points [timestamp, price]
            
        Returns:
            Volatility as a decimal (e.g., 0.05 for 5%)
        """
        if not prices or len(prices) < 2:
            return 0.0
            
        # Extract just the prices (second element in each pair)
        price_values = [p[1] for p in prices[-self._volatility_window:] if isinstance(p, list) and len(p) > 1]
        
        if len(price_values) < 2:
            return 0.0
            
        # Calculate daily returns
        returns = []
        for i in range(1, len(price_values)):
            if price_values[i-1] > 0:  # Avoid division by zero
                daily_return = (price_values[i] - price_values[i-1]) / price_values[i-1]
                returns.append(daily_return)
        
        if not returns:
            return 0.0
            
        # Calculate standard deviation of returns
        return float(np.std(returns))
    
    def _estimate_market_impact(self, daily_volume: float, current_price: float) -> float:
        """
        Estimate market impact of a $1M trade based on daily volume
        
        Args:
            daily_volume: 24h trading volume in USD
            current_price: Current price in USD
            
        Returns:
            Estimated price impact as a decimal (e.g., 0.02 for 2%)
        """
        if not daily_volume or not current_price:
            return 0.0
            
        # Standard trade size for impact estimation
        standard_trade_size = 1000000  # $1M
        
        # Simple square-root model for market impact
        # Impact ~ k * (trade size / daily volume)^0.5
        # k is a constant, typically 0.1-0.3
        k = 0.2
        impact = k * (standard_trade_size / daily_volume) ** 0.5
        
        # Cap the impact at 100%
        return min(1.0, impact)
