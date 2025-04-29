#!/usr/bin/env python3
"""
Database connection management for the NewCoins application.
Provides connection pooling and context manager for database connections.
"""
import os
import psycopg2
from psycopg2 import pool
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Import database configuration
from utils.db_config import get_db_config

# Connection pool settings
POOL_MINCONN = int(os.getenv("PG_POOL_MINCONN", 1))
POOL_MAXCONN = int(os.getenv("PG_POOL_MAXCONN", 10))

# Global connection pool instance (thread-safe)
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """
    Get or create a database connection pool.
    Implements retry logic with exponential backoff for connection failures.
    
    Returns:
        ThreadedConnectionPool: A connection pool instance
    """
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                # Add retry logic with exponential backoff
                max_retries = 5
                retry_count = 0
                base_delay = 2  # Start with 2 seconds delay
                max_delay = 30  # Cap delay at 30 seconds
                
                while retry_count < max_retries:
                    try:
                        _connection_pool = pool.ThreadedConnectionPool(
                            POOL_MINCONN, POOL_MAXCONN, **get_db_config()
                        )
                        break
                    except psycopg2.OperationalError as e:
                        # Check if this is a DNS resolution error
                        if "could not translate host name" in str(e).lower() or "could not connect to server" in str(e).lower():
                            retry_count += 1
                            if retry_count >= max_retries:
                                logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                                raise
                            
                            # Calculate delay with exponential backoff, capped at max_delay
                            delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)
                            logger.warning(f"Database connection failed, retrying in {delay} seconds: {e}")
                            time.sleep(delay)
                        else:
                            # If it's not a DNS resolution error, re-raise immediately
                            logger.error(f"Database connection error: {e}")
                            raise
    
    return _connection_pool

class DBConnection:
    """
    Context manager for database connections.
    Automatically gets a connection from the pool and returns it when done.
    
    Usage:
        with DBConnection() as conn:
            # Use conn for database operations
    """
    def __init__(self):
        self._conn = None

    def __enter__(self):
        """Get a connection from the pool when entering the context"""
        self._conn = get_connection_pool().getconn()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Return the connection to the pool when exiting the context"""
        if self._conn:
            if exc_type is None:
                # Only commit if no exception occurred
                self._conn.commit()
            else:
                # Rollback on exception
                self._conn.rollback()
            get_connection_pool().putconn(self._conn)
            self._conn = None
            
    def putconn(self, conn):
        """
        Return a connection to the pool.
        This is used when a connection is obtained outside the context manager.
        
        Args:
            conn: The connection to return to the pool
        """
        if conn:
            get_connection_pool().putconn(conn)
