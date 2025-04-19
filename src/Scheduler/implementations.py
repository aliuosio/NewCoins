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
    def create_jobs(self, symbols: List[str]) -> None:
        if not symbols:
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
        for symbol in symbols:
            buy_job = f"* * * * * /usr/bin/python -m Trade.main buy {symbol}"
            sell_job = f"* * * * * /usr/bin/python -m Trade.main sell {symbol}"
            if buy_job not in current_crontab:
                new_jobs.append(buy_job)
            if sell_job not in current_crontab:
                new_jobs.append(sell_job)

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

