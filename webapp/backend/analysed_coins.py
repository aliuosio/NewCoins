from fastapi import APIRouter
from src.utils.db import DBConnection

router = APIRouter()

@router.get("/api/analysed_coins")
def get_analysed_coins():
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT symbol FROM analysis_summary ORDER BY symbol;")
            rows = cur.fetchall()
            return [row[0] for row in rows]
