#!/usr/bin/env python3
"""
View cryptocurrency analysis results stored in the database.
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
logger = logging.getLogger("view_analysis")

# Database connection parameters
DB_PARAMS = {
    'dbname': 'pumpanddump',
    'user': 'SpecialOsio',
    'password': 'oeh_ahb6Ahzah7exeish',
    'host': 'postgres',
    'port': '5432'
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

def display_results(results):
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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='View cryptocurrency analysis results from the database')
    parser.add_argument('--symbol', type=str, help='Symbol of the cryptocurrency to view (e.g., BTC)')
    parser.add_argument('--days', type=int, default=7, help='Number of days to look back')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of results to return')
    args = parser.parse_args()
    
    # Get the latest analysis results
    results = get_latest_analysis(args.symbol, args.days, args.limit)
    
    # Display the results
    display_results(results)

if __name__ == "__main__":
    main()
