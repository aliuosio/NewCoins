from typing import Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from .db import DBConnection

logger = logging.getLogger(__name__)

# The analysis_summary view is created by Docker initialization scripts in .docker/db/import/create_analysis_view.sql

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
