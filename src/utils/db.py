#!/usr/bin/env python3
"""
Database connection and persistence utilities for PumpAndDump app.
"""
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
import pytz
from datetime import datetime
from pathlib import Path
import threading

from utils.db_config import get_db_config

# Connection pool settings
POOL_MINCONN = int(os.getenv("PG_POOL_MINCONN", 1))
POOL_MAXCONN = int(os.getenv("PG_POOL_MAXCONN", 10))

# Global connection pool instance (thread-safe)
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = pool.ThreadedConnectionPool(
                    POOL_MINCONN, POOL_MAXCONN, **get_db_config()
                )
    return _connection_pool

class DBConnection:
    def __init__(self):
        self._conn = None

    def __enter__(self):
        self._conn = get_connection_pool().getconn()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.commit()
            get_connection_pool().putconn(self._conn)
            self._conn = None

def create_tables():
    """
    Create all necessary tables if they do not exist.
    """
    # Create coins table
    table = os.getenv('POSTGRES_TABLE')
    sql_path = Path(__file__).parent.parent / "sql" / "create_coins_table.sql"
    with open(sql_path) as f:
        create_query = f.read().format(table=table)
    drop_query = f"DROP TABLE IF EXISTS {table} CASCADE;"
    
    # Create technical analysis table
    technical_table = os.getenv('POSTGRES_ANALYSIS_TABLE', 'analyse_technical')
    technical_sql_path = Path(__file__).parent.parent / "sql" / "create_analyse_technical.sql"
    with open(technical_sql_path) as f:
        technical_create_query = f.read().format(table=technical_table)
    technical_drop_query = f"DROP TABLE IF EXISTS {technical_table} CASCADE;"
    
    # Create social analysis table
    social_table = os.getenv('POSTGRES_SOCIAL_TABLE', 'analyse_social')
    social_sql_path = Path(__file__).parent.parent / "sql" / "create_analyse_social.sql"
    with open(social_sql_path) as f:
        social_create_query = f.read().format(table=social_table)
    social_drop_query = f"DROP TABLE IF EXISTS {social_table} CASCADE;"
    
    with DBConnection() as conn:
        with conn.cursor() as cur:
            # Create technical analysis table
            cur.execute(technical_drop_query)
            cur.execute(technical_create_query)
            
            # Create social analysis table
            cur.execute(social_drop_query)
            cur.execute(social_create_query)
            
            # Create or update the analysis_summary view (after indicator tables, before coins table)
            analysis_view_sql_path = Path(__file__).parent.parent / "sql" / "create_analysis_view.sql"
            with open(analysis_view_sql_path) as f:
                analysis_view_query = f.read()
            cur.execute(analysis_view_query)
            
            # Create coins table
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
