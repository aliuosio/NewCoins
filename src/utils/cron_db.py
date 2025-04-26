"""
cron_db.py
Utility functions for managing cronjob records in the PostgreSQL database.
Ensures the cronjobs table exists before writing new jobs.
"""

import psycopg2
from datetime import datetime
from .db import DBConnection


from pathlib import Path

def ensure_cronjobs_table_exists():
    # Create the cronjobs table directly with SQL instead of loading from a file
    cronjobs_table_sql = """
    CREATE TABLE IF NOT EXISTS cronjobs (
        id SERIAL PRIMARY KEY,
        schedule TEXT NOT NULL,
        command TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(cronjobs_table_sql)
        conn.commit()

def save_cronjob(schedule: str, command: str):
    ensure_cronjobs_table_exists()
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cronjobs (schedule, command, created_at) VALUES (%s, %s, %s)",
                (schedule, command, datetime.now())
            )
        conn.commit()

def get_cronjobs():
    ensure_cronjobs_table_exists()
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, schedule, command, created_at FROM cronjobs ORDER BY created_at DESC")
            return cur.fetchall()
