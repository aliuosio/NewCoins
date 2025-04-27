from fastapi import APIRouter, HTTPException
from src.utils.db import DBConnection
from typing import Dict, List, Any

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
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")

@router.get("/api/coins")
def get_all_coins() -> List[Dict[str, Any]]:
    """
    Returns all data for all coins from the coins table.
    """
    with DBConnection() as conn:
        with conn.cursor() as cur:
            # First, get the column names
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'coins' ORDER BY ordinal_position;")
            columns = [col[0] for col in cur.fetchall()]
            
            # Then get all data
            cur.execute("SELECT * FROM coins ORDER BY symbol;")
            rows = cur.fetchall()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in rows]

@router.get("/api/coin/{symbol}")
def get_coin_data(symbol: str) -> Dict[str, Any]:
    """
    Returns all data for a single coin symbol from the coins table.
    """
    with DBConnection() as conn:
        with conn.cursor() as cur:
            # First, get the column names
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'coins' ORDER BY ordinal_position;")
            columns = [col[0] for col in cur.fetchall()]
            
            # Then get the data for the specific symbol
            cur.execute("SELECT * FROM coins WHERE symbol = %s;", (symbol,))
            row = cur.fetchone()
            
            if row:
                return dict(zip(columns, row))
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")
