#!/usr/bin/env python3
"""
Main CLI for PumpAndDump analysis (technical + social indicators).
"""
import argparse
import os
import sys
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List
from tabulate import tabulate
from datetime import datetime

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


def run_analysis(symbol: str, verbose: bool):
    # Prepare indicators and runner
    provider = None
    from Analyse.data_providers import CoinGeckoProvider
    provider = CoinGeckoProvider(api_key=os.getenv('COINGECKO_API_KEY',''))
    tech = [TradingVolumeIndicator(provider), LiquidityIndicator(provider), WhaleTransactionsIndicator(provider), TokenDistributionIndicator(provider), PreSaleVestingIndicator(provider), SmartContractAuditIndicator(provider)]
    social = [SocialVolumeIndicator(provider), SentimentAnalysisIndicator(provider), DeveloperActivityIndicator(provider)]
    runner = IndicatorRunner()
    # Run technical
    tech_results = runner.run_all_indicators(tech, symbol)
    # Run social
    social_results = runner.run_all_indicators(social, symbol)
    # Print
    print("\n=== TECHNICAL INDICATORS ===")
    for r in tech_results: print_result(r) if verbose else print(f"{r.indicator_name}: {r.score:.2f}/{r.max_score:.2f}")
    print("\n=== SOCIAL INDICATORS ===")
    for r in social_results: print_result(r) if verbose else print(f"{r.indicator_name}: {r.score:.2f}/{r.max_score:.2f}")
    return tech_results, social_results


def main():
    # Ensure base tables exist (coins)
    create_tables()
    parser = argparse.ArgumentParser(description='PumpAndDump cryptocurrency analysis')
    sub = parser.add_subparsers(dest='cmd')
    an = sub.add_parser('analyze', help='Run analysis')
    an.add_argument('symbol', help='Symbol(s), comma-separated')
    an.add_argument('--verbose', action='store_true', help='Detailed output')
    an.add_argument('--save', action='store_true', help='Save to DB')
    rp = sub.add_parser('report', help='View saved')
    rp.add_argument('--symbol', help='Symbol to filter')
    args = parser.parse_args()

    create_analysis_table()
    create_social_table()

    if args.cmd == 'analyze':
        tech, social = run_analysis(args.symbol, args.verbose)
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
