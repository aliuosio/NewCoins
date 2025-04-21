from fastapi import APIRouter
from typing import List, Dict
import os
import psycopg2

from src.utils.db_config import get_db_config

router = APIRouter()

from src.utils.db_config import get_db_config, get_coins_table

COINS_SELECT_QUERY = "SELECT symbol, name FROM {table} ORDER BY symbol;"

def map_coin_row(row):
    symbol, name = row
    return {"symbol": symbol, "name": name}

@router.get("/api/coins", response_model=List[Dict[str, str]])
def get_coins():
    table = get_coins_table()
    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cur:
            cur.execute(COINS_SELECT_QUERY.format(table=table))
            rows = cur.fetchall()
            return [map_coin_row(row) for row in rows]
    finally:
        conn.close()
