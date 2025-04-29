#!/usr/bin/env python3
"""
Initialize the database and verify connection for the NewCoins application.
"""
import os
import logging

from utils.database.connection import DBConnection

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database connection and verify it's working."""
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"Connected to PostgreSQL version: {version}")
                return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

if __name__ == "__main__":
    init_database()
