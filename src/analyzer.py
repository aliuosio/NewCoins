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

def run_analysis(symbol, verbose):
    """Run analysis for a symbol"""
    # Create data provider
    api_key = os.getenv('COINGECKO_API_KEY', '')
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
                results = run_analysis(symbol, args.verbose)
                
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
