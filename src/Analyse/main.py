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
from utils.analysis_db import save_analysis_results, get_latest_analysis, save_analysis_results_batch
from utils.social_db import save_social_results, get_latest_social, save_social_results_batch
from utils.analysis_view import get_latest_analysis

# Configure logging
# Default to INFO level, but allow debug level if requested
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pumptandump")

# Set specific loggers to higher levels to reduce noise
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pytrends").setLevel(logging.ERROR)
logging.getLogger("praw").setLevel(logging.WARNING)

def parse_symbols(symbol_args: list) -> list:
    """Parse and deduplicate comma-separated symbols from CLI arguments."""
    all_symbols = []
    for symbol in symbol_args:
        all_symbols.extend(symbol.split(','))
    return sorted(set(all_symbols))

def create_technical_indicators(data_provider):
    """Factory for technical indicators list."""
    return [
        TradingVolumeIndicator(data_provider=data_provider),
        LiquidityIndicator(data_provider=data_provider),
        WhaleTransactionsIndicator(data_provider=data_provider),
        TokenDistributionIndicator(data_provider=data_provider),
        PreSaleVestingIndicator(data_provider=data_provider),
        SmartContractAuditIndicator(data_provider=data_provider)
    ]

def create_social_indicators(data_provider):
    """Factory for social indicators list."""
    return [
        SentimentAnalysisIndicator(data_provider=data_provider),
        DeveloperActivityIndicator(data_provider=data_provider),
        CommunityGrowthIndicator(data_provider=data_provider),
        GoogleTrendsIndicator(data_provider=data_provider)
    ]

def group_results_by_symbol(results, indicators, symbols):
    """Group indicator results by symbol."""
    grouped = {}
    idx = 0
    for symbol in symbols:
        grouped[symbol] = results[idx:idx+len(indicators)]
        idx += len(indicators)
    return grouped

# Function to set debug level if needed
def set_debug_level(debug: bool):
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("indicator_runner").setLevel(logging.DEBUG)
        logging.getLogger("whale_transactions").setLevel(logging.DEBUG)
        print("\n=== DEBUG MODE ENABLED ===")

def print_result(result, verbose=False, debug=False):
    # Safety check - print the structure of the result object
    logger.debug(f"Result for {result.indicator_name}: {vars(result)}")
    
    # Check if score is None, which indicates not applicable
    score_is_none = result.score is None
    
    # Check if the indicator is explicitly marked as not applicable
    explicitly_not_applicable = hasattr(result, 'not_applicable') and result.not_applicable
    
    # Combined check for not applicable status
    not_applicable = score_is_none or explicitly_not_applicable
    
    # Always show debug output if debug flag is set
    if debug:
        print(f"\nDEBUG DETAILS FOR {result.indicator_name}")
        if not_applicable:
            print(f"Status: Not Applicable")
        else:
            print(f"Score: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")
        if hasattr(result, 'details') and isinstance(result.details, dict):
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
        print("\n")
    
    if verbose:
        # Detailed output for verbose mode
        print(f"\n{'=' * 50}")
        print(f"INDICATOR: {result.indicator_name}")
        print(f"{'=' * 50}")
        print(f"Symbol: {result.symbol}")
        if not_applicable:
            print(f"Status: Not Applicable")
            if hasattr(result, 'message'):
                print(f"Message: {result.message}")
        else:
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
        if not_applicable:
            print(f"\n{result.indicator_name}: N/A (Not Applicable)")
            if hasattr(result, 'message'):
                print(f"  Note: {result.message}")
        else:
            print(f"\n{result.indicator_name}: {result.score:.1f}/{result.max_score:.1f} ({result.score/result.max_score*100:.1f}%)")
            if hasattr(result, 'error') and result.error:
                print(f"  ERROR: {result.error}")


# Create data provider and indicator runner
# Indicator lists are now created as needed using factories
runner = IndicatorRunner()

def run_analysis(args, verbose=False, debug=False):
    """Run technical and social indicators for all provided symbols."""
    # Set logging level based on verbose flag
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("pumptandump").setLevel(logging.INFO)
        logging.getLogger("indicator_runner").setLevel(logging.INFO)
        logging.getLogger("data_provider").setLevel(logging.INFO)
    else:
        logging.getLogger("pumptandump").setLevel(logging.INFO)
    
    all_symbols = parse_symbols(args.symbols)
    data_provider = CoinGeckoProvider()
    technical_indicators = create_technical_indicators(data_provider)
    social_indicators = create_social_indicators(data_provider)

    technical_results = []
    social_results = []
    for symbol in all_symbols:
        print(f"\n=== RESULTS FOR {symbol} ===\n")
        print("=== TECHNICAL INDICATORS ===" if verbose else "TECHNICAL INDICATORS:")
        technical_result = runner.run_all_indicators(technical_indicators, symbol)
        for result in technical_result:
            print_result(result, verbose)
        technical_results.extend(technical_result)
        print("\n=== SOCIAL INDICATORS ===" if verbose else "\nSOCIAL INDICATORS:")
        social_result = runner.run_all_indicators(social_indicators, symbol)
        for result in social_result:
            print_result(result, verbose)
        social_results.extend(social_result)
        print("\n")
    return technical_results, social_results


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    from utils.db import DBConnection
    
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = %s
    );
    """
    
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (table_name,))
            return cur.fetchone()[0]

def main():
    """Main entry point for the PumpAndDump analysis CLI."""
    # Ensure DB tables exist
    if not check_table_exists('analyse_technical'):
        create_tables()
        # The analysis view is now created by Docker initialization scripts

    parser = argparse.ArgumentParser(description='PumpAndDump application')
    sub = parser.add_subparsers(dest='cmd')
    an = sub.add_parser('analyze', help='Run analysis')
    an.add_argument('symbols', nargs='+', help='Cryptocurrency symbol(s) to analyze (comma-separated)')
    an.add_argument('--verbose', action='store_true', help='Detailed output')
    an.add_argument('--debug', action='store_true', help='Show debug information')
    args = parser.parse_args()

    if args.cmd == 'analyze':
        tech, social = run_analysis(args, args.verbose, args.debug)
        all_symbols = parse_symbols(args.symbols)
        data_provider = CoinGeckoProvider()
        technical_indicators = create_technical_indicators(data_provider)
        social_indicators = create_social_indicators(data_provider)
        tech_results_dict = group_results_by_symbol(tech, technical_indicators, all_symbols)
        social_results_dict = group_results_by_symbol(social, social_indicators, all_symbols)
        save_analysis_results_batch(tech_results_dict)
        save_social_results_batch(social_results_dict)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
