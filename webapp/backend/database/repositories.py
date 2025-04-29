#!/usr/bin/env python3
"""
Domain-specific repositories for the webapp backend.
These repositories extend the core database repositories with web-specific functionality.
"""
import logging
from typing import List, Dict, Any, Optional

from src.utils.database import DatabaseRepository
from .helpers import execute_collection_query

logger = logging.getLogger(__name__)

class AnalysisRepository:
    """
    Repository for analysis-related database operations in the webapp.
    """
    
    @staticmethod
    def get_analysed_coins() -> List[str]:
        """
        Get all analyzed coin symbols from the analysis_summary table.
        
        Returns:
            List of analyzed coin symbols
        """
        def fetch_analysed_coins():
            results = DatabaseRepository.execute_query_to_dict(
                "SELECT symbol FROM analysis_summary ORDER BY symbol;"
            )
            return [result["symbol"] for result in results]
        
        return execute_collection_query(fetch_analysed_coins, "Error fetching analysed coins")

class CoinRepository:
    """
    Repository for coin-related database operations in the webapp.
    """
    
    @staticmethod
    def get_all_coins() -> List[Dict[str, Any]]:
        """
        Get all coins from the database.
        
        Returns:
            List of coin records
        """
        def fetch_coins():
            return DatabaseRepository.execute_query_to_dict(
                "SELECT * FROM coins ORDER BY time_start DESC;"
            )
        
        return execute_collection_query(fetch_coins, "Error fetching coins")
    
    @staticmethod
    def get_coin_data(symbol: str) -> Dict[str, Any]:
        """
        Get data for a specific coin by symbol.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Coin data as a dictionary
        """
        def fetch_coin_data():
            result = DatabaseRepository.execute_query_to_dict(
                "SELECT * FROM coins WHERE symbol = %s;",
                (symbol,),
                fetch_all=False
            )
            if not result:
                raise ValueError(f"Coin with symbol '{symbol}' not found")
            return result
        
        return execute_collection_query(fetch_coin_data, f"Error fetching coin data for {symbol}")
    
    @staticmethod
    def get_coin_start_time(symbol: str) -> Optional[str]:
        """
        Get the start time for a specific coin.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Start time as ISO format string or None if not found
        """
        def fetch_start_time():
            result = DatabaseRepository.execute_query_to_dict(
                "SELECT time_start FROM coins WHERE symbol = %s;",
                (symbol,),
                fetch_all=False
            )
            if not result:
                raise ValueError(f"Coin with symbol '{symbol}' not found")
            return result["time_start"].isoformat() if result["time_start"] else None
        
        return execute_collection_query(fetch_start_time, f"Error fetching start time for {symbol}")

class CronRepository:
    """
    Repository for cronjob-related database operations in the webapp.
    """
    
    @staticmethod
    def get_all_cronjobs() -> List[Dict[str, Any]]:
        """
        Get all cronjobs from the database.
        
        Returns:
            List of cronjob records
        """
        def fetch_cronjobs():
            results = DatabaseRepository.execute_query_to_dict(
                "SELECT id, schedule, command, created_at FROM cronjobs ORDER BY created_at DESC;"
            )
            # Format datetime for JSON response
            for result in results:
                if result["created_at"]:
                    result["created_at"] = result["created_at"].isoformat()
            return results
        
        return execute_collection_query(fetch_cronjobs, "Error fetching cronjobs")
