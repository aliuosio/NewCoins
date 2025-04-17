#!/usr/bin/env python3
"""
Test script for the PumpAndDump indicator system.
Tests all six indicators with mock data without database interaction.
Simple test script for indicators without relative imports.
"""
import sys
import os
import json
import statistics
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("indicator_test")

# Mock data provider
class MockDataProvider:
    """Mock data provider with realistic test data for all indicators"""
    """Mock data provider for testing"""
    
    def __init__(self):
        """Initialize the mock data provider"""
        self.name = "mock"
    
    def get_data(self, symbol: str) -> Dict[str, Any]:
        """Return mock data for the symbol"""
        # Normalize symbol
        symbol = symbol.upper()
        
        # Return comprehensive mock data for all indicators
        return {
            'symbol': symbol,
            'coin_id': f"mock-{symbol.lower()}",
            'price_usd': 1000.0,
            'market_cap': 10000000.0,  # $10M
            'total_volume_24h': 5000000.0,  # $5M
            'base_currency': symbol,
            'spread': 0.004,  # 0.4% spread (good liquidity)
            # Mock price history data for whale analysis
            'prices': [
                [1617580800000, 950.0],  # Timestamp and price
                [1617667200000, 980.0],
                [1617753600000, 1020.0],
                [1617840000000, 1050.0],
                [1617926400000, 1000.0],
                # Add more price points...
                [1618012800000, 1100.0],
                [1618099200000, 1150.0],
                [1618185600000, 1200.0],
                [1618272000000, 1180.0],
                [1618358400000, 1220.0],
                # More price points for 24 total
                [1618444800000, 1250.0],
                [1618531200000, 1300.0],
                [1618617600000, 1280.0],
                [1618704000000, 1320.0],
                [1618790400000, 1350.0],
                [1618876800000, 1370.0],
                [1618963200000, 1400.0],
                [1619049600000, 1380.0],
                [1619136000000, 1420.0],
                [1619222400000, 1450.0],
                [1619308800000, 1480.0],
                [1619395200000, 1500.0],
                [1619481600000, 1520.0],
                [1619568000000, 1550.0]
            ],
            # Mock volume history data
            'volumes': [
                [1617580800000, 2000000.0],  # Timestamp and volume
                [1617667200000, 2200000.0],
                [1617753600000, 2500000.0],
                [1617840000000, 2800000.0],
                [1617926400000, 3000000.0],
                # Add more volume points...
                [1618012800000, 3200000.0],
                [1618099200000, 3500000.0],
                [1618185600000, 3800000.0],
                [1618272000000, 4000000.0],
                [1618358400000, 4200000.0],
                # More volume points for 24 total
                [1618444800000, 4500000.0],
                [1618531200000, 4800000.0],
                [1618617600000, 5000000.0],
                [1618704000000, 5200000.0],
                [1618790400000, 5500000.0],
                [1618876800000, 10000000.0],  # Volume spike (whale activity)
                [1618963200000, 5800000.0],
                [1619049600000, 6000000.0],
                [1619136000000, 6200000.0],
                [1619222400000, 6500000.0],
                [1619308800000, 11000000.0],  # Another volume spike
                [1619395200000, 7000000.0],
                [1619481600000, 7200000.0],
                [1619568000000, 7500000.0]
            ],
            # Token distribution data
            'coin_data': {
                'market_data': {
                    'circulating_supply': 8000000.0,  # 80% circulating
                    'total_supply': 10000000.0,
                    'fully_diluted_valuation': 12000000.0
                },
                'community_data': {
                    'twitter_followers': 120000,
                    'reddit_subscribers': 50000,
                    'telegram_channel_user_count': 25000
                }
            },
            # For whale transactions and liquidity
            'market_chart': True
        }

    def get_vesting_data(self, coin_id: str) -> Dict[str, Any]:
        """Return mock vesting data for the coin"""
        # This is a mock implementation that returns simulated vesting data
        # In a real implementation, this would fetch data from an API or database
        return None  # Return None to trigger the fallback to simulated data

    def get_audit_data(self, coin_id: str) -> Dict[str, Any]:
        """Return mock audit data for the coin"""
        # This is a mock implementation that returns simulated audit data
        # In a real implementation, this would fetch data from an API or database
        return None  # Return None to trigger the fallback to simulated data

