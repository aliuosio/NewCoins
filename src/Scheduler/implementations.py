import subprocess
import psycopg2
import os
from datetime import datetime, timedelta, timezone
from typing import List
from .interfaces import CoinFetcher, CoinRepository, CoinAnalyzer, RecommendationService, CronJobManager

# Load environment variables from .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='/.env')  # Explicit path for Docker compatibility
except ImportError:
    pass  # If dotenv is not installed, skip (but recommend installing for local dev)

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
}
ANALYSIS_VIEW = 'analysis_summary'

class DefaultCoinFetcher:
    def fetch(self) -> None:
        print("[Scheduler] Fetching new coins...")
        subprocess.run(["python", "-m", "NewCoins.main"], check=True)

class PostgresCoinRepository:
    def get_new_symbols(self) -> List[str]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        cur.execute(
            f"SELECT symbol FROM {os.getenv('POSTGRES_TABLE', 'coins')} WHERE time_start >= %s",
            (since,)
        )
        coins = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"[Scheduler] Found new coins: {coins}")
        return coins

    def get_new_symbols_with_time(self) -> List[tuple]:
        """
        Returns a list of (symbol, time_start) tuples for new coins scheduled to launch in the next 24 hours.
        """
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        now = datetime.now(timezone.utc)
        next_24h = now + timedelta(hours=24)
        cur.execute(
            f"SELECT symbol, time_start FROM {os.getenv('POSTGRES_TABLE', 'coins')} WHERE time_start >= %s AND time_start <= %s",
            (now, next_24h)
        )
        coins = [(row[0], row[1]) for row in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"[Scheduler] Found new coins with times (next 24h): {coins}")
        return coins


class DefaultCoinAnalyzer:
    def analyze(self, symbols: List[str]) -> None:
        if not symbols:
            print("[Scheduler] No new coins to analyze.")
            return
        coin_str = ','.join(symbols)
        print(f"[Scheduler] Analyzing: {coin_str}")
        subprocess.run(["python", "main.py", "analyze", coin_str], check=True)

class PostgresRecommendationService:
    def get_qualified(self) -> List[str]:
        # Always fetch the latest threshold from the environment
        threshold_env = os.getenv('SCORE_THRESHOLD')
        try:
            threshold = float(threshold_env) if threshold_env is not None else 70.0
        except ValueError:
            threshold = 70.0
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(f"SELECT symbol FROM {ANALYSIS_VIEW} WHERE total_score >= %s", (threshold,))
        coins = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"[Scheduler] Qualified coins for trading (score >= {threshold}): {coins}")
        return coins

import subprocess

class PrintCronJobManager:
    def create_jobs(self, symbol_times: list) -> None:
        if not symbol_times:
            print("[Scheduler] No coins qualified for trading.")
            return
        # Get current crontab
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, check=False)
            current_crontab = result.stdout if result.returncode == 0 else ''
        except Exception as e:
            print(f"[Scheduler] Could not read current crontab: {e}")
            current_crontab = ''

        new_jobs = []
        import os
        from datetime import timedelta
        import sys, os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from src.utils.cron_db import save_cronjob
        for symbol, time_start in symbol_times:
            # Convert time_start (datetime) to cron format
            if isinstance(time_start, str):
                from dateutil import parser
                dt = parser.parse(time_start)
            else:
                dt = time_start
            minute = dt.minute
            hour = dt.hour
            day = dt.day
            month = dt.month
            # Weekday is optional, use '*'
            cron_time = f"{minute} {hour} {day} {month} *"
            buy_job = f"{cron_time} /usr/bin/python -m Trade.main buy {symbol}"

            # Get SELL_AFTER_MIN from env, default 10
            sell_after_min = int(os.getenv('SELL_AFTER_MIN', 10))
            sell_dt = dt + timedelta(minutes=sell_after_min)
            sell_minute = sell_dt.minute
            sell_hour = sell_dt.hour
            sell_day = sell_dt.day
            sell_month = sell_dt.month
            sell_cron_time = f"{sell_minute} {sell_hour} {sell_day} {sell_month} *"
            sell_job = f"{sell_cron_time} /usr/bin/python -m Trade.main sell {symbol}"

            if buy_job not in current_crontab:
                new_jobs.append(buy_job)
                save_cronjob(cron_time, f"/usr/bin/python -m Trade.main buy {symbol}")
            if sell_job not in current_crontab:
                new_jobs.append(sell_job)
                save_cronjob(sell_cron_time, f"/usr/bin/python -m Trade.main sell {symbol}")

        if new_jobs:
            # Combine existing crontab with new jobs
            updated_crontab = current_crontab.strip() + '\n' + '\n'.join(new_jobs) + '\n'
            try:
                proc = subprocess.run(['crontab', '-'], input=updated_crontab, text=True, check=True)
                for job in new_jobs:
                    print(f"[Scheduler] Added cronjob: {job}")
            except Exception as e:
                print(f"[Scheduler] Failed to update crontab: {e}")
        else:
            print("[Scheduler] All relevant cronjobs already exist.")

# Note: You must install python-dateutil for date parsing if not already present.


