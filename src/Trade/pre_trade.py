#!/usr/bin/env python3
"""
Pre-trade script to fetch and cache necessary data for fast trade execution.
This script fetches price, exchange info, and balance data and stores it in RAM
for quick access during trade execution.
"""
import os
import json
import logging
import argparse
from typing import Dict, Any
from utils.mexc_api_factory import MEXCApiFactory
from .connection_pool import MEXCPoolClient, is_server_running

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define RAM directory (using /dev/shm which is RAM-based filesystem in Linux)
RAM_DIR = "/dev/shm"
CACHE_FILE = os.path.join(RAM_DIR, "mexc_trade_cache.json")

def fetch_and_cache_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch necessary data from MEXC API and cache it in RAM
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
    Returns:
        Dictionary with cached data
    """
    logger.info(f"Fetching pre-trade data for {symbol}")
    
    try:
        # Start connection pool if not running and initialize client
        if not is_server_running():
            logger.info("Starting connection pool server")
        
        # Initialize pool client (will start server if needed)
        client = MEXCPoolClient(start_if_not_running=True)
        
        # Test connection
        client.ping()
        logger.info("Connected to MEXC API via connection pool")
        
        # 1. Try to fetch price data (may not be available for new listings)
        price = None
        try:
            ticker_data = client.ticker_price(symbol)
            if isinstance(ticker_data, dict):
                price = float(ticker_data.get("price", 0)) if ticker_data.get("price") else None
            elif isinstance(ticker_data, list):
                for entry in ticker_data:
                    if entry.get("symbol") == symbol:
                        price = float(entry.get("price", 0)) if entry.get("price") else None
                        break
            
            if price:
                logger.info(f"Fetched price for {symbol}: {price}")
            else:
                logger.info(f"Price data not available for {symbol} (likely a new listing)")
        except Exception as e:
            logger.warning(f"Could not fetch price for {symbol}: {str(e)}")
            logger.info("This is normal for new listings before trading begins")
        
        # 2. Fetch exchange info (should be available even for new listings)
        exchange_info = client.exchange_info()
        symbol_info = next((s for s in exchange_info.get('symbols', []) if s['symbol'] == symbol), None)
        
        if not symbol_info:
            logger.warning(f"Symbol {symbol} not found in exchange info. This may be a very new listing or incorrect symbol.")
            logger.info("Will proceed with default values, but order may fail if symbol doesn't exist")
            min_notional = 0
            step_size = 0
            trading_status = "UNKNOWN"
        else:
            min_notional = 0
            step_size = 0
            trading_status = symbol_info.get('status', 'UNKNOWN')
            
            for f in symbol_info.get('filters', []):
                if f['filterType'] == 'MIN_NOTIONAL':
                    min_notional = float(f['minNotional'])
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
            
            logger.info(f"Fetched exchange info for {symbol}: status={trading_status}, min_notional={min_notional}, step_size={step_size}")
        
        # 3. Fetch balance
        account_info = client.account_info()
        usdt_balance = 0
        asset = symbol.replace('USDT', '')
        asset_balance = 0
        
        for balance in account_info.get('balances', []):
            if balance.get('asset') == 'USDT':
                usdt_balance = float(balance.get('free', 0))
            if balance.get('asset') == asset:
                asset_balance = float(balance.get('free', 0))
        
        logger.info(f"Fetched balances: USDT={usdt_balance}, {asset}={asset_balance}")
        
        # Create cache data
        server_time_response = client.time()
        server_time = int(server_time_response.get('serverTime', 0))
        
        # Calculate usable balance (99% of available to account for fees and fluctuations)
        usable_balance = usdt_balance * 0.99
        
        cache_data = {
            "symbol": symbol,
            "asset": asset,
            "price": price,  # May be None for new listings
            "min_notional": min_notional,
            "step_size": step_size,
            "usdt_balance": usdt_balance,
            "usable_balance": usable_balance,  # 99% of available balance
            "asset_balance": asset_balance,
            "trading_status": trading_status,
            "timestamp": server_time,
            "is_new_listing": price is None,  # Flag to indicate if this is likely a new listing
            "server_time": server_time,
            "connection_pool_active": True  # Flag to indicate connection pool is active
        }
        
        # Ensure RAM directory exists
        os.makedirs(RAM_DIR, exist_ok=True)
        
        # Write cache to RAM
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        
        logger.info(f"Pre-trade data cached successfully to {CACHE_FILE}")
        return cache_data
        
    except Exception as e:
        logger.error(f"Error fetching pre-trade data: {str(e)}")
        raise

def get_cached_data() -> Dict[str, Any]:
    """
    Get cached data from RAM
    
    Returns:
        Dictionary with cached data or empty dict if cache doesn't exist
    """
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Cache file {CACHE_FILE} not found")
            return {}
    except Exception as e:
        logger.error(f"Error reading cache: {str(e)}")
        return {}

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Pre-trade data fetcher and cacher')
    parser.add_argument('symbol', help='Trading pair symbol (e.g., BTCUSDT)')
    parser.add_argument('--force', action='store_true', help='Force cache update even if symbol is not found')
    
    args = parser.parse_args()
    symbol = args.symbol.upper()
    if not symbol.endswith('USDT'):
        symbol = f"{symbol}USDT"
    
    try:
        cache_data = fetch_and_cache_data(symbol)
        
        # Print status information
        print(f"Pre-trade data for {symbol} cached successfully:")
        print(json.dumps(cache_data, indent=2))
        
        if cache_data['is_new_listing']:
            print("\nNOTE: This appears to be a new listing as price data is not available.")
            print("The trade will use a market order with your USDT balance when executed.")
        
        if cache_data['trading_status'] != 'TRADING':
            print(f"\nWARNING: Symbol status is '{cache_data['trading_status']}', not 'TRADING'.")
            print("This may indicate the token is not yet available for trading.")
    except Exception as e:
        logger.error(f"Failed to fetch and cache data: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
