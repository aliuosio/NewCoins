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
    
    For established cryptocurrencies with high liquidity (like Bitcoin), this indicator
    uses different thresholds and detection methods to avoid false negatives.
    """
    
    # List of high-liquidity cryptocurrencies that require different thresholds
    HIGH_LIQUIDITY_COINS = {
        'BTC': 'bitcoin',       # Bitcoin
        'ETH': 'ethereum',     # Ethereum
        'BNB': 'binance-coin', # Binance Coin
        'SOL': 'solana',       # Solana
        'XRP': 'ripple',       # XRP
        'ADA': 'cardano',      # Cardano
        'DOGE': 'dogecoin',    # Dogecoin
        'DOT': 'polkadot',     # Polkadot
        'MATIC': 'polygon',    # Polygon
        'LINK': 'chainlink',   # Chainlink
        'LTC': 'litecoin',     # Litecoin
        'AVAX': 'avalanche-2', # Avalanche
        'UNI': 'uniswap',      # Uniswap
    }
    
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
        
        # High liquidity coin parameters (different thresholds)
        self._high_liquidity_volume_spike_threshold = 1.2  # Lower threshold for high liquidity coins
        self._high_liquidity_price_impact_threshold = 0.01  # Lower threshold for high liquidity coins
    
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
            
        # Check if this is a high-liquidity coin and adjust thresholds accordingly
        is_high_liquidity = symbol.upper() in self.HIGH_LIQUIDITY_COINS
        coin_id = data.get('coin_id', f"mock-{symbol.lower()}")
        if coin_id in self.HIGH_LIQUIDITY_COINS.values():
            is_high_liquidity = True
            
        # Adjust thresholds based on liquidity
        if is_high_liquidity:
            self._logger.debug(f"{symbol} is a high-liquidity coin, using adjusted thresholds")
            volume_spike_threshold = self._high_liquidity_volume_spike_threshold
            price_impact_threshold = self._high_liquidity_price_impact_threshold
        else:
            volume_spike_threshold = self._volume_spike_threshold
            price_impact_threshold = self._price_impact_threshold

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
        
        # For high-liquidity coins, we need to ensure we have a minimum baseline score
        # since whale activity is always present in major cryptocurrencies
        min_score = 2.0 if is_high_liquidity else 0.0
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
            
        # Detect volume spikes and classify them as buy or sell spikes
        # Use the appropriate threshold based on liquidity
        volume_spike_indices, buy_spikes_count, sell_spikes_count = self._detect_volume_spikes(
            price_volume_data, 
            volume_threshold=volume_spike_threshold,
            price_threshold=price_impact_threshold
        )
        
        # Calculate percentage of buy spikes
        total_spikes = buy_spikes_count + sell_spikes_count
        buy_percentage = (buy_spikes_count / total_spikes * 100) if total_spikes > 0 else 50
        
        # Detect whale patterns (accumulation and distribution)
        accumulation_score, distribution_score, patterns = self._detect_whale_patterns(price_volume_data)
        
        # Calculate OBV trend
        obv_trend = self._calculate_obv_trend(price_volume_data)
        
        # Detect consecutive price drops
        max_consecutive_drops = self._detect_consecutive_drops(price_volume_data)
        
        # Calculate volatility
        volatility = self._calculate_volatility(price_volume_data)
        
        # Calculate base score based on buy percentage
        # >50% buy spikes is good, <50% is bad
        if buy_percentage >= 50:
            base_score = 5.0 + (buy_percentage - 50) / 10
        else:
            base_score = 5.0 - (50 - buy_percentage) / 5
            
        # Adjust score based on accumulation vs distribution
        whale_activity_score = base_score + accumulation_score - distribution_score
        
        # Adjust score based on OBV trend
        # Positive OBV trend indicates buying pressure
        obv_adjustment = obv_trend * 2.0
        whale_activity_score += obv_adjustment
        
        # Penalize for consecutive price drops (potential dumping)
        if max_consecutive_drops > 3:
            consecutive_drop_penalty = min(3.0, (max_consecutive_drops - 3) * 0.5)
            whale_activity_score -= consecutive_drop_penalty
        
        # Adjust for volatility
        # High volatility can indicate whale manipulation
        volatility_factor = min(2.0, volatility * 10)
        if buy_percentage < 50:  # Only penalize for volatility if more sell spikes
            whale_activity_score -= volatility_factor
        
        # For high-liquidity coins, ensure a minimum score since whale activity is always present
        if is_high_liquidity:
            whale_activity_score = max(min_score, whale_activity_score)
            
            # For high-liquidity coins with significant market cap, we should also consider
            # the absolute volume of transactions as a factor
            market_cap = data.get('market_cap', 0)
            if market_cap > 1_000_000_000:  # > $1B market cap
                # Ensure score is at least 4.0 for major cryptocurrencies
                whale_activity_score = max(4.0, whale_activity_score)
        
        # Ensure score is within bounds
        final_score = max(0, min(10, whale_activity_score))
        
        # Round to 2 decimal places
        final_score = round(final_score, 2)
        
        return {
            'score': final_score,
            'details': {
                'volume_spikes_detected': len(volume_spike_indices),
                'buy_spikes': buy_spikes_count,
                'sell_spikes': sell_spikes_count,
                'buy_percentage': round(buy_percentage, 2),
                'accumulation_patterns': patterns['accumulation'],
                'distribution_patterns': patterns['distribution'],
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
    
    def _detect_volume_spikes(self, data: List[Dict[str, Any]], volume_threshold: float = None, price_threshold: float = None) -> Tuple[List[int], int, int]:
        """
        Detect volume spikes and classify them as buy or sell spikes
        
        Args:
            data: Normalized price and volume data
            volume_threshold: Threshold for volume spikes (optional)
            price_threshold: Threshold for price impact (optional)
            
        Returns:
            Tuple of (volume_spike_indices, buy_spikes_count, sell_spikes_count)
        """
        if not data or len(data) < 3:
            return [], 0, 0
            
        # Use provided thresholds or fall back to instance defaults
        volume_threshold = volume_threshold or self._volume_spike_threshold
        price_threshold = price_threshold or self._price_impact_threshold
        
        # Calculate moving average of volume
        window_size = min(24, len(data) // 3)
        volumes = [point['volume'] for point in data]
        volume_ma = []
        
        for i in range(len(volumes)):
            if i < window_size:
                # For the first window_size points, use all available data
                window = volumes[:i+1]
            else:
                # For the rest, use a sliding window
                window = volumes[i-window_size+1:i+1]
            volume_ma.append(sum(window) / len(window))
        
        # Detect volume spikes
        volume_spike_indices = []
        buy_spikes_count = 0
        sell_spikes_count = 0
        
        for i in range(window_size, len(data)):
            # Check if volume is significantly higher than the moving average
            if data[i]['volume'] > volume_ma[i] * volume_threshold:
                volume_spike_indices.append(i)
                
                # Classify as buy or sell spike based on price movement
                if i > 0 and data[i]['price'] > data[i-1]['price'] * (1 + price_threshold):
                    buy_spikes_count += 1
                elif i > 0 and data[i]['price'] < data[i-1]['price'] * (1 - price_threshold):
                    sell_spikes_count += 1
                else:
                    # If price change is not significant, classify based on general trend
                    if i > 2:
                        # Look at the trend over the last 3 data points
                        if data[i]['price'] > data[i-3]['price']:
                            buy_spikes_count += 1
                        else:
                            sell_spikes_count += 1
                    else:
                        # Default to neutral (count as both buy and sell)
                        buy_spikes_count += 0.5
                        sell_spikes_count += 0.5
        
        return volume_spike_indices, buy_spikes_count, sell_spikes_count
    
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
