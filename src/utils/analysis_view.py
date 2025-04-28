from typing import Optional, Dict, Any
import logging
from sqlalchemy import text
from .db import DBConnection

logger = logging.getLogger(__name__)

# The analysis_summary view is created by Docker initialization scripts in .docker/db/import/create_analysis_view.sql

def get_latest_analysis(symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Get the latest analysis summary for a specific symbol.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)
        days: Number of days to look back for analysis (not currently used in the query)
        
    Returns:
        Dictionary containing analysis summary or None if no data found
    """
    # Normalize symbol to uppercase for consistency
    symbol = symbol.upper()
    
    try:
        with DBConnection() as conn:
            # SQL query with proper indentation and no unnecessary parameters
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
            
            # Execute query with only the parameters actually used
            result = conn.execute(query, {"symbol": symbol}).fetchone()
            
            if not result:
                logger.info(f"No analysis found for symbol {symbol}")
                return None
                
            # Create the response dictionary
            analysis_data = {
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
            
            return analysis_data
            
    except Exception as e:
        logger.error(f"Failed to get latest analysis for {symbol}: {str(e)}")
        # Log the full exception for debugging
        logger.exception("Detailed error:")
        return None  # Return None instead of raising to make the API more resilient
