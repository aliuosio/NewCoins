import subprocess
import psycopg2
import os
from typing import List

# --- CONFIG ---
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'pad'),
    'user': os.getenv('POSTGRES_USER', 'SpecialOsio'),
    'password': os.getenv('POSTGRES_PASSWORD', 'oeh_ahb6Ahzah7exeish'),
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', 5432),
}
ANALYSIS_VIEW = 'analysis_summary'

# --- STEP 1: Fetch new coins ---
def fetch_new_coins():
    print("[Scheduler] Fetching new coins...")
    subprocess.run(["python", "-m", "NewCoins.main"], check=True)

# --- STEP 2: Read new coins from DB ---
def get_new_coin_symbols() -> List[str]:
    """
    Fetch symbols of coins added in the last 24 hours from the coins table.
    """
    from datetime import datetime, timedelta, timezone
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

# --- STEP 3: Analyze new coins ---
def analyze_coins(symbols: List[str]):
    if not symbols:
        print("[Scheduler] No new coins to analyze.")
        return
    coin_str = ','.join(symbols)
    print(f"[Scheduler] Analyzing: {coin_str}")
    subprocess.run(["python", "main.py", "analyze", coin_str], check=True)

# --- STEP 4: Query analysis view for recommendations ---
def get_qualified_coins() -> List[str]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"SELECT symbol FROM {ANALYSIS_VIEW} WHERE recommendation LIKE 'BUY%' OR recommendation LIKE 'STRONG BUY%'")
    coins = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    print(f"[Scheduler] Qualified coins for trading: {coins}")
    return coins

# --- STEP 5: Create cronjobs for fictive trade script ---
def create_cronjobs(symbols: List[str]):
    if not symbols:
        print("[Scheduler] No coins qualified for trading.")
        return
    for symbol in symbols:
        job = f"* * * * * /usr/bin/python /src/Trade/fictive_trade.py {symbol} \n"
        # This just prints the job; real implementation should add to crontab
        print(f"[Scheduler] Would add cronjob: {job.strip()}")
        # To actually install, you could use python-crontab or edit crontab directly

if __name__ == "__main__":
    fetch_new_coins()
    new_coins = get_new_coin_symbols()
    analyze_coins(new_coins)
    qualified = get_qualified_coins()
    create_cronjobs(qualified)
