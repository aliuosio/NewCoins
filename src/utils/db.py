#!/usr/bin/env python3
"""
Database connection and persistence utilities for PumpAndDump app.
"""
import os
# psycopg2-binary installs as psycopg2 module
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
import pytz
from datetime import datetime
from pathlib import Path
import threading
import time
import logging

logger = logging.getLogger(__name__)

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
                logger.info("Creating database connection pool")
                _connection_pool = pool.ThreadedConnectionPool(
                    POOL_MINCONN, POOL_MAXCONN, **get_db_config()
                )
                logger.info("Successfully created database connection pool")
    
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
    Tables are now created by Docker initialization scripts.
    This function is kept as a stub for backward compatibility.
    """
    # All table creation is now handled by Docker initialization
    pass

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
