#!/usr/bin/env python3
"""
Main CLI for PumpAndDump analysis (technical + social indicators).
"""
import sys
import os
import logging
import argparse
import datetime
from typing import List
from tabulate import tabulate

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
from load_env import load_environment_variables
load_environment_variables()

import argparse
from Analyse.data_providers import CoinGeckoProvider
from Analyse.Technical import (
    TradingVolumeIndicator,
    LiquidityIndicator,
    WhaleTransactionsIndicator,
    TokenDistributionIndicator,
    PreSaleVestingIndicator,
    SmartContractAuditIndicator
)
from Analyse.Social import (
    SentimentAnalysisIndicator,
    DeveloperActivityIndicator,
    CommunityGrowthIndicator,
    GoogleTrendsIndicator
)
from Analyse.indicator_runner import IndicatorRunner
from utils.db import create_tables
from utils.analysis_db import create_technical_indicators_table, save_analysis_results, get_latest_analysis
from utils.social_db import create_social_indicators_table, save_social_results, get_latest_social
from utils.analysis_view import create_analysis_view

# Configure logging
# Default to WARNING level to reduce output in normal mode
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pumptandump")

# Set specific loggers to higher levels to reduce noise
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pytrends").setLevel(logging.ERROR)
logging.getLogger("praw").setLevel(logging.WARNING)

def print_result(result, verbose=False):
    if verbose:
        # Detailed output for verbose mode
        print(f"\n{'=' * 50}")
        print(f"INDICATOR: {result.indicator_name}")
        print(f"{'=' * 50}")
        print(f"Symbol: {result.symbol}")
        print(f"Score: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")
        if hasattr(result, 'error') and result.error:
            print(f"ERROR: {result.error}")
        else:
            print("\nDetails:")
            for k, v in result.details.items():
                if isinstance(v, dict):
                    print(f"  {k}:")
                    for kk, vv in v.items(): print(f"    {kk}: {vv}")
                elif isinstance(v, list):
                    print(f"  {k}:")
                    for item in v: print(f"    - {item}")
                else:
                    print(f"  {k}: {v}")
    else:
        # Concise output for normal mode
        print(f"\n{result.indicator_name}: {result.score:.1f}/{result.max_score:.1f} ({result.score/result.max_score*100:.1f}%)")
        if hasattr(result, 'error') and result.error:
            print(f"  ERROR: {result.error}")


def run_analysis(args, verbose: bool):
    # Set logging level based on verbose flag
    if verbose:
        # In verbose mode, set main loggers to INFO level
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("pumptandump").setLevel(logging.INFO)
        logging.getLogger("indicator_runner").setLevel(logging.INFO)
        logging.getLogger("data_provider").setLevel(logging.INFO)
    else:
        # In normal mode, keep most loggers at WARNING level
        # Only set essential loggers to INFO
        logging.getLogger("pumptandump").setLevel(logging.INFO)
    
    # Create data provider and indicator instances
    data_provider = CoinGeckoProvider()
    
    # Create indicators
    technical_indicators = [
        TradingVolumeIndicator(data_provider=data_provider),
        LiquidityIndicator(data_provider=data_provider),
        WhaleTransactionsIndicator(data_provider=data_provider),
        TokenDistributionIndicator(data_provider=data_provider),
        PreSaleVestingIndicator(data_provider=data_provider),
        SmartContractAuditIndicator(data_provider=data_provider)
    ]
    
    social_indicators = [
        SentimentAnalysisIndicator(data_provider=data_provider),
        DeveloperActivityIndicator(data_provider=data_provider),
        CommunityGrowthIndicator(data_provider=data_provider),
        GoogleTrendsIndicator(data_provider=data_provider)
    ]
    
    runner = IndicatorRunner()
    
    # Split comma-separated symbols and flatten the list
    all_symbols = []
    for symbol in args.symbols:
        all_symbols.extend(symbol.split(','))
    
    # Remove duplicates and sort
    all_symbols = sorted(set(all_symbols))
    
    # Run indicators for each symbol
    technical_results = []
    social_results = []
    for symbol in all_symbols:
        print(f"\n=== RESULTS FOR {symbol} ===\n")
        
        # Run technical indicators
        print("=== TECHNICAL INDICATORS ===" if verbose else "TECHNICAL INDICATORS:")
        technical_result = runner.run_all_indicators(technical_indicators, symbol)
        for result in technical_result:
            print_result(result, verbose)
        technical_results.extend(technical_result)
        
        # Run social indicators
        print("\n=== SOCIAL INDICATORS ===" if verbose else "\nSOCIAL INDICATORS:")
        social_result = runner.run_all_indicators(social_indicators, symbol)
        for result in social_result:
            print_result(result, verbose)
        social_results.extend(social_result)
        
        print("\n")
    
    return technical_results, social_results


def main():
    # Ensure base tables exist (coins)
    create_tables()
    parser = argparse.ArgumentParser(description='PumpAndDump application')
    sub = parser.add_subparsers(dest='cmd')
    an = sub.add_parser('analyze', help='Run analysis')
    an.add_argument('symbols', nargs='+', help='Cryptocurrency symbol(s) to analyze (comma-separated)')
    an.add_argument('--verbose', action='store_true', help='Detailed output')
    rp = sub.add_parser('report', help='View saved analysis')
    rp.add_argument('symbols', nargs='*', help='Cryptocurrency symbol(s) to view (optional)')
    args = parser.parse_args()

    # Create tables first
    create_technical_indicators_table()
    create_social_indicators_table()
    
    # Create view after tables are created
    create_analysis_view()

    if args.cmd == 'analyze':
        tech, social = run_analysis(args, args.verbose)
        # Always save results to database
        symbol = args.symbols[0]
        save_analysis_results(tech, symbol)
        save_social_results(social, symbol)
    elif args.cmd == 'report':
        # If no symbols specified, get all analyses
        if not args.symbols:
            ta = get_latest_analysis()
            sa = get_latest_social()
        else:
            # Get analysis for specified symbols
            ta = get_latest_analysis(symbols=args.symbols)
            sa = get_latest_social(symbols=args.symbols)
        print("\n=== ANALYSIS HISTORY ===")
        print(tabulate([list(t.values()) for t in ta], headers=ta[0].keys() if ta else []))
        print("\n=== SOCIAL HISTORY ===")
        print(tabulate([list(s.values()) for s in sa], headers=sa[0].keys() if sa else []))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
