from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging
from database.repositories import CoinRepository
from database import execute_query_with_error_handling

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/coin_start_times")
def get_coin_start_times() -> List[Dict[str, Any]]:
    """
    Returns a list of coins with their symbol and start_time from the coins table.
    """
    # Get all coins and extract only the symbol and time_start fields
    coins = CoinRepository.get_all_coins()
    return [
        {"symbol": coin["symbol"], "time_start": coin["time_start"]} 
        for coin in coins
    ]

@router.get("/api/coin_start_time/{symbol}")
def get_coin_start_time(symbol: str) -> Dict[str, Any]:
    """
    Returns the start_time for a single coin symbol from the coins table.
    """
    # Get the coin data and extract only the symbol and time_start fields
    coin_data = CoinRepository.get_coin_data(symbol)
    if not coin_data:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")
    
    return {
        "symbol": coin_data["symbol"],
        "time_start": coin_data["time_start"]
    }

@router.get("/api/coins")
def get_all_coins() -> List[Dict[str, Any]]:
    """
    Returns all data for all coins from the coins table.
    """
    return CoinRepository.get_all_coins()

@router.get("/api/coin/{symbol}")
def get_coin_data(symbol: str) -> Dict[str, Any]:
    """
    Returns all data for a single coin symbol from the coins table.
    """
    coin_data = CoinRepository.get_coin_data(symbol)
    if not coin_data:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")
    return coin_data
