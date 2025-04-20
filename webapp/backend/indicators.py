from fastapi import APIRouter, Query
import os
import psycopg2

router = APIRouter()

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "pad")
DB_USER = os.getenv("POSTGRES_USER", "SpecialOsio")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "oeh_ahb6Ahzah7exeish")

@router.get("/api/indicators")
def get_indicators(token: str = Query(..., alias="token")):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT trading_volume_score, liquidity_score, whale_transactions_score, token_distribution_score, pre_sale_vesting_score, smart_contract_audit_score,
                       social_volume_score, sentiment_analysis_score, developer_activity_score, community_growth_score,
                       total_social_score, total_technical_score, total_score, score_percentage
                FROM analysis_summary
                WHERE symbol = %s
            """, (token,))
            row = cur.fetchone()
            if not row:
                return {"technical": [], "social": []}
            technical = [
                {"name": "Trading Volume", "value": float(row[0]) if row[0] is not None else 0, "max": 15},
                {"name": "Liquidity", "value": float(row[1]) if row[1] is not None else 0, "max": 15},
                {"name": "Whale Transactions", "value": float(row[2]) if row[2] is not None else 0, "max": 10},
                {"name": "Token Distribution", "value": float(row[3]) if row[3] is not None else 0, "max": 10},
                {"name": "Pre-Sale Vesting", "value": float(row[4]) if row[4] is not None else 0, "max": 10},
                {"name": "Smart Contract Audit", "value": float(row[5]) if row[5] is not None else 0, "max": 10},
            ]
            social = [
                {"name": "Social Volume", "value": float(row[6]) if row[6] is not None else 0, "max": 10},
                {"name": "Sentiment Analysis", "value": float(row[7]) if row[7] is not None else 0, "max": 10},
                {"name": "Developer Activity", "value": float(row[8]) if row[8] is not None else 0, "max": 10},
            ]
            score_percentage = float(row[13]) if row[13] is not None else None
            total_score = float(row[12]) if row[12] is not None else None
            return {"technical": technical, "social": social, "score_percentage": score_percentage, "total_score": total_score}
    finally:
        conn.close()
