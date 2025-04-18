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
    SocialVolumeIndicator,
    SentimentAnalysisIndicator,
    DeveloperActivityIndicator,
    CommunityGrowthIndicator,
    GoogleTrendsIndicator
)
from Analyse.indicator_runner import IndicatorRunner
from utils.db import create_tables
from utils.analysis_db import create_analysis_table, save_analysis_results, get_latest_analysis
from utils.social_db import create_social_table, save_social_results, get_latest_social

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pumptandump")

def print_result(result):
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
            else: print(f"  {k}: {v}")


def run_analysis(args, verbose: bool):
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
        SocialVolumeIndicator(data_provider=data_provider),
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
        print("=== TECHNICAL INDICATORS ===")
        technical_result = runner.run_all_indicators(technical_indicators, symbol)
        for result in technical_result:
            print_result(result)
        technical_results.extend(technical_result)
        
        # Run social indicators
        print("\n=== SOCIAL INDICATORS ===")
        social_result = runner.run_all_indicators(social_indicators, symbol)
        for result in social_result:
            print_result(result)
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
    an.add_argument('--save', action='store_true', help='Save to DB')
    rp = sub.add_parser('report', help='View saved')
    rp.add_argument('--symbol', help='Symbol to filter')
    args = parser.parse_args()

    create_analysis_table()
    create_social_table()

    if args.cmd == 'analyze':
        tech, social = run_analysis(args, args.verbose)
        if args.save:
            save_analysis_results(tech, args.symbol)
            save_social_results(social, args.symbol)
    elif args.cmd == 'report':
        ta = get_latest_analysis(symbol=args.symbol)
        sa = get_latest_social(symbol=args.symbol)
        print("\n=== ANALYSIS HISTORY ===")
        print(tabulate([list(t.values()) for t in ta], headers=ta[0].keys() if ta else []))
        print("\n=== SOCIAL HISTORY ===")
        print(tabulate([list(s.values()) for s in sa], headers=sa[0].keys() if sa else []))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
