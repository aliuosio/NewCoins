#!/usr/bin/env python3
"""
Database utilities for saving cryptocurrency social indicators data.
"""
import os
import json
import logging
import psycopg2
from psycopg2.extras import execute_values, Json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .db import DBConnection

logger = logging.getLogger("social_db")

# Table creation function removed as SQL imports are now handled by Docker initialization

def save_social_results(results: List, symbol: str, conn=None):
    """
    Save the social indicators results to the database.
    
    Args:
        results: List of social indicator results (IndicatorResult objects)
        symbol: Cryptocurrency symbol
        conn: Optional database connection (if not provided, will create one)
    
    Returns:
        Tuple of (SQL query, parameters) if conn is None, otherwise executes the query
    """
    if not results:
        logger.warning(f"No social results to save for {symbol}")
        return
    
    table = os.getenv('POSTGRES_SOCIAL_TABLE', 'analyse_social')
    
    try:
        # Calculate overall social score
        total_score = sum(r.score for r in results)
        
        # Prepare indicator-specific data
        indicator_data = {}
        
        # Only save scores that exist in the table schema
        valid_scores = [
            'social_volume',
            'sentiment_analysis',
            'developer_activity',
            'community_growth'
        ]
        
        for result in results:
            indicator_name = result.indicator_name
            if indicator_name in valid_scores:
                indicator_data[f"{indicator_name}_score"] = result.score
        
        # Calculate total social score
        total_social_score = sum(r.score for r in results)
        
        # Prepare the insert data
        insert_data = {
            "symbol": symbol
        }
        
        # Add indicator-specific data (scores)
        insert_data.update(indicator_data)
        
        # Build the SQL query dynamically based on available fields
        fields = list(insert_data.keys())
        placeholders = [f"%({field})s" for field in fields]
        
        query = f"""
        INSERT INTO {table} ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT (symbol) 
        DO UPDATE SET 
            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field != 'symbol'])}
        """
        
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, insert_data)
            return None
        else:
            return query, insert_data
    except Exception as e:
        logger.error(f"Error saving social results for {symbol}: {e}")
        raise

def save_social_results_batch(results_dict: Dict[str, List], conn=None):
    """
    Save social results for multiple symbols in a single transaction.
    
    Args:
        results_dict: Dictionary mapping symbol to list of social indicator results
        conn: Optional database connection (if not provided, will create one)
    """
    if not results_dict:
        logger.warning("No social results to save")
        return
    
    # Collect all queries and parameters
    queries = []
    for symbol, results in results_dict.items():
        query_and_params = save_social_results(results, symbol, conn)
        if query_and_params:
            queries.append(query_and_params)
    
    if not queries:
        return
    
    if not conn:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                for query, params in queries:
                    cur.execute(query, params)
            conn.commit()
    else:
        with conn.cursor() as cur:
            for query, params in queries:
                cur.execute(query, params)

    logger.info(f"Successfully saved social results for {len(results_dict)} symbols")

def get_latest_social(symbols: List[str] = None, limit: int = 10):
    """
    Retrieve the latest social indicators from the database.
    
    Args:
        symbol: Optional cryptocurrency symbol to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of social indicator results
    """
    table = os.getenv('POSTGRES_SOCIAL_TABLE', 'analyse_social')
    
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                if symbols:
                    query = f"""
                    SELECT * FROM {table}
                    WHERE symbol IN %s
                    ORDER BY analysis_date DESC
                    LIMIT %s
                    """
                    cur.execute(query, (tuple(symbols), limit))
                else:
                    query = f"""
                    SELECT * FROM {table}
                    ORDER BY analysis_date DESC
                    LIMIT %s
                    """
                    cur.execute(query, (limit,))
                
                columns = [desc[0] for desc in cur.description]
                results = []
                
                for row in cur.fetchall():
                    result = dict(zip(columns, row))
                    results.append(result)
                
                return results
    except Exception as e:
        logger.error(f"Error retrieving social indicators: {e}")
        return []
