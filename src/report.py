#!/usr/bin/env python3
"""
Report - View cryptocurrency analysis results stored in the database.

This script retrieves and displays previously saved analysis results,
allowing you to view historical data and track cryptocurrency performance over time.

Usage:
    python report.py [--symbol BTC] [--days 7] [--limit 10]
"""
import os
import sys
import argparse
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from tabulate import tabulate
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("report")

# Load environment variables
load_dotenv()

# Database connection parameters from environment variables
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

def get_connection():
    """Get a connection to the database."""
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def get_latest_analysis(symbol=None, days=7, limit=10):
    """
    Get the latest analysis results from the database.
    
    Args:
        symbol: Optional cryptocurrency symbol to filter by
        days: Number of days to look back
        limit: Maximum number of results to return
    
    Returns:
        List of analysis results
    """
    table = os.getenv('POSTGRES_ANALYSIS_TABLE', 'crypto_analysis')
    
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if symbol:
                query = f"""
                SELECT 
                    symbol, 
                    analysis_date, 
                    total_score, 
                    recommendation,
                    trading_volume_score,
                    liquidity_score,
                    whale_transactions_score,
                    token_distribution_score,
                    pre_sale_vesting_score,
                    smart_contract_audit_score
                FROM {table}
                WHERE symbol = %s
                AND analysis_date > %s
                ORDER BY analysis_date DESC
                LIMIT %s
                """
                cur.execute(query, (
                    symbol, 
                    datetime.now() - timedelta(days=days),
                    limit
                ))
            else:
                query = f"""
                SELECT 
                    symbol, 
                    analysis_date, 
                    total_score, 
                    recommendation,
                    trading_volume_score,
                    liquidity_score,
                    whale_transactions_score,
                    token_distribution_score,
                    pre_sale_vesting_score,
                    smart_contract_audit_score
                FROM {table}
                WHERE analysis_date > %s
                ORDER BY analysis_date DESC
                LIMIT %s
                """
                cur.execute(query, (
                    datetime.now() - timedelta(days=days),
                    limit
                ))
            
            results = cur.fetchall()
            conn.close()
            return results
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {e}")
        return []

def display_technical_results(results):
    """
    Display analysis results in a table format.
    
    Args:
        results: List of analysis results
    """
    if not results:
        print("No analysis results found.")
        return
    
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
    
    rows = []
    for r in results:
        # Calculate percentage on-the-fly
        percentage = (r['total_score'] / TOTAL_MAX_SCORE) * 100
        
        rows.append([
            r['symbol'],
            r['analysis_date'].strftime('%Y-%m-%d %H:%M'),
            f"{percentage:.1f}%",
            r['recommendation'],
            f"{r['trading_volume_score']:.1f}",
            f"{r['liquidity_score']:.1f}",
            f"{r['whale_transactions_score']:.1f}",
            f"{r['token_distribution_score']:.1f}",
            f"{r['pre_sale_vesting_score']:.1f}",
            f"{r['smart_contract_audit_score']:.1f}"
        ])
    
    # Display the table
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def display_social_results(results):
    """
    Display social results in a table format.
    
    Args:
        results: List of social results
    """
    if not results:
        print("No social results found.")
        return
    
    # Prepare data for tabulation
    headers = [
        "Symbol", 
        "Date", 
        "Volume",
        "Sentiment",
        "Developer"
    ]
    
    rows = []
    for r in results:
        rows.append([
            r['symbol'],
            r['analysis_date'].strftime('%Y-%m-%d %H:%M'),
            f"{r.get('social_volume_score', 0):.1f}",
            f"{r.get('sentiment_analysis_score', 0):.1f}",
            f"{r.get('developer_activity_score', 0):.1f}"
        ])
    
    # Display the table
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def main():
    """Main function to run the report"""
    parser = argparse.ArgumentParser(description='View cryptocurrency analysis results')
    parser.add_argument('--symbol', help='Cryptocurrency symbol to filter by')
    parser.add_argument('--days', type=int, help='Number of days to look back')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of results to show')
    parser.add_argument('--social', action='store_true', help='Show social indicators instead of technical')
    args = parser.parse_args()
    
    # Get the latest analysis results
    if args.social:
        results = get_latest_social(args.symbol, args.days, args.limit)
        display_social_results(results)
    else:
        results = get_latest_analysis(args.symbol, args.days, args.limit)
        display_technical_results(results)

if __name__ == "__main__":
    main()
