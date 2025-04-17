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
    Awards up to 15 points for having tight spread (<0.5%) and deep order book.
    Enhanced with volatility-adjusted spread and market impact analysis.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the liquidity indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("liquidity", 15.0, data_provider)
        self._target_spread = 0.005  # 0.5%
        self._volatility_window = 14  # Days to calculate volatility
        self._market_impact_threshold = 0.01  # 1% price impact
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the liquidity score based on bid/ask spread and market depth
        with enhanced analysis of volatility-adjusted spread and market impact
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results
        """
        # Extract data
        spread = data.get('spread', 0.01)  # Default to 1% if not available
        market_cap = data.get('market_cap', 0)
        total_volume = data.get('total_volume_24h', 0)
        prices = data.get('prices', [])
        current_price = data.get('price_usd', 0)
        
        # Calculate volatility-adjusted spread
        volatility = self._calculate_volatility(prices)
        vol_adjusted_spread = spread
        if volatility > 0:
            vol_adjusted_spread = spread / volatility
        
        # Calculate market impact (how much $1M would move the price)
        market_impact = self._estimate_market_impact(total_volume, current_price)
        
        # Calculate spread score (0-15 points)
        # If spread is <= 0.5%, get full points
        # If spread is > 0.5%, score decreases linearly
        if vol_adjusted_spread <= self._target_spread:
            spread_score = self.max_score
        else:
            # More gradual decline for volatility-adjusted spread
            spread_score = max(0, self.max_score * (1 - (vol_adjusted_spread - self._target_spread) / (self._target_spread * 3)))
        
        # Calculate depth score (0-15 points) with market impact consideration
        # Lower market impact = higher score
        impact_score = max(0, self.max_score * (1 - market_impact / self._market_impact_threshold))
        
        # Traditional depth score using market cap and volume
        traditional_depth_score = min(
            self.max_score, 
            self.max_score * (1 - 1 / (1 + (market_cap + total_volume) / 100000000))
        )
        
        # Combine traditional depth score with impact score
        depth_score = 0.7 * traditional_depth_score + 0.3 * impact_score
        
        # Combine scores with different weights
        # Spread is more important than depth
        final_score = 0.7 * spread_score + 0.3 * depth_score
        
        # Round the score
        rounded_score = round(final_score, 2)
        
        # Return result with details
        return {
            'score': rounded_score,
            'details': {
                'spread': spread,
                'volatility': round(volatility, 4) if volatility else None,
                'volatility_adjusted_spread': round(vol_adjusted_spread, 4),
                'market_impact': f"{round(market_impact * 100, 2)}%" if market_impact else None,
                'spread_score': round(spread_score, 2),
                'market_cap': market_cap,
                'total_volume': total_volume,
                'depth_score': round(depth_score, 2),
                'target_spread': self._target_spread
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
