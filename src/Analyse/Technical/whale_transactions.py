"""
Whale Transactions Indicator implementation.
Analyzes potential whale activity through volume spikes and price patterns.
Enhanced with advanced pattern detection and machine learning-inspired techniques.
"""
import statistics
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional
from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider


class WhaleTransactionsIndicator(BaseIndicator):
    """
    Indicator that analyzes potential whale activity through volume spikes and price patterns.
    Awards up to 10 points for having >50% whale buys and no mass sell-offs.
    Enhanced with advanced pattern detection for accumulation and distribution phases.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the whale transactions indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("whale_transactions", 10.0, data_provider)
        self._logger = logging.getLogger("whale_transactions")
        
        # Configuration parameters
        self._volume_spike_threshold = 1.5  # Reduced from 2.0 to detect more spikes
        self._price_impact_threshold = 0.02  # Reduced from 0.03 to be more sensitive
        self._accumulation_window = 5  # Days to look for accumulation patterns
        self._distribution_penalty = 0.5  # Penalty multiplier for distribution patterns
        self._min_hours = 24  # Minimum hours of data needed for analysis
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a proxy score for whale transactions based on available data.
        Enhanced with advanced pattern detection for accumulation and distribution phases.
        
        Args:
            symbol: Symbol of the cryptocurrency
            data: Data retrieved from the data provider
            
        Returns:
            Dictionary with calculation results
        """
        # Extract price and volume data from market chart format
        market_chart = data.get('market_chart', {})
        prices = market_chart.get('prices', [])
        volumes = market_chart.get('total_volumes', [])
        
        # We need at least 24 hours of data for proper analysis
        min_hours = 24
        if not prices or len(prices) < min_hours or not volumes or len(volumes) < min_hours:
            self._logger.error(f"Not enough historical data for {symbol}")
            self._logger.error(f"Required: {min_hours} hours")
            self._logger.error(f"Available: prices={len(prices)}, volumes={len(volumes)}")
            return {
                'score': 0,
                'details': {
                    'error': 'Not enough historical data',
                    'required_data_points': min_hours,
                    'available_price_points': len(prices),
                    'available_volume_points': len(volumes),
                    'note': f'This indicator requires at least {min_hours} hours of price and volume history.'
                }
            }

        self._logger.debug(f"\nWhale Transactions Analysis for {symbol}")
        self._logger.debug(f"Raw data points: prices={len(prices)}, volumes={len(volumes)}")
        
        # Normalize data to ensure timestamps match
        price_volume_data = self._normalize_price_volume_data(prices, volumes)
        if not price_volume_data:
            self._logger.error(f"Could not normalize price and volume data for {symbol}")
            return {
                'score': 0,
                'details': {
                    'error': 'Could not normalize price and volume data',
                    'note': 'This indicator requires matching timestamps for price and volume data.'
                }
            }

        self._logger.debug(f"Normalized data points: {len(price_volume_data)}")
        self._logger.debug(f"First data point: {price_volume_data[0] if price_volume_data else 'None'}")
        self._logger.debug(f"Last data point: {price_volume_data[-1] if price_volume_data else 'None'}")
        
        # Normalize data to ensure timestamps match
        price_volume_data = self._normalize_price_volume_data(prices, volumes)
        if not price_volume_data:
            return {
                'score': 0,
                'details': {
                    'error': 'Could not normalize price and volume data',
                    'note': 'This indicator requires matching timestamps for price and volume data.'
                }
            }
        
        # 1. Detect volume spikes with price impact
        volume_spikes, buy_spikes, sell_spikes = self._detect_volume_spikes(price_volume_data)
        
        # 2. Detect accumulation and distribution patterns
        accumulation_score, distribution_score, patterns = self._detect_whale_patterns(price_volume_data)
        
        # 3. Calculate buy/sell ratio
        total_spikes = buy_spikes + sell_spikes
        buy_ratio = buy_spikes / total_spikes if total_spikes > 0 else 0.5
        
        # 4. Check for mass sell-offs (consecutive price drops)
        max_consecutive_drops = self._detect_consecutive_drops(price_volume_data)
        
        # 5. Calculate price volatility
        volatility = self._calculate_volatility(price_volume_data)
        
        # 6. Calculate OBV (On-Balance Volume) trend
        obv_trend = self._calculate_obv_trend(price_volume_data)
        
        # Calculate component scores
        # Base score for having data
        base_score = 1.0
        
        # Buy ratio score (0-5 points)
        buy_ratio_score = 5 * min(1, buy_ratio / 0.5) if buy_ratio >= 0.5 else 0
        
        # Sell-off score (0-5 points)
        sell_off_score = 5 * max(0, 1 - (max_consecutive_drops / 5))
        
        # Pattern score (0-3 points)
        pattern_adjustment = (accumulation_score - distribution_score * self._distribution_penalty)
        pattern_score = max(0, min(3, pattern_adjustment))
        
        # OBV trend adjustment (-2 to +2 points)
        obv_adjustment = obv_trend * 2
        
        # Combine all factors into final score
        final_score = base_score + buy_ratio_score + sell_off_score + pattern_score + obv_adjustment
        capped_score = min(max(0, final_score), self.max_score)
        
        # Debug logging
        self._logger.debug(f"\nScoring Details for {symbol}")
        self._logger.debug(f"Volume spikes: {len(volume_spikes)}")
        self._logger.debug(f"Buy spikes: {buy_spikes}")
        self._logger.debug(f"Sell spikes: {sell_spikes}")
        self._logger.debug(f"Buy ratio: {buy_ratio:.2f}")
        self._logger.debug(f"Consecutive drops: {max_consecutive_drops}")
        self._logger.debug(f"Accumulation score: {accumulation_score:.2f}")
        self._logger.debug(f"Distribution score: {distribution_score:.2f}")
        self._logger.debug(f"OBV trend: {obv_trend:.2f}")
        self._logger.debug(f"Final score: {capped_score:.2f}")
        
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
                'accumulation_patterns': patterns['accumulation'],
                'distribution_patterns': patterns['distribution'],
                'pattern_score': round(pattern_score, 2),
                'obv_trend': round(obv_trend, 2),
                'price_volatility': round(volatility * 100, 2),  # As percentage
                'data_points_analyzed': len(price_volume_data),
                'note': 'This score analyzes volume spikes and price patterns to estimate whale activity.'
            }
        }
    
    def _normalize_price_volume_data(self, prices: List, volumes: List) -> List[Dict[str, Any]]:
        """
        Normalize price and volume data to ensure timestamps match
        
        Args:
            prices: List of price data points [timestamp, price]
            volumes: List of volume data points [timestamp, volume]
            
        Returns:
            List of dictionaries with timestamp, price, and volume
        """
        if not prices or not volumes:
            return []
            
        # Create dictionaries for faster lookup
        price_dict = {int(p[0]): p[1] for p in prices if isinstance(p, list) and len(p) > 1}
        volume_dict = {int(v[0]): v[1] for v in volumes if isinstance(v, list) and len(v) > 1}
        
        # Find common timestamps
        common_timestamps = sorted(set(price_dict.keys()).intersection(set(volume_dict.keys())))
        
        # Create normalized data
        normalized_data = [
            {
                'timestamp': ts,
                'price': price_dict[ts],
                'volume': volume_dict[ts]
            }
            for ts in common_timestamps
        ]
        
        return normalized_data
    
    def _detect_volume_spikes(self, data: List[Dict[str, Any]]) -> Tuple[List[int], int, int]:
        """
        Detect volume spikes and classify them as buy or sell spikes
        
        Args:
            data: Normalized price and volume data
            
        Returns:
            Tuple of (volume_spike_indices, buy_spikes_count, sell_spikes_count)
        """
        if not data:
            return [], 0, 0
            
        # Calculate average volume
        volumes = [d['volume'] for d in data]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        
        # Detect spikes
        volume_spikes = []
        buy_spikes = 0
        sell_spikes = 0
        
        for i in range(1, len(data)):
            # Check if volume exceeds threshold
            if data[i]['volume'] > self._volume_spike_threshold * avg_volume:
                volume_spikes.append(i)
                
                # Calculate price change percentage
                price_change = 0
                if data[i-1]['price'] > 0:
                    price_change = (data[i]['price'] - data[i-1]['price']) / data[i-1]['price']
                
                # Classify as buy or sell based on price impact
                if price_change > self._price_impact_threshold:
                    buy_spikes += 1
                elif price_change < -self._price_impact_threshold:
                    sell_spikes += 1
                else:
                    # If price impact is minimal, use direction
                    if price_change > 0:
                        buy_spikes += 1
                    else:
                        sell_spikes += 1
        
        return volume_spikes, buy_spikes, sell_spikes
    
    def _detect_whale_patterns(self, data: List[Dict[str, Any]]) -> Tuple[float, float, Dict[str, List[int]]]:
        """
        Detect accumulation and distribution patterns
        
        Args:
            data: Normalized price and volume data
            
        Returns:
            Tuple of (accumulation_score, distribution_score, patterns_dict)
        """
        if not data or len(data) < self._accumulation_window + 1:
            return 0.0, 0.0, {'accumulation': [], 'distribution': []}
        
        accumulation_patterns = []
        distribution_patterns = []
        
        # Sliding window analysis
        for i in range(len(data) - self._accumulation_window):
            window = data[i:i+self._accumulation_window]
            
            # Calculate price trend in window
            price_start = window[0]['price']
            price_end = window[-1]['price']
            price_change = (price_end - price_start) / price_start if price_start > 0 else 0
            
            # Calculate volume trend
            volumes = [d['volume'] for d in window]
            volume_trend = self._calculate_trend(volumes)
            
            # Accumulation pattern: Increasing volume, stable or slightly increasing price
            if volume_trend > 0.5 and 0 <= price_change < 0.05:
                accumulation_patterns.append(i)
            
            # Distribution pattern: Increasing volume, decreasing price
            if volume_trend > 0.5 and price_change < -0.02:
                distribution_patterns.append(i)
        
        # Calculate scores based on pattern frequency
        accumulation_score = min(3.0, len(accumulation_patterns) * 0.5)
        distribution_score = min(3.0, len(distribution_patterns) * 0.5)
        
        return accumulation_score, distribution_score, {
            'accumulation': accumulation_patterns,
            'distribution': distribution_patterns
        }
    
    def _detect_consecutive_drops(self, data: List[Dict[str, Any]]) -> int:
        """
        Detect consecutive price drops
        
        Args:
            data: Normalized price and volume data
            
        Returns:
            Maximum number of consecutive price drops
        """
        if not data:
            return 0
            
        consecutive_drops = 0
        max_consecutive_drops = 0
        
        for i in range(1, len(data)):
            if data[i]['price'] < data[i-1]['price']:
                consecutive_drops += 1
            else:
                max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)
                consecutive_drops = 0
        
        # Check final streak
        max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)
        
        return max_consecutive_drops
    
    def _calculate_volatility(self, data: List[Dict[str, Any]]) -> float:
        """
        Calculate price volatility
        
        Args:
            data: Normalized price and volume data
            
        Returns:
            Volatility as a decimal
        """
        if not data or len(data) < 2:
            return 0.5  # Default
            
        # Calculate daily returns
        returns = []
        for i in range(1, len(data)):
            if data[i-1]['price'] > 0:
                daily_return = (data[i]['price'] - data[i-1]['price']) / data[i-1]['price']
                returns.append(daily_return)
        
        if not returns:
            return 0.5
            
        try:
            return float(np.std(returns))
        except:
            return statistics.stdev(returns) if len(returns) > 1 else 0.5
    
    def _calculate_obv_trend(self, data: List[Dict[str, Any]]) -> float:
        """
        Calculate On-Balance Volume (OBV) trend
        
        Args:
            data: Normalized price and volume data
            
        Returns:
            OBV trend as a value between -1 and 1
        """
        if not data or len(data) < 2:
            return 0.0
            
        # Calculate OBV
        obv = [0]
        for i in range(1, len(data)):
            if data[i]['price'] > data[i-1]['price']:
                obv.append(obv[-1] + data[i]['volume'])
            elif data[i]['price'] < data[i-1]['price']:
                obv.append(obv[-1] - data[i]['volume'])
            else:
                obv.append(obv[-1])
        
        # Calculate OBV trend using linear regression slope
        if len(obv) < 3:
            return 0.0
            
        return self._calculate_trend(obv)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate trend of a time series using normalized slope
        
        Args:
            values: List of values
            
        Returns:
            Trend as a value between -1 and 1
        """
        if not values or len(values) < 2:
            return 0.0
            
        try:
            # Simple linear regression
            x = np.array(range(len(values)))
            y = np.array(values)
            
            # Calculate slope
            n = len(values)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) ** 2)
            
            # Normalize slope to [-1, 1] range
            max_possible_slope = max(values) - min(values)
            if max_possible_slope > 0:
                normalized_slope = slope / max_possible_slope
                return max(-1.0, min(1.0, normalized_slope))
            return 0.0
        except:
            # Fallback to simple end-to-start comparison
            if values[-1] > values[0]:
                return 0.5
            elif values[-1] < values[0]:
                return -0.5
            return 0.0
