from fastapi import APIRouter
from typing import List, Dict
import os
import psycopg2

router = APIRouter()

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "pad")
DB_USER = os.getenv("POSTGRES_USER", "SpecialOsio")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "oeh_ahb6Ahzah7exeish")
DB_TABLE = os.getenv("POSTGRES_TABLE", "coins")

@router.get("/api/coins", response_model=List[Dict[str, str]])
def get_coins():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT symbol, name FROM {DB_TABLE} ORDER BY symbol;")
            rows = cur.fetchall()
            return [{"symbol": symbol, "name": name} for symbol, name in rows]
    finally:
        conn.close()
