#!/usr/bin/env python3
"""
Main script for testing indicators without writing to the database.
"""
import os
import sys
import logging
import argparse
from typing import List
from dotenv import load_dotenv

from .data_providers import CoinGeckoProvider, MockDataProvider
from .indicators import TradingVolumeIndicator, MarketCapIndicator, PriceStabilityIndicator
from .indicator_runner import IndicatorRunner
from .interfaces import IIndicator


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_indicators(data_provider) -> List[IIndicator]:
    """
    Create all available indicators
    
    Args:
        data_provider: Data provider to use for all indicators
        
    Returns:
        List of indicator instances
    """
    return [
        TradingVolumeIndicator(data_provider),
        MarketCapIndicator(data_provider),
        PriceStabilityIndicator(data_provider)
    ]


def print_result(result):
    """
    Print indicator result in a formatted way
    
    Args:
        result: Indicator result to print
    """
    print(f"\n{'=' * 50}")
    print(f"INDICATOR: {result.indicator_name}")
    print(f"{'=' * 50}")
    print(f"Symbol: {result.symbol}")
    print(f"Score: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")
    
    if not result.success:
        print(f"ERROR: {result.error}")
    else:
        print("\nDetails:")
        for key, value in result.details.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")
    
    if result.execution_time_ms is not None:
        print(f"\nExecution time: {result.execution_time_ms}ms")


def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    setup_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test cryptocurrency indicators')
    parser.add_argument('symbol', help='Cryptocurrency symbol (e.g., BTC, ETH)')
    parser.add_argument('--mock', action='store_true', help='Use mock data instead of real API')
    parser.add_argument('--indicator', help='Run only this specific indicator')
    args = parser.parse_args()
    
    # Create data provider
    if args.mock:
        data_provider = MockDataProvider()
        print(f"Using MOCK data provider for {args.symbol}")
    else:
        data_provider = CoinGeckoProvider()
        print(f"Using CoinGecko data provider for {args.symbol}")
    
    # Create indicators
    all_indicators = create_indicators(data_provider)
    
    # Filter indicators if specified
    if args.indicator:
        indicators = [ind for ind in all_indicators if ind.name.lower() == args.indicator.lower()]
        if not indicators:
            print(f"Error: Indicator '{args.indicator}' not found")
            print(f"Available indicators: {', '.join(ind.name for ind in all_indicators)}")
            return
    else:
        indicators = all_indicators
    
    # Create runner
    runner = IndicatorRunner()
    
    # Run indicators
    results = runner.run_all_indicators(indicators, args.symbol)
    
    # Print results
    for result in results:
        print_result(result)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_score = sum(r.score for r in results)
    max_score = sum(r.max_score for r in results)
    
    print(f"Symbol: {args.symbol}")
    print(f"Total Score: {total_score:.2f}/{max_score:.2f} ({total_score/max_score*100:.1f}%)")
    
    for result in results:
        print(f"  {result.indicator_name}: {result.score:.2f}/{result.max_score:.2f} ({result.score/result.max_score*100:.1f}%)")


if __name__ == "__main__":
    main()
