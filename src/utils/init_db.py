#!/usr/bin/env python3
"""
Initialize the database and create necessary tables for the PumpAndDump application.
"""
import os

from db import DBConnection


def init_database():
    """Initialize the database and create all necessary tables."""

    try:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
    except Exception as e:
        raise

if __name__ == "__main__":
    init_database()
