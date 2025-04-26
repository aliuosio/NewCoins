from fastapi import APIRouter
from src.utils.db import DBConnection

router = APIRouter()

@router.get("/api/coin_start_times")
def get_coin_start_times():
    """
    Returns a list of coins with their symbol and start_time from the coins table.
    """
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT symbol, time_start FROM coins ORDER BY symbol;")
            rows = cur.fetchall()
            return [
                {"symbol": row[0], "time_start": row[1]} for row in rows
            ]

@router.get("/api/coin_start_time/{symbol}")
def get_coin_start_time(symbol: str):
    """
    Returns the start_time for a single coin symbol from the coins table.
    """
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT symbol, time_start FROM coins WHERE symbol = %s;", (symbol,))
            row = cur.fetchone()
            if row:
                return {"symbol": row[0], "time_start": row[1]}
            return {"detail": f"Symbol '{symbol}' not found."}, 404
