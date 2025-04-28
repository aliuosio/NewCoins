"""
cron_db.py
Utility functions for managing cronjob records in the PostgreSQL database.
The cronjobs table is created by Docker initialization scripts in .docker/db/import/create_cronjobs_table.sql
"""

import psycopg2
from datetime import datetime
from .db import DBConnection


from pathlib import Path

def save_cronjob(schedule: str, command: str):
    # The cronjobs table is created by Docker initialization scripts
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cronjobs (schedule, command, created_at) VALUES (%s, %s, %s)",
                (schedule, command, datetime.now())
            )
        conn.commit()

def get_cronjobs():
    # The cronjobs table is created by Docker initialization scripts
    with DBConnection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, schedule, command, created_at FROM cronjobs ORDER BY created_at DESC")
            return cur.fetchall()
