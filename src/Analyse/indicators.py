"""
Concrete indicator implementations based on the original PumpAndDump system.
"""
from typing import Dict, Any, List
import statistics
from datetime import datetime

from .base_indicator import BaseIndicator
from .interfaces import IDataProvider


class TradingVolumeIndicator(BaseIndicator):
    """
    Indicator that measures trading volume over 24 hours.
    Awards up to 15 points for having at least $1M in 24h trading volume.
    Based on the original PumpAndDump implementation.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the trading volume indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("trading_volume", 15.0, data_provider)
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


class LiquidityIndicator(BaseIndicator):
    """
    Indicator that measures liquidity based on spread and market depth.
    Awards up to 15 points for having tight spread (<0.5%) and deep order book.
    Based on the original PumpAndDump implementation.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the liquidity indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("liquidity", 15.0, data_provider)
        self._target_spread = 0.005  # 0.5%
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the liquidity score based on bid/ask spread and market depth
        
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
        
        # Calculate spread score (0-15 points)
        # If spread is <= 0.5%, get full points
        # If spread is > 0.5%, score decreases linearly
        if spread <= self._target_spread:
            spread_score = self.max_score
        else:
            spread_score = max(0, self.max_score * (1 - (spread - self._target_spread) / self._target_spread))
        
        # Calculate depth score (0-15 points)
        # Use logarithmic scale to avoid very high scores for extremely deep markets
        # Consider both market cap and volume
        depth_score = min(
            self.max_score, 
            self.max_score * (1 - 1 / (1 + (market_cap + total_volume) / 100000000))
        )
        
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
                'spread_score': round(spread_score, 2),
                'market_cap': market_cap,
                'total_volume': total_volume,
                'depth_score': round(depth_score, 2),
                'target_spread': self._target_spread
            }
        }


class WhaleTransactionsIndicator(BaseIndicator):
    """
    Indicator that analyzes potential whale activity through volume spikes and price patterns.
    Awards up to 10 points for having >50% whale buys and no mass sell-offs.
    Based on the original PumpAndDump implementation.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the whale transactions indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("whale_transactions", 10.0, data_provider)
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a proxy score for whale transactions based on available data.
        This is a simplified approach since most APIs don't provide direct whale transaction data.
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results
        """
        # Extract price and volume data
        prices = data.get('prices', [])
        volumes = data.get('volumes', [])
        
        if not prices or len(prices) < 24 or not volumes or len(volumes) < 24:
            return {
                'score': 0,
                'details': {
                    'error': 'Not enough historical data',
                    'required_data_points': 24,
                    'available_price_points': len(prices),
                    'available_volume_points': len(volumes)
                }
            }
        
        # 1. Look for abnormal volume spikes (potential whale buys/sells)
        avg_volume = sum(vol[1] for vol in volumes) / len(volumes) if volumes else 0
        volume_spikes = []
        for i, vol in enumerate(volumes):
            if vol[1] > 2 * avg_volume:  # Volume more than 2x average
                volume_spikes.append((i, vol[1]))
        
        # 2. Analyze price movements during volume spikes
        buy_spikes = 0
        sell_spikes = 0
        for spike_idx, _ in volume_spikes:
            if spike_idx > 0 and spike_idx < len(prices):
                # Price increased during spike = likely buy pressure
                if prices[spike_idx][1] > prices[spike_idx-1][1]:  
                    buy_spikes += 1
                # Price decreased during spike = likely sell pressure
                else:  
                    sell_spikes += 1
        
        # 3. Calculate buy/sell ratio (>50% whale buys)
        total_spikes = buy_spikes + sell_spikes
        buy_ratio = buy_spikes / total_spikes if total_spikes > 0 else 0.5
        
        # 4. Check for mass sell-offs (consecutive price drops with high volume)
        consecutive_drops = 0
        max_consecutive_drops = 0
        for i in range(1, len(prices)):
            if prices[i][1] < prices[i-1][1]:
                consecutive_drops += 1
            else:
                max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)
                consecutive_drops = 0
        max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)  # In case the last ones were drops
        
        # 5. Calculate price volatility (for sudden drops)
        price_changes = []
        for i in range(1, len(prices)):
            if prices[i-1][1] > 0:  # Avoid division by zero
                change = (prices[i][1] - prices[i-1][1]) / prices[i-1][1]
                price_changes.append(change)
        
        try:
            volatility = statistics.stdev(price_changes) if price_changes else 0.5
        except statistics.StatisticsError:
            volatility = 0.5  # Default if not enough data
        
        # Calculate scores for each component
        # 1. Buy ratio score (higher is better, >50% is ideal)
        buy_ratio_score = 5 * min(1, buy_ratio / 0.5) if buy_ratio >= 0.5 else 0
        
        # 2. No mass sell-offs score (lower consecutive drops is better)
        # Normalize: 0 drops = 5 points, 5+ drops = 0 points
        sell_off_score = 5 * max(0, 1 - (max_consecutive_drops / 5))
        
        # Combine scores
        final_score = buy_ratio_score + sell_off_score
        
        # Cap at max_score
        capped_score = min(final_score, self.max_score)
        
        return {
            'score': capped_score,
            'details': {
                'volume_spikes_detected': len(volume_spikes),
                'buy_spikes': buy_spikes,
                'sell_spikes': sell_spikes,
                'buy_ratio': round(buy_ratio * 100, 2),  # As percentage
                'buy_ratio_score': round(buy_ratio_score, 2),
                'max_consecutive_drops': max_consecutive_drops,
                'sell_off_score': round(sell_off_score, 2),
                'price_volatility': round(volatility * 100, 2),  # As percentage
                'data_points_analyzed': len(prices),
                'note': 'This score analyzes volume spikes and price patterns to estimate whale activity.'
            }
        }


