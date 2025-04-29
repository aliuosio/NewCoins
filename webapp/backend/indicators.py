from fastapi import APIRouter, Query
import logging
from typing import Dict, Any, Optional
from database import execute_query_to_dict, get_cached_data, execute_query_with_error_handling

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/indicators")
def get_indicators(token: str = Query(..., alias="token")):
    """
    Get technical and social indicators for a specific token.
    
    Args:
        token: Cryptocurrency symbol
        
    Returns:
        Dictionary containing technical and social indicators
    """
    # Normalize token to uppercase for consistent cache keys
    token = token.upper()
    
    # Define the function to fetch indicators data
    def fetch_indicators_data(token_symbol):
        try:
            query = """
                SELECT trading_volume_score, liquidity_score, whale_transactions_score, token_distribution_score, pre_sale_vesting_score, smart_contract_audit_score,
                       google_trends_score, sentiment_analysis_score, developer_activity_score, community_growth_score,
                       total_social_score, total_technical_score, total_score, score_percentage
                FROM analysis_summary
                WHERE symbol = %s
            """
            result = execute_query_to_dict(query, (token_symbol,), fetch_all=False)
            
            if not result:
                logger.warning(f"No indicators found for token: {token_symbol}")
                return {"technical": [], "social": []}
            
            # Define the indicators with their names, values, and max scores
            technical = [
                {"name": "Trading Volume", "value": float(result["trading_volume_score"]) if result["trading_volume_score"] is not None else 0, "max": 15},
                {"name": "Liquidity", "value": float(result["liquidity_score"]) if result["liquidity_score"] is not None else 0, "max": 15},
                {"name": "Whale Transactions", "value": float(result["whale_transactions_score"]) if result["whale_transactions_score"] is not None else 0, "max": 10},
                {"name": "Token Distribution", "value": float(result["token_distribution_score"]) if result["token_distribution_score"] is not None else 0, "max": 10},
                {"name": "Pre-Sale Vesting", "value": float(result["pre_sale_vesting_score"]) if result["pre_sale_vesting_score"] is not None else 0, "max": 10},
                {"name": "Smart Contract Audit", "value": float(result["smart_contract_audit_score"]) if result["smart_contract_audit_score"] is not None else 0, "max": 10},
            ]
            social = [
                {"name": "Google Trends", "value": float(result["google_trends_score"]) if result["google_trends_score"] is not None else 0, "max": 5},
                {"name": "Sentiment Analysis", "value": float(result["sentiment_analysis_score"]) if result["sentiment_analysis_score"] is not None else 0, "max": 10},
                {"name": "Developer Activity", "value": float(result["developer_activity_score"]) if result["developer_activity_score"] is not None else 0, "max": 10},
                {"name": "Community Growth", "value": float(result["community_growth_score"]) if result["community_growth_score"] is not None else 0, "max": 5},
            ]
            
            score_percentage = float(result["score_percentage"]) if result["score_percentage"] is not None else None
            total_score = float(result["total_score"]) if result["total_score"] is not None else None
            
            return {
                "technical": technical, 
                "social": social, 
                "score_percentage": score_percentage, 
                "total_score": total_score
            }
        except Exception as e:
            logger.exception(f"Error fetching indicators for {token_symbol}: {str(e)}")
            return {"technical": [], "social": [], "error": str(e)}
    
    # Use the cached data helper to get or fetch the data
    return get_cached_data(f"indicators_{token}", fetch_indicators_data, token)
