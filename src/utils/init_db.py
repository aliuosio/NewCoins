#!/usr/bin/env python3
"""
Initialize the database and create necessary tables for the PumpAndDump application.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from db import create_tables, DBConnection
from analysis_db import create_analysis_table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("init_db")

def init_database():
    """Initialize the database and create all necessary tables."""
    # Load environment variables
    load_dotenv()
    
    # Check database connection
    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version}")
        
        # Create coins table
        logger.info("Creating coins table...")
        create_tables()
        
        # Create analysis table
        logger.info("Creating analysis table...")
        create_analysis_table()
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()