class TokenDistributionIndicator(BaseIndicator):
    """
    Indicator that analyzes token distribution based on supply metrics and community size.
    Awards up to 10 points for having no single wallet holding >10% of tokens.
    Based on the original PumpAndDump implementation.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the token distribution indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("token_distribution", 10.0, data_provider)
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a proxy score for token distribution based on available metrics.
        This is a simplified approach since most APIs don't provide direct wallet concentration data.
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results
        """
        # Extract coin data
        coin_data = data.get('coin_data', {})
        
        if not coin_data:
            return {
                'score': 0,
                'details': {
                    'error': 'Could not retrieve coin data',
                    'note': 'Token distribution analysis requires detailed coin data'
                }
            }
        
        # Calculate distribution score based on available proxies
        score = self._calculate_distribution_score(coin_data)
        
        # Ensure score is within bounds
        final_score = min(score, self.max_score)
        
        # Prepare details
        details = {
            'note': 'This is a proxy score based on supply metrics and community size.'
        }
        
        # Add supply metrics if available
        market_data = coin_data.get('market_data', {})
        if market_data:
            if 'circulating_supply' in market_data and 'total_supply' in market_data and market_data.get('total_supply'):
                circulation_ratio = market_data['circulating_supply'] / market_data['total_supply']
                details['circulation_ratio'] = f"{round(circulation_ratio * 100, 2)}%"
                
            if 'market_cap' in market_data and 'fully_diluted_valuation' in market_data:
                fdv = market_data.get('fully_diluted_valuation')
                if isinstance(fdv, (int, float)) and fdv > 0:
                    dilution_ratio = market_data['market_cap'] / fdv
                    details['dilution_ratio'] = f"{round(dilution_ratio * 100, 2)}%"
        
        # Add community metrics if available
        community = coin_data.get('community_data', {})
        if community and 'twitter_followers' in community:
            details['twitter_followers'] = community['twitter_followers']
        
        return {
            'score': final_score,
            'details': details
        }
    
    def _calculate_distribution_score(self, coin_data: Dict[str, Any]) -> float:
        """
        Calculate a proxy score for token distribution based on available metrics
        
        Args:
            coin_data: Coin data from the data provider
            
        Returns:
            Score between 0 and 10
        """
        score = 5  # Start with a neutral score
        
        # Check if we have market data
        market_data = coin_data.get('market_data', {})
        if not market_data:
            return score
        
        # 1. Check circulating supply vs total supply ratio
        # A higher ratio indicates better distribution
        if 'circulating_supply' in market_data and 'total_supply' in market_data:
            total_supply = market_data['total_supply']
            if total_supply:
                circulation_ratio = market_data['circulating_supply'] / total_supply
                
                # Score based on circulation ratio:
                # 90%+ circulating = +3 points (excellent distribution)
                # 70-90% circulating = +2 points (good distribution)
                # 50-70% circulating = +1 point (fair distribution)
                # <50% circulating = +0 points (poor distribution)
                if circulation_ratio >= 0.9:
                    score += 3
                elif circulation_ratio >= 0.7:
                    score += 2
                elif circulation_ratio >= 0.5:
                    score += 1
        
        # 2. Check market cap vs fully diluted valuation
        # A ratio closer to 1 suggests less future dilution
        if 'market_cap' in market_data and 'fully_diluted_valuation' in market_data:
            fdv = market_data['fully_diluted_valuation']
            if isinstance(fdv, (int, float)) and fdv > 0:
                dilution_ratio = market_data['market_cap'] / fdv
                
                # Score based on dilution ratio:
                # >90% = +2 points (minimal dilution risk)
                # >70% = +1 point (moderate dilution risk)
                # <70% = +0 points (high dilution risk)
                if dilution_ratio > 0.9:
                    score += 2
                elif dilution_ratio > 0.7:
                    score += 1
        
        # 3. Check community metrics as a proxy for distribution
        # Larger communities often correlate with wider distribution
        community = coin_data.get('community_data', {})
        if community:
            # Twitter followers as a proxy for distribution
            twitter_followers = community.get('twitter_followers', 0)
            if twitter_followers:
                # Score based on Twitter followers:
                # >100K followers = +1 point
                # >1M followers = +2 points
                if twitter_followers > 1000000:
                    score += 2
                elif twitter_followers > 100000:
                    score += 1
        
        return score
