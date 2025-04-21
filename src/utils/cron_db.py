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
    sql_path = Path(__file__).parent.parent / "sql" / "create_cronjobs_table.sql"
    with open(sql_path) as f:
        cronjobs_table_sql = f.read()
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
