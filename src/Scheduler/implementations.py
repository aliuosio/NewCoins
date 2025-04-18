import subprocess
import psycopg2
import os
from datetime import datetime, timedelta, timezone
from typing import List
from .interfaces import CoinFetcher, CoinRepository, CoinAnalyzer, RecommendationService, CronJobManager

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'pad'),
    'user': os.getenv('POSTGRES_USER', 'SpecialOsio'),
    'password': os.getenv('POSTGRES_PASSWORD', 'oeh_ahb6Ahzah7exeish'),
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', 5432),
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
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(f"SELECT symbol FROM {ANALYSIS_VIEW} WHERE recommendation LIKE 'BUY%' OR recommendation LIKE 'STRONG BUY%'")
        coins = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"[Scheduler] Qualified coins for trading: {coins}")
        return coins

class PrintCronJobManager:
    def create_jobs(self, symbols: List[str]) -> None:
        if not symbols:
            print("[Scheduler] No coins qualified for trading.")
            return
        for symbol in symbols:
            job = f"* * * * * /usr/bin/python /src/Trade/fictive_trade.py {symbol}"
            print(f"[Scheduler] Would add cronjob: {job}")
