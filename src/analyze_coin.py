#!/usr/bin/env python3
"""
Analyze a cryptocurrency using the PumpAndDump indicator system.
This script uses real data from CoinGecko to evaluate a cryptocurrency.
"""
import sys
import logging
import argparse
import os
from typing import Dict, Any, List

from Analyse import (
    CoinGeckoProvider, 
    TradingVolumeIndicator, 
    LiquidityIndicator, 
    WhaleTransactionsIndicator, 
    TokenDistributionIndicator,
    PreSaleVestingIndicator,
    SmartContractAuditIndicator,
    IndicatorRunner
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("analyze_coin")

def print_result(result):
    """Print indicator result in a formatted way"""
    print(f"\n{'=' * 50}")
    print(f"INDICATOR: {result.indicator_name}")
    print(f"{'=' * 50}")
    print(f"Symbol: {result.symbol}")
    print(f"Score: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")
    
    if hasattr(result, 'error') and result.error:
        print(f"ERROR: {result.error}")
    else:
        print("\nDetails:")
        for key, value in result.details.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze cryptocurrencies using the PumpAndDump indicator system')
    parser.add_argument('symbols', type=str, help='Symbol(s) of the cryptocurrency to analyze (e.g., BTC or BTC,ETH,SOL)')
    parser.add_argument('--mock', action='store_true', help='Use mock data instead of real data')
    parser.add_argument('--save', action='store_true', help='Save results to database')
    parser.add_argument('--verbose', action='store_true', help='Show detailed results for each indicator')
    args = parser.parse_args()
    
    # Split the symbols by comma and convert to uppercase
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    use_mock = args.mock
    save_to_db = args.save
    
    print(f"Analyzing {', '.join(symbols)} with {'mock' if use_mock else 'real'} data")
    
    # Create data provider
    if use_mock:
        # Create a more comprehensive mock data provider
        class ComprehensiveMockDataProvider:
            """Mock data provider with realistic test data for all indicators"""
            
            def __init__(self):
                """Initialize the mock data provider"""
                self.name = "comprehensive_mock"
            
            def get_data(self, symbol: str) -> Dict[str, Any]:
                """Return comprehensive mock data for the symbol"""
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
                            'reddit_subscribers': 50000
                        }
                    },
                    # For whale transactions and liquidity
                    'market_chart': True,
                    
                    # Smart contract audit data
                    'contract_age_days': 365,  # 1 year old contract
                    'audits': [
                        {'firm': 'Certik', 'date': '2024-01-15', 'score': 9.2},
                        {'firm': 'PeckShield', 'date': '2023-10-20', 'score': 8.8}
                    ],
                    'critical_vulnerabilities': 0,
                    'major_vulnerabilities': 1,
                    'vulnerabilities_fixed': 1,
                    
                    # Pre-sale vesting data
                    'upcoming_unlocks': [
                        {'date': '2025-06-01', 'percentage': 3.0, 'tokens': 3000000}
                    ],
                    'days_to_next_unlock': 45,
                    'next_unlock_percentage': 3.0,
                    'total_unlocks_30_days': 0,
                    'total_percentage_30_days': 0.0
                }
        
        data_provider = ComprehensiveMockDataProvider()
    else:
        # Get API key from environment variable
        api_key = os.environ.get('COINGECKO_API_KEY')
        data_provider = CoinGeckoProvider(api_key=api_key)
    
    # Create indicators
    indicators = [
        # Market indicators
        TradingVolumeIndicator(data_provider),
        LiquidityIndicator(data_provider),
        
        # Whale activity indicators
        WhaleTransactionsIndicator(data_provider),
        
        # Tokenomics indicators
        TokenDistributionIndicator(data_provider),
        PreSaleVestingIndicator(data_provider),
        
        # Security indicators
        SmartContractAuditIndicator(data_provider)
    ]
    
    # Create indicator runner
    runner = IndicatorRunner()
    
    # Process each symbol
    for symbol in symbols:
        print(f"\n\n{'#' * 70}")
        print(f"# ANALYZING {symbol}")
        print(f"{'#' * 70}")
        
        # Run indicators for this symbol
        results = runner.run_all_indicators(indicators, symbol)
        
        # Skip printing detailed results unless verbose mode is enabled
        if args.verbose:
            for result in results:
                print_result(result)
        
        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        total_score = sum(r.score for r in results)
        max_score = sum(r.max_score for r in results)
        
        print(f"Symbol: {symbol}")
        print(f"Total Score: {total_score:.2f}/{max_score:.2f} ({total_score/max_score*100:.1f}%)")
        
        for result in results:
            print(f"  {result.indicator_name}: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")
        
        # Return a recommendation based on the score
        percentage = total_score / max_score * 100 if max_score > 0 else 0
        if percentage >= 80:
            print("\nRECOMMENDATION: STRONG BUY - High potential for growth")
        elif percentage >= 70:
            print("\nRECOMMENDATION: BUY - Good potential for growth")
        elif percentage >= 60:
            print("\nRECOMMENDATION: HOLD - Moderate potential")
        elif percentage >= 50:
            print("\nRECOMMENDATION: WATCH - Some concerns")
        else:
            print("\nRECOMMENDATION: AVOID - Significant concerns")

if __name__ == "__main__":
    main()
