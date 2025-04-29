import subprocess
from utils.database.connection import DBConnection
import os
from datetime import datetime, timedelta, timezone
from typing import List
from Scheduler.interfaces import CoinFetcher, CoinRepository, CoinAnalyzer, RecommendationService, CronJobManager

ANALYSIS_VIEW = 'analysis_summary'

class DefaultCoinFetcher:
    def fetch(self) -> None:
        print("[Scheduler] Fetching new coins...")
        subprocess.run(["python", "-m", "NewCoins.main"], check=True)

class PostgresCoinRepository:
    def get_new_symbols(self) -> List[str]:
        with DBConnection() as conn:
            with conn.cursor() as cur:
                since = datetime.now(timezone.utc) - timedelta(hours=24)
                cur.execute(
                    f"SELECT symbol FROM {os.getenv('POSTGRES_TABLE', 'coins')} WHERE time_start >= %s",
                    (since,)
                )
                coins = [row[0] for row in cur.fetchall()]
            print(f"[Scheduler] Found new coins: {coins}")
            return coins

    def get_new_symbols_with_time(self) -> List[tuple]:
        """
        Returns a list of (symbol, time_start) tuples for new coins scheduled to launch in the next 24 hours.
        """
        with DBConnection() as conn:
            with conn.cursor() as cur:
                now = datetime.now(timezone.utc)
                next_24h = now + timedelta(hours=24)
                cur.execute(
                    f"SELECT symbol, time_start FROM {os.getenv('POSTGRES_TABLE', 'coins')} WHERE time_start >= %s AND time_start <= %s",
                    (now, next_24h)
                )
                coins = [(row[0], row[1]) for row in cur.fetchall()]
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
        with DBConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT symbol FROM {ANALYSIS_VIEW} WHERE FLOOR(score_percentage) >= %s", (threshold,))
                coins = [row[0] for row in cur.fetchall()]
            print(f"[Scheduler] Qualified coins for trading (score >= {threshold}): {coins}")
            return coins

import subprocess

class PrintCronJobManager:
    def create_jobs(self, symbol_times: list) -> None:
        if not symbol_times:
            print("[Scheduler] No coins qualified for trading.")
            return
            
        # Import required modules
        import os
        from datetime import timedelta
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from utils.database import CronRepository
        from dateutil import parser
        
        # Get current crontab
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, check=False)
            current_crontab = result.stdout if result.returncode == 0 else ''
        except Exception as e:
            print(f"[Scheduler] Could not read current crontab: {e}")
            current_crontab = ''

        # Get environment variables
        sell_after_min = int(os.getenv('SELL_AFTER_MIN', 10))
        
        # Helper function to create cron time string
        def format_cron_time(dt):
            return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
            
        # Helper function to create job string
        def format_job_string(cron_time, command):
            return f"{cron_time} {command}"
        
        # Helper function to process a single job
        def process_job(cron_time, command, job_type):
            job_string = format_job_string(cron_time, command)
            
            # Check if job already exists in crontab
            if job_string in current_crontab:
                return None
                
            # Save to database (will check for duplicates internally)
            CronRepository.save_cronjob(cron_time, command)
            
            # Return the job string for crontab update
            return job_string
        
        # Process all symbol times
        new_jobs = []
        for symbol, time_start in symbol_times:
            # Parse time_start if it's a string
            dt = parser.parse(time_start) if isinstance(time_start, str) else time_start
            
            # Calculate job times
            pre_trade_dt = dt - timedelta(minutes=5)
            buy_dt = dt
            sell_dt = dt + timedelta(minutes=sell_after_min)
            
            # Format cron times
            pre_trade_cron_time = format_cron_time(pre_trade_dt)
            buy_cron_time = format_cron_time(buy_dt)
            sell_cron_time = format_cron_time(sell_dt)
            
            # Format commands
            pre_trade_cmd = f"/usr/bin/python -m Trade.pre_trade {symbol}"
            buy_cmd = f"/usr/bin/python -m Trade.main buy {symbol}"
            sell_cmd = f"/usr/bin/python -m Trade.main sell {symbol}"
            
            # Process each job type
            pre_trade_job = process_job(pre_trade_cron_time, pre_trade_cmd, "pre-trade")
            buy_job = process_job(buy_cron_time, buy_cmd, "buy")
            sell_job = process_job(sell_cron_time, sell_cmd, "sell")
            
            # Add non-None jobs to the list
            for job in [pre_trade_job, buy_job, sell_job]:
                if job:
                    new_jobs.append(job)

        # Update crontab if we have new jobs
        if new_jobs:
            # Combine existing crontab with new jobs
            updated_crontab = current_crontab.strip() + '\n' + '\n'.join(new_jobs) + '\n'
            try:
                subprocess.run(['crontab', '-'], input=updated_crontab, text=True, check=True)
                for job in new_jobs:
                    print(f"[Scheduler] Added cronjob: {job}")
            except Exception as e:
                print(f"[Scheduler] Failed to update crontab: {e}")
        else:
            print("[Scheduler] All relevant cronjobs already exist.")

# Note: You must install python-dateutil for date parsing if not already present.


