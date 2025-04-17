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

def create_social_table():
    """
    Create the social indicators table if it doesn't exist.
    """
    table = os.getenv('POSTGRES_SOCIAL_TABLE', 'crypto_social')
    coins_table = os.getenv('POSTGRES_TABLE', 'coins')
    # Load SQL from project-level sql folder
    sql_path = Path(__file__).parent.parent / "sql" / "create_social_table.sql"
    
    try:
        with open(sql_path) as f:
            create_query = f.read().format(table=table, coins_table=coins_table)
        
        with DBConnection() as conn:
            with conn.cursor() as cur:
                # Create table schema
                cur.execute(create_query)
            conn.commit()
        logger.info(f"Successfully created/updated social indicators table: {table}")
    except Exception as e:
        logger.error(f"Error creating social indicators table: {e}")
        raise

def save_social_results(results: List, symbol: str):
    """
    Save the social indicators results to the database.
    
    Args:
        results: List of social indicator results (IndicatorResult objects)
        symbol: Cryptocurrency symbol
    """
    if not results:
        logger.warning(f"No social results to save for {symbol}")
        return
    
    table = os.getenv('POSTGRES_SOCIAL_TABLE', 'crypto_social')
    
    try:
        # Calculate overall social score
        total_score = sum(r.score for r in results)
        
        # Prepare indicator-specific data
        indicator_data = {}
        raw_data = {}
        
        for result in results:
            indicator_name = result.indicator_name
            indicator_data[f"{indicator_name}_score"] = result.score
            
            # Store raw details for future reference
            raw_data[indicator_name] = {
                'score': result.score,
                'max_score': result.max_score,
                'details': result.details,
                'execution_time_ms': result.execution_time_ms,
                'success': result.success,
                'error': result.error
            }
        
        # Calculate total social score
        total_social_score = sum(r.score for r in results)
        
        # Prepare the insert data
        insert_data = {
            "symbol": symbol,
            "analysis_date": datetime.now(),
            "raw_data": Json(raw_data)
        }
        
        # Add indicator-specific data
        insert_data.update(indicator_data)
        
        # Add total social score
        insert_data["total_social_score"] = total_social_score
        
        # Build the SQL query dynamically based on available fields
        fields = list(insert_data.keys())
        placeholders = [f"%({field})s" for field in fields]
        
        with DBConnection() as conn:
            with conn.cursor() as cur:
                query = f"""
                INSERT INTO {table} ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (symbol, analysis_date) 
                DO UPDATE SET 
                    {', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field not in ['symbol', 'analysis_date']])}
                """
                cur.execute(query, insert_data)
            conn.commit()
        
        logger.info(f"Successfully saved social indicators for {symbol}")
    except Exception as e:
        logger.error(f"Error saving social indicators for {symbol}: {e}")
        raise

def get_latest_social(symbol: str = None, limit: int = 10):
    """
    Retrieve the latest social indicators from the database.
    
    Args:
        symbol: Optional cryptocurrency symbol to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of social indicator results
    """
    table = os.getenv('POSTGRES_SOCIAL_TABLE', 'crypto_social')
    
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                if symbol:
                    query = f"""
                    SELECT * FROM {table}
                    WHERE symbol = %s
                    ORDER BY analysis_date DESC
                    LIMIT %s
                    """
                    cur.execute(query, (symbol, limit))
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
