from typing import Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from .db import DBConnection

logger = logging.getLogger(__name__)

def create_analysis_view():
    """
    Create the analysis_summary view if it doesn't exist.
    """
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                # Check if view exists
                exists_query = """
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.views 
                        WHERE table_schema = 'public' 
                        AND table_name = 'analysis_summary'
                    )
                """
                
                cur.execute(exists_query)
                exists = cur.fetchone()[0]
                
                if not exists:
                    # Read SQL file
                    with open("sql/create_analysis_view.sql", "r") as f:
                        sql = f.read()
                    
                    # Execute SQL
                    cur.execute(sql)
                    conn.commit()
                    logger.info("Analysis summary view created successfully")
                else:
                    logger.info("Analysis summary view already exists")
                
    except Exception as e:
        logger.error(f"Error creating analysis view: {str(e)}")
        raise

def refresh_analysis_view():
    """
    Refresh the analysis_summary materialized view to update with latest data.
    """
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("REFRESH MATERIALIZED VIEW analysis_summary")
            logger.info("Analysis summary view refreshed successfully")
    except Exception as e:
        logger.error(f"Failed to refresh analysis summary view: {str(e)}")
        raise

def get_latest_analysis(symbol: str, days: int = 30) -> Optional[dict]:
    """
    Get the latest analysis summary for a specific symbol.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)
        days: Number of days to look back for analysis
        
    Returns:
        Dictionary containing analysis summary or None if no data found
    """
    try:
        with DBConnection() as conn:
            query = text("""
                SELECT 
                    symbol,
                    analysis_date,
                    total_technical_score,
                    total_score,
                    score_percentage,
                    recommendation,
                    technical_data,
                    social_data
                FROM analysis_summary
                WHERE symbol = :symbol
                AND analysis_date >= NOW() - INTERVAL ':days days'
                ORDER BY analysis_date DESC
                LIMIT 1
            """)
            
            result = conn.execute(query, {"symbol": symbol, "days": days}).fetchone()
            
            if result:
                return {
                    "symbol": result.symbol,
                    "analysis_date": result.analysis_date,
                    "total_technical_score": result.total_technical_score,
                    "total_score": result.total_score,
                    "score_percentage": result.score_percentage,
                    "recommendation": result.recommendation,
                    "technical_data": result.technical_data,
                    "social_data": result.social_data
                }
            return None
    except Exception as e:
        logger.error(f"Failed to get latest analysis for {symbol}: {str(e)}")
        raise
