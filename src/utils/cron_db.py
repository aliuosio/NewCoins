"""
cron_db.py
Utility functions for managing cronjob records in the PostgreSQL database.
Ensures the cronjobs table exists before writing new jobs.
"""

import psycopg2
from datetime import datetime
import os

CRONJOBS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cronjobs (
    id SERIAL PRIMARY KEY,
    schedule TEXT NOT NULL,
    command TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def ensure_cronjobs_table_exists():
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"]
    )
    try:
        with conn.cursor() as cur:
            cur.execute(CRONJOBS_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()

def save_cronjob(schedule: str, command: str):
    ensure_cronjobs_table_exists()
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"]
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cronjobs (schedule, command, created_at) VALUES (%s, %s, %s)",
                (schedule, command, datetime.now())
            )
        conn.commit()
    finally:
        conn.close()

def get_cronjobs():
    ensure_cronjobs_table_exists()
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"]
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, schedule, command, created_at FROM cronjobs ORDER BY created_at DESC")
            return cur.fetchall()
    finally:
        conn.close()
