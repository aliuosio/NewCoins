#!/usr/bin/env python3
"""
Repository for cryptocurrency coin data operations.
"""
import os
import logging
import pytz
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from ..repository import DatabaseRepository

logger = logging.getLogger(__name__)

class CoinRepository:
    """
    Repository for cryptocurrency coin data operations.
    Implements the repository pattern for coin-specific database operations.
    """
    
    @staticmethod
    def _get_table_name() -> str:
        """Get the coins table name from environment variables"""
        return os.getenv('POSTGRES_TABLE', 'coins')
    
    @staticmethod
    def insert_new_coins(coins) -> bool:
        """
        Persist a list of NewCoin instances into the database.
        
        Args:
            coins: List of NewCoin instances to persist
            
        Returns:
            True if successful, False otherwise
        """
        if not coins:
            return True
            
        try:
            # Prepare data for batch insert
            data_list = [
                {
                    "name": c.name,
                    "symbol": c.symbol,
                    "time_start": datetime.fromtimestamp(int(c.start_time) / 1000, tz=pytz.utc),
                    "futures": c.futures
                }
                for c in coins
            ]
            
            # Use DatabaseRepository for batch insert
            table = CoinRepository._get_table_name()
            return DatabaseRepository.batch_insert_or_update(table, data_list, "symbol")
        except Exception as e:
            logger.error(f"Error inserting new coins: {e}")
            return False
    
    @staticmethod
    def get_all_coins(limit: int = None, order_by: str = "time_start DESC") -> List[Dict[str, Any]]:
        """
        Get all coins from the database.
        
        Args:
            limit: Maximum number of results to return
            order_by: Column to order by
            
        Returns:
            List of coin records as dictionaries
        """
        table = CoinRepository._get_table_name()
        query = f"SELECT * FROM {table} ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
            
        return DatabaseRepository.execute_query_to_dict(query) or []
    
    @staticmethod
    def get_coin_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get a coin by its symbol.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Coin record as dictionary or None if not found
        """
        table = CoinRepository._get_table_name()
        return DatabaseRepository.get_record_by_id(table, "symbol", symbol)
    
    @staticmethod
    def get_coins_by_symbols(symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple coins by their symbols.
        
        Args:
            symbols: List of cryptocurrency symbols
            
        Returns:
            List of coin records as dictionaries
        """
        if not symbols:
            return []
            
        table = CoinRepository._get_table_name()
        return DatabaseRepository.get_records_by_ids(table, "symbol", symbols)
    
    @staticmethod
    def get_coin_start_time(symbol: str) -> Optional[datetime]:
        """
        Get the start time for a specific coin.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Start time as datetime or None if not found
        """
        table = CoinRepository._get_table_name()
        query = f"SELECT time_start FROM {table} WHERE symbol = %s"
        result = DatabaseRepository.execute_query(query, (symbol,), fetch_all=False)
        
        if result and result[0]:
            return result[0]
        return None
