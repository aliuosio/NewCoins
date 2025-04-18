#!/usr/bin/env python3
"""
Database utilities for saving cryptocurrency analysis results.
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

logger = logging.getLogger("analysis_db")

def create_technical_indicators_table():
    """
    Create the technical indicators table if it doesn't exist.
    """
    table = os.getenv('POSTGRES_ANALYSIS_TABLE', 'analyse_technical')
    # Load SQL from project-level sql folder
    sql_path = '/src/sql/create_analyse_technical.sql'
    
    try:
        with open(sql_path) as f:
            create_query = f.read().format(table=table)
        
        with DBConnection() as conn:
            with conn.cursor() as cur:
                # Create table schema
                cur.execute(create_query)
            conn.commit()
        logger.info(f"Successfully created/updated analysis table: {table}")
    except Exception as e:
        logger.error(f"Error creating analysis table: {e}")
        raise

def save_analysis_results(results: List, symbol: str, conn=None):
    """
    Save the analysis results to the database.
    
    Args:
        results: List of indicator results
        symbol: Cryptocurrency symbol
        conn: Optional database connection (if not provided, will create one)
    
    Returns:
        Tuple of (SQL query, parameters) if conn is None, otherwise executes the query
    """
    if not results:
        logger.warning(f"No analysis results to save for {symbol}")
        return
    
    table = os.getenv('POSTGRES_ANALYSIS_TABLE', 'analyse_technical')
    
    try:
        # Calculate overall scores - filter out None values (not applicable indicators)
        valid_results = [r for r in results if r.score is not None]
        total_score = sum(r.score for r in valid_results)
        
        # For max_score, we only count the indicators that are applicable
        max_score = sum(r.max_score for r in valid_results)
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Determine recommendation
        if percentage >= 80:
            recommendation = "STRONG BUY"
        elif percentage >= 70:
            recommendation = "BUY"
        elif percentage >= 60:
            recommendation = "HOLD"
        elif percentage >= 50:
            recommendation = "WATCH"
        else:
            recommendation = "AVOID"
        
        # Prepare indicator-specific data
        indicator_data = {}
        raw_data = {}
        
        for result in results:
            indicator_name = result.indicator_name
            
            # Handle not applicable indicators
            if result.score is None:
                # Store a special value or flag to indicate not applicable
                indicator_data[f"{indicator_name}_score"] = None
                indicator_data[f"{indicator_name}_applicable"] = False
            else:
                indicator_data[f"{indicator_name}_score"] = result.score
                indicator_data[f"{indicator_name}_applicable"] = True
            
            # Store raw details for future reference
            raw_data[indicator_name] = result.details
        
        # Extract additional data points if available
        additional_data = {}
        
        # Market cap and supply data
        for result in results:
            if result.indicator_name == "token_distribution" and hasattr(result, "details"):
                details = result.details
                if "circulating_supply" in details:
                    additional_data["circulating_supply"] = details["circulating_supply"]
                if "total_supply" in details:
                    additional_data["total_supply"] = details["total_supply"]
        
        # Trading volume data
        for result in results:
            if result.indicator_name == "trading_volume" and hasattr(result, "details"):
                details = result.details
                if "total_volume_24h" in details:
                    additional_data["trading_volume_24h"] = details["total_volume_24h"]
        
        # Vesting data
        for result in results:
            if result.indicator_name == "pre_sale_vesting" and hasattr(result, "details"):
                details = result.details
                if "upcoming_unlocks" in details:
                    additional_data["upcoming_unlocks"] = details["upcoming_unlocks"]
                if "days_to_next_unlock" in details:
                    additional_data["days_to_next_unlock"] = details["days_to_next_unlock"]
                if "unlock_percentage" in details:
                    # Remove % sign if present and convert to float
                    unlock_pct = details["unlock_percentage"]
                    if isinstance(unlock_pct, str) and "%" in unlock_pct:
                        unlock_pct = float(unlock_pct.replace("%", ""))
                    additional_data["unlock_percentage"] = unlock_pct
        
        # Audit data
        for result in results:
            if result.indicator_name == "smart_contract_audit" and hasattr(result, "details"):
                details = result.details
                if "audits_found" in details:
                    additional_data["audits_found"] = details["audits_found"]
                if "vulnerabilities" in details:
                    vuln_text = details["vulnerabilities"]
                    if isinstance(vuln_text, str):
                        # Parse "X critical, Y major" format
                        parts = vuln_text.split(",")
                        for part in parts:
                            if "critical" in part:
                                additional_data["vulnerabilities_critical"] = int(part.split()[0])
                            if "major" in part:
                                additional_data["vulnerabilities_major"] = int(part.split()[0])
        
        # Prepare the insert data
        insert_data = {
            "symbol": symbol,
            "analysis_date": datetime.now(),
            "recommendation": recommendation
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
        logger.error(f"Error saving analysis results for {symbol}: {e}")
        raise

def save_analysis_results_batch(results_dict: Dict[str, List], conn=None):
    """
    Save analysis results for multiple symbols in a single transaction.
    
    Args:
        results_dict: Dictionary mapping symbol to list of indicator results
        conn: Optional database connection (if not provided, will create one)
    """
    if not results_dict:
        logger.warning("No analysis results to save")
        return
    
    # Collect all queries and parameters
    queries = []
    for symbol, results in results_dict.items():
        query_and_params = save_analysis_results(results, symbol, conn)
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

    logger.info(f"Successfully saved analysis results for {len(results_dict)} symbols")

def get_latest_analysis(symbols: List[str] = None, limit: int = 10):
    """
    Retrieve the latest analysis results from the database.
    
    Args:
        symbol: Optional cryptocurrency symbol to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of analysis results
    """
    table = os.getenv('POSTGRES_ANALYSIS_TABLE', 'analyse_technical')
    
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
        logger.error(f"Error retrieving analysis results: {e}")
        return []
