from fastapi import APIRouter
import os
import psycopg2

router = APIRouter()

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "pad")
DB_USER = os.getenv("POSTGRES_USER", "SpecialOsio")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "oeh_ahb6Ahzah7exeish")

@router.get("/api/analysed_coins")
def get_analysed_coins():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT symbol FROM analysis_summary ORDER BY symbol;")
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()