# Base indicator class
class BaseIndicator:
    """Base class for all indicators"""
    
    def __init__(self, name: str, max_score: float, data_provider):
        """Initialize the indicator"""
        self.name = name
        self.max_score = max_score
        self.data_provider = data_provider
        self.logger = logging.getLogger(f"indicator.{name}")
    
    def calculate(self, symbol: str) -> Dict[str, Any]:
        """Calculate the indicator score"""
        try:
            # Get data from provider
            data = self.data_provider.get_data(symbol)
            
            # Perform the calculation
            result = self._calculate(symbol, data)
            
            # Add metadata
            result.update({
                'symbol': symbol,
                'indicator': self.name,
                'max_score': self.max_score
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating {self.name} for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'indicator': self.name,
                'score': 0,
                'max_score': self.max_score,
                'error': str(e),
                'success': False
            }

# Trading volume indicator
class TradingVolumeIndicator(BaseIndicator):
    """Indicator that measures trading volume over 24 hours"""
    
    def __init__(self, data_provider):
        """Initialize the trading volume indicator"""
        super().__init__("trading_volume", 15.0, data_provider)
        self.target_volume = 1_000_000  # $1M in USD
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the trading volume score"""
        # Extract volume data
        total_volume = data.get('total_volume_24h', 0)
        
        # Calculate score based on volume
        if total_volume >= self.target_volume:
            score = self.max_score
        else:
            score = (total_volume / self.target_volume) * self.max_score
        
        # Return result with details
        return {
            'score': score,
            'details': {
                'total_volume_24h': total_volume,
                'target_volume': self.target_volume,
                'percentage_of_target': (total_volume / self.target_volume) * 100 if self.target_volume > 0 else 0
            }
        }

# Liquidity indicator
class LiquidityIndicator(BaseIndicator):
    """Indicator that measures liquidity based on spread and market depth"""
    
    def __init__(self, data_provider):
        """Initialize the liquidity indicator"""
        super().__init__("liquidity", 15.0, data_provider)
        self.target_spread = 0.005  # 0.5%
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the liquidity score"""
        # Extract data
        spread = data.get('spread', 0.01)  # Default to 1% if not available
        market_cap = data.get('market_cap', 0)
        total_volume = data.get('total_volume_24h', 0)
        
        # Calculate spread score (0-15 points)
        if spread <= self.target_spread:
            spread_score = self.max_score
        else:
            spread_score = max(0, self.max_score * (1 - (spread - self.target_spread) / self.target_spread))
        
        # Calculate depth score (0-15 points)
        depth_score = min(
            self.max_score, 
            self.max_score * (1 - 1 / (1 + (market_cap + total_volume) / 100000000))
        )
        
        # Combine scores with different weights
        final_score = 0.7 * spread_score + 0.3 * depth_score
        rounded_score = round(final_score, 2)
        
        return {
            'score': rounded_score,
            'details': {
                'spread': spread,
                'spread_score': round(spread_score, 2),
                'market_cap': market_cap,
                'total_volume': total_volume,
                'depth_score': round(depth_score, 2),
                'target_spread': self.target_spread
            }
        }

# Whale transactions indicator
class WhaleTransactionsIndicator(BaseIndicator):
    """Indicator that analyzes potential whale activity"""
    
    def __init__(self, data_provider):
        """Initialize the whale transactions indicator"""
        super().__init__("whale_transactions", 10.0, data_provider)
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the whale transactions score"""
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
        
        # 1. Look for abnormal volume spikes
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
        
        # 3. Calculate buy/sell ratio
        total_spikes = buy_spikes + sell_spikes
        buy_ratio = buy_spikes / total_spikes if total_spikes > 0 else 0.5
        
        # 4. Check for mass sell-offs
        consecutive_drops = 0
        max_consecutive_drops = 0
        for i in range(1, len(prices)):
            if prices[i][1] < prices[i-1][1]:
                consecutive_drops += 1
            else:
                max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)
                consecutive_drops = 0
        max_consecutive_drops = max(max_consecutive_drops, consecutive_drops)
        
        # 5. Calculate price volatility
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
        buy_ratio_score = 5 * min(1, buy_ratio / 0.5) if buy_ratio >= 0.5 else 0
        sell_off_score = 5 * max(0, 1 - (max_consecutive_drops / 5))
        
        # Combine scores
        final_score = buy_ratio_score + sell_off_score
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
                'data_points_analyzed': len(prices)
            }
        }

# Token distribution indicator
class TokenDistributionIndicator(BaseIndicator):
    """Indicator that analyzes token distribution based on supply metrics"""
    
    def __init__(self, data_provider):
        """Initialize the token distribution indicator"""
        super().__init__("token_distribution", 10.0, data_provider)
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the token distribution score"""
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
        
        score = 5  # Start with a neutral score
        
        # Check if we have market data
        market_data = coin_data.get('market_data', {})
        if market_data:
            # 1. Check circulating supply vs total supply ratio
            if 'circulating_supply' in market_data and 'total_supply' in market_data:
                total_supply = market_data['total_supply']
                if total_supply:
                    circulation_ratio = market_data['circulating_supply'] / total_supply
                    
                    if circulation_ratio >= 0.9:
                        score += 3
                    elif circulation_ratio >= 0.7:
                        score += 2
                    elif circulation_ratio >= 0.5:
                        score += 1
            
            # 2. Check market cap vs fully diluted valuation
            if 'market_cap' in market_data and 'fully_diluted_valuation' in market_data:
                fdv = market_data['fully_diluted_valuation']
                if isinstance(fdv, (int, float)) and fdv > 0:
                    dilution_ratio = market_data['market_cap'] / fdv
                    
                    if dilution_ratio > 0.9:
                        score += 2
                    elif dilution_ratio > 0.7:
                        score += 1
        
        # 3. Check community metrics as a proxy for distribution
        community = coin_data.get('community_data', {})
        if community:
            twitter_followers = community.get('twitter_followers', 0)
            if twitter_followers:
                if twitter_followers > 1000000:
                    score += 2
                elif twitter_followers > 100000:
                    score += 1
        
        # Prepare details
        details = {
            'note': 'This is a proxy score based on supply metrics and community size.'
        }
        
        if market_data:
            if 'circulating_supply' in market_data and 'total_supply' in market_data and market_data.get('total_supply'):
                circulation_ratio = market_data['circulating_supply'] / market_data['total_supply']
                details['circulation_ratio'] = f"{round(circulation_ratio * 100, 2)}%"
        
        if community and 'twitter_followers' in community:
            details['twitter_followers'] = community['twitter_followers']
        
        return {
            'score': min(score, self.max_score),
            'details': details
        }

def print_result(result):
    """Print indicator result in a formatted way"""
    print(f"\n{'=' * 50}")
    print(f"INDICATOR: {result['indicator']}")
    print(f"{'=' * 50}")
    print(f"Symbol: {result['symbol']}")
    print(f"Score: {result['score']:.2f}/{result['max_score']:.2f} ({result['score']/result['max_score']*100:.1f}%)")
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
    elif 'details' in result:
        print("\nDetails:")
        for key, value in result['details'].items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")

def main():
    """Main entry point"""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 test_indicators.py <symbol>")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    print(f"Testing indicators for {symbol} with mock data")
    
    # Create data provider
    data_provider = MockDataProvider()
    
    # Import our enhanced indicators
    try:
        from src.Analyse.Technical.pre_sale_vesting import PreSaleVestingIndicator
        from src.Analyse.Technical.smart_contract_audit import SmartContractAuditIndicator
        has_enhanced_indicators = True
    except ImportError:
        # Fallback to local imports if running outside the project structure
        logger.warning("Enhanced indicators not found, using only basic indicators")
        has_enhanced_indicators = False
    
    # Create indicators
    indicators = [
        TradingVolumeIndicator(data_provider),
        LiquidityIndicator(data_provider),
        WhaleTransactionsIndicator(data_provider),
        TokenDistributionIndicator(data_provider)
    ]
    
    # Add enhanced indicators if available
    if has_enhanced_indicators:
        indicators.extend([
            PreSaleVestingIndicator(data_provider),
            SmartContractAuditIndicator(data_provider)
        ])
    
    # Run indicators
    results = []
    for indicator in indicators:
        result = indicator.calculate(symbol)
        results.append(result)
        print_result(result)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_score = sum(r['score'] for r in results)
    max_score = sum(r['max_score'] for r in results)
    
    print(f"Symbol: {symbol}")
    print(f"Total Score: {total_score:.2f}/{max_score:.2f} ({total_score/max_score*100:.1f}%)")
    
    for result in results:
        print(f"  {result['indicator']}: {result['score']:.2f}/{result['max_score']:.2f} ({result['score']/result['max_score']*100:.1f}%)")

if __name__ == "__main__":
    main()
