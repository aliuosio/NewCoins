#!/usr/bin/env python3
"""
Database connection and persistence utilities for PumpAndDump app.
"""
import os
import psycopg2
from psycopg2.extras import execute_values
import pytz
from datetime import datetime
from pathlib import Path

class DBConnection:
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        self.db = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.table = os.getenv("POSTGRES_TABLE", "coins")
        self._conn = None

    def __enter__(self):
        self._conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db,
            user=self.user,
            password=self.password
        )
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.commit()
            self._conn.close()

def create_tables():
    """
    Create necessary tables (coins) if they do not exist.
    """
    table = os.getenv('POSTGRES_TABLE')
    # load SQL from project-level sql folder
    sql_path = Path(__file__).parent.parent / "sql" / "create_coins_table.sql"
    with open(sql_path) as f:
        create_query = f.read().format(table=table)
    drop_query = f"DROP TABLE IF EXISTS {table} CASCADE;"
    with DBConnection() as conn:
        with conn.cursor() as cur:
            # recreate table schema
            cur.execute(drop_query)
            cur.execute(create_query)
        conn.commit()

def insert_new_coins(coins):
    """
    Persist a list of NewCoin instances into PostgreSQL using full schema.
    """
    if not coins:
        return
    table = os.getenv('POSTGRES_TABLE')
    with DBConnection() as conn:
        with conn.cursor() as cur:
            values = [
                (
                    c.name,
                    c.symbol,
                    datetime.fromtimestamp(int(c.start_time) / 1000, tz=pytz.utc)
                )
                for c in coins
            ]
            insert_query = f"""
            INSERT INTO {table} (name, symbol, time_start)
            VALUES %s
            ON CONFLICT (symbol) DO UPDATE
                SET name = EXCLUDED.name,
                    time_start = EXCLUDED.time_start;
            """
            execute_values(cur, insert_query, values)
