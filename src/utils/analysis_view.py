from typing import Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from .db import DBConnection

logger = logging.getLogger(__name__)

def create_analysis_view():
    """
    Create the analysis_summary view if it doesn't exist.
    The view is now created by Docker initialization scripts, but this function
    is kept for backward compatibility and to ensure the view exists.
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
                    # Create the view directly with SQL
                    sql = """
                    CREATE OR REPLACE VIEW analysis_summary AS
                    SELECT 
                        t.symbol,
                        t.trading_volume_score,
                        t.liquidity_score,
                        t.whale_transactions_score,
                        t.token_distribution_score,
                        t.pre_sale_vesting_score,
                        t.smart_contract_audit_score,
                        s.google_trends_score,
                        s.sentiment_analysis_score,
                        s.developer_activity_score,
                        s.community_growth_score,
                        COALESCE(t.trading_volume_score, 0) + 
                        COALESCE(t.liquidity_score, 0) + 
                        COALESCE(t.whale_transactions_score, 0) + 
                        COALESCE(t.token_distribution_score, 0) + 
                        COALESCE(t.pre_sale_vesting_score, 0) + 
                        COALESCE(t.smart_contract_audit_score, 0) AS total_technical_score,
                        COALESCE(s.google_trends_score, 0) + 
                        COALESCE(s.sentiment_analysis_score, 0) + 
                        COALESCE(s.developer_activity_score, 0) + 
                        COALESCE(s.community_growth_score, 0) AS total_social_score,
                        (COALESCE(t.trading_volume_score, 0) + 
                        COALESCE(t.liquidity_score, 0) + 
                        COALESCE(t.whale_transactions_score, 0) + 
                        COALESCE(t.token_distribution_score, 0) + 
                        COALESCE(t.pre_sale_vesting_score, 0) + 
                        COALESCE(t.smart_contract_audit_score, 0) +
                        COALESCE(s.google_trends_score, 0) + 
                        COALESCE(s.sentiment_analysis_score, 0) + 
                        COALESCE(s.developer_activity_score, 0) + 
                        COALESCE(s.community_growth_score, 0)) AS total_score,
                        CASE 
                            WHEN (COALESCE(t.trading_volume_score, 0) + 
                                COALESCE(t.liquidity_score, 0) + 
                                COALESCE(t.whale_transactions_score, 0) + 
                                COALESCE(t.token_distribution_score, 0) + 
                                COALESCE(t.pre_sale_vesting_score, 0) + 
                                COALESCE(t.smart_contract_audit_score, 0) +
                                COALESCE(s.google_trends_score, 0) + 
                                COALESCE(s.sentiment_analysis_score, 0) + 
                                COALESCE(s.developer_activity_score, 0) + 
                                COALESCE(s.community_growth_score, 0)) >= 70 THEN 'Strong Buy'
                            WHEN (COALESCE(t.trading_volume_score, 0) + 
                                COALESCE(t.liquidity_score, 0) + 
                                COALESCE(t.whale_transactions_score, 0) + 
                                COALESCE(t.token_distribution_score, 0) + 
                                COALESCE(t.pre_sale_vesting_score, 0) + 
                                COALESCE(t.smart_contract_audit_score, 0) +
                                COALESCE(s.google_trends_score, 0) + 
                                COALESCE(s.sentiment_analysis_score, 0) + 
                                COALESCE(s.developer_activity_score, 0) + 
                                COALESCE(s.community_growth_score, 0)) >= 50 THEN 'Buy'
                            WHEN (COALESCE(t.trading_volume_score, 0) + 
                                COALESCE(t.liquidity_score, 0) + 
                                COALESCE(t.whale_transactions_score, 0) + 
                                COALESCE(t.token_distribution_score, 0) + 
                                COALESCE(t.pre_sale_vesting_score, 0) + 
                                COALESCE(t.smart_contract_audit_score, 0) +
                                COALESCE(s.google_trends_score, 0) + 
                                COALESCE(s.sentiment_analysis_score, 0) + 
                                COALESCE(s.developer_activity_score, 0) + 
                                COALESCE(s.community_growth_score, 0)) >= 30 THEN 'Hold'
                            ELSE 'Sell'
                        END AS recommendation,
                        CASE 
                            WHEN (COALESCE(t.trading_volume_score, 0) + 
                                COALESCE(t.liquidity_score, 0) + 
                                COALESCE(t.whale_transactions_score, 0) + 
                                COALESCE(t.token_distribution_score, 0) + 
                                COALESCE(t.pre_sale_vesting_score, 0) + 
                                COALESCE(t.smart_contract_audit_score, 0) +
                                COALESCE(s.google_trends_score, 0) + 
                                COALESCE(s.sentiment_analysis_score, 0) + 
                                COALESCE(s.developer_activity_score, 0) + 
                                COALESCE(s.community_growth_score, 0)) = 0 THEN 0
                            ELSE 
                                ROUND(((COALESCE(t.trading_volume_score, 0) + 
                                COALESCE(t.liquidity_score, 0) + 
                                COALESCE(t.whale_transactions_score, 0) + 
                                COALESCE(t.token_distribution_score, 0) + 
                                COALESCE(t.pre_sale_vesting_score, 0) + 
                                COALESCE(t.smart_contract_audit_score, 0) +
                                COALESCE(s.google_trends_score, 0) + 
                                COALESCE(s.sentiment_analysis_score, 0) + 
                                COALESCE(s.developer_activity_score, 0) + 
                                COALESCE(s.community_growth_score, 0)) / 100.0) * 100, 2)
                        END AS score_percentage,
                        GREATEST(t.updated_at, s.updated_at) AS updated_at
                    FROM 
                        analyse_technical t
                    LEFT JOIN 
                        analyse_social s ON t.symbol = s.symbol;
                    """
                    
                    # Execute SQL
                    cur.execute(sql)
                    conn.commit()
                    logger.info("Analysis summary view created successfully")
                else:
                    logger.info("Analysis summary view already exists")
                
    except Exception as e:
        logger.error(f"Error creating analysis view: {str(e)}")
        raise

# Regular views don't need to be refreshed as they're computed on-the-fly

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

                    total_technical_score,
                    total_social_score,
                    total_score,
                    score_percentage,
                    recommendation,
                    trading_volume_score,
                    liquidity_score,
                    whale_transactions_score,
                    token_distribution_score,
                    pre_sale_vesting_score,
                    smart_contract_audit_score,
                    google_trends_score,
                    sentiment_analysis_score,
                    developer_activity_score,
                    community_growth_score
                FROM analysis_summary
                WHERE symbol = :symbol
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            
            result = conn.execute(query, {"symbol": symbol, "days": days}).fetchone()
            
            if result:
                return {
                    "symbol": result.symbol,

                    "total_technical_score": result.total_technical_score,
                    "total_social_score": result.total_social_score,
                    "total_score": result.total_score,
                    "score_percentage": result.score_percentage,
                    "recommendation": result.recommendation,
                    "technical_indicators": {
                        "trading_volume": result.trading_volume_score,
                        "liquidity": result.liquidity_score,
                        "whale_transactions": result.whale_transactions_score,
                        "token_distribution": result.token_distribution_score,
                        "pre_sale_vesting": result.pre_sale_vesting_score,
                        "smart_contract_audit": result.smart_contract_audit_score
                    },
                    "social_indicators": {
                        "google_trends": result.google_trends_score,
                        "sentiment_analysis": result.sentiment_analysis_score,
                        "developer_activity": result.developer_activity_score,
                        "community_growth": result.community_growth_score
                    }
                }
            return None
    except Exception as e:
        logger.error(f"Failed to get latest analysis for {symbol}: {str(e)}")
        raise
