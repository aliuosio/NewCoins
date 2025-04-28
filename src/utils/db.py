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
                # Add retry logic for DNS resolution issues
                max_retries = 5
                retry_delay = 2  # seconds
                last_exception = None
                
                for attempt in range(1, max_retries + 1):
                    try:
                        logger.info(f"Attempting to create connection pool (attempt {attempt}/{max_retries})")
                        _connection_pool = pool.ThreadedConnectionPool(
                            POOL_MINCONN, POOL_MAXCONN, **get_db_config()
                        )
                        logger.info("Successfully created database connection pool")
                        break
                    except (psycopg2.OperationalError, psycopg2.Error) as e:
                        last_exception = e
                        if "could not translate host name" in str(e) or "could not connect to server" in str(e):
                            logger.warning(f"Database connection attempt {attempt} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            # Increase delay for next attempt (exponential backoff)
                            retry_delay = min(retry_delay * 2, 30)  # Cap at 30 seconds
                        else:
                            # If it's not a DNS or connection issue, re-raise immediately
                            logger.error(f"Database error: {str(e)}")
                            raise
                
                # If we've exhausted all retries and still don't have a connection
                if _connection_pool is None:
                    logger.error(f"Failed to connect to database after {max_retries} attempts")
                    raise last_exception
    
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
