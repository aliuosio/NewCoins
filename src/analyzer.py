#!/usr/bin/env python3
"""
Analyzer - Analyze cryptocurrencies using the PumpAndDump indicator system.

This script fetches data from CoinGecko API, runs multiple technical indicators,
and provides a comprehensive analysis with scores and recommendations.
Results can be saved to the database for historical tracking.

Usage:
    python analyzer.py BTC,ETH,SOL [--verbose] [--save] [--mock]
"""
import argparse
import logging
import sys
import json
import time
import os
from typing import Dict, Any, List
from tabulate import tabulate
from datetime import datetime, timedelta

from Analyse.Technical import (
    TradingVolumeIndicator,
    LiquidityIndicator,
    WhaleTransactionsIndicator,
    TokenDistributionIndicator,
    PreSaleVestingIndicator,
    SmartContractAuditIndicator
)

from Analyse.Social import (
    SocialVolumeIndicator,
    SentimentAnalysisIndicator,
    DeveloperActivityIndicator
)

from Analyse import IndicatorRunner

# Import database utilities
from utils.analysis_db import create_analysis_table, save_analysis_results, get_latest_analysis
from utils.social_db import create_social_table, save_social_results, get_latest_social

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("analyzer")

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

def run_analysis(symbol, verbose, mock, social):
    """Run analysis for a symbol"""
    # Create data provider
    if mock:
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
    technical_indicators = [
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
    
    social_indicators = [
        SocialVolumeIndicator(data_provider),
        SentimentAnalysisIndicator(data_provider),
        DeveloperActivityIndicator(data_provider)
    ]
    
    # Always include both technical and social indicators
    indicators = technical_indicators + social_indicators
    
    # Create indicator runner
    runner = IndicatorRunner()
    
    # Run indicators for this symbol
    results = runner.run_all_indicators(indicators, symbol)
    
    # Skip printing detailed results unless verbose mode is enabled
    if verbose:
        for result in results:
            print_result(result)
    
    return results

def display_technical_results(results):
    """Display technical analysis results in a table"""
    if not results:
        print("No technical analysis results found.")
        return
        
    # Define max scores for each indicator
    MAX_SCORES = {
        'trading_volume': 15.0,
        'liquidity': 15.0,
        'whale_transactions': 10.0,
        'token_distribution': 10.0,
        'pre_sale_vesting': 10.0,
        'smart_contract_audit': 10.0
    }
    TOTAL_MAX_SCORE = 70.0
    
    # Prepare data for tabulation
    headers = [
        "Symbol", 
        "Date", 
        "Score", 
        "Recommendation",
        "Volume",
        "Liquidity",
        "Whales",
        "Distribution",
        "Vesting",
        "Audit"
    ]
    
    rows = []
    for r in results:
        # Calculate percentage on-the-fly
        percentage = (r['total_score'] / TOTAL_MAX_SCORE) * 100
        
        rows.append([
            r['symbol'],
            r['analysis_date'].strftime('%Y-%m-%d %H:%M'),
            f"{percentage:.1f}%",
            r['recommendation'],
            f"{r.get('trading_volume_score', 0):.1f}",
            f"{r.get('liquidity_score', 0):.1f}",
            f"{r.get('whale_transactions_score', 0):.1f}",
            f"{r.get('token_distribution_score', 0):.1f}",
            f"{r.get('pre_sale_vesting_score', 0):.1f}",
            f"{r.get('smart_contract_audit_score', 0):.1f}"
        ])
    
    # Display the table
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def display_social_results(results):
    """Display social analysis results in a table"""
    if not results:
        print("No social analysis results found.")
        return
    
    # Prepare data for tabulation
    headers = [
        "Symbol", 
        "Date", 
        "Total",
        "Volume",
        "Sentiment",
        "Developer"
    ]
    
    rows = []
    for r in results:
        rows.append([
            r['symbol'],
            r['analysis_date'].strftime('%Y-%m-%d %H:%M'),
            f"{r.get('total_social_score', 0):.1f}",
            f"{r.get('social_volume_score', 0):.1f}",
            f"{r.get('sentiment_analysis_score', 0):.1f}",
            f"{r.get('developer_activity_score', 0):.1f}"
        ])
    
    # Display the table
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def main():
    """Main function to run the analysis or view reports"""
    parser = argparse.ArgumentParser(description='Analyze cryptocurrencies or view saved results')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze cryptocurrencies')
    analyze_parser.add_argument('symbol', help='Cryptocurrency symbol(s) to analyze (comma-separated)')
    analyze_parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    analyze_parser.add_argument('--save', action='store_true', help='Save results to database')
    analyze_parser.add_argument('--mock', action='store_true', help='Use mock data for testing')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='View saved analysis results')
    report_parser.add_argument('--symbol', help='Cryptocurrency symbol to filter by')
    report_parser.add_argument('--days', type=int, default=7, help='Number of days to look back')
    report_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results to show')
    report_parser.add_argument('--type', choices=['technical', 'social', 'all'], default='all', 
                            help='Type of indicators to show (technical, social, or all)')
    args = parser.parse_args()
    
    # Handle different commands
    if args.command == 'analyze':
        # Split the symbols by comma and convert to uppercase
        symbols = [s.strip().upper() for s in args.symbol.split(',')]
        
        # Process each symbol
        for symbol in symbols:
            try:
                # Run the analysis
                results = run_analysis(symbol, args.verbose, args.mock, args.social)
                
                # Save results to database if requested
                if args.save:
                    try:
                        # Save technical analysis results
                        create_analysis_table()
                        technical_results = [r for r in results if r.indicator_name in 
                                        [i.name for i in technical_indicators]]
                        save_analysis_results(technical_results, symbol)
                        logger.info(f"Technical analysis results for {symbol} saved to database")
                        
                        # Save social analysis results
                        create_social_table()
                        social_results = [r for r in results if r.indicator_name in 
                                     [i.name for i in social_indicators]]
                        save_social_results(social_results, symbol)
                        logger.info(f"Social analysis results for {symbol} saved to database")
                    except Exception as e:
                        logger.error(f"Failed to save analysis results: {e}")
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                print(f"Error analyzing {symbol}: {e}")
    
    elif args.command == 'report':
        # Get analysis results based on report type
        if args.type == 'social':
            results = get_latest_social(symbol=args.symbol, limit=args.limit)
            display_social_results(results)
        elif args.type == 'technical':
            results = get_latest_analysis(symbol=args.symbol, limit=args.limit)
            display_technical_results(results)
        else:  # 'all'
            # Show both technical and social results
            tech_results = get_latest_analysis(symbol=args.symbol, limit=args.limit)
            social_results = get_latest_social(symbol=args.symbol, limit=args.limit)
            
            print("\n=== TECHNICAL INDICATORS ===")
            display_technical_results(tech_results)
            
            print("\n=== SOCIAL INDICATORS ===")
            display_social_results(social_results)
    
    else:
        # If no command is specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()
