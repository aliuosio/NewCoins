#!/usr/bin/env python3
"""
Repository for cryptocurrency social indicators data operations.
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

from ..repository import DatabaseRepository

logger = logging.getLogger(__name__)

class SocialRepository:
    """
    Repository for cryptocurrency social indicators data operations.
    Implements the repository pattern for social-specific database operations.
    """
    
    @staticmethod
    def _get_table_name() -> str:
        """Get the social table name from environment variables"""
        return os.getenv('POSTGRES_SOCIAL_TABLE', 'analyse_social')
    
    @staticmethod
    def process_social_results(results: List, symbol: str) -> Dict[str, Any]:
        """
        Process social indicator results and extract data for database storage.
        
        Args:
            results: List of social indicator results
            symbol: Cryptocurrency symbol
            
        Returns:
            Dictionary of processed data ready for database insertion
        """
        if not results:
            return None
            
        try:
            # Prepare indicator-specific data
            indicator_data = {}
            
            # Only save scores that exist in the table schema
            valid_scores = [
                'social_volume',
                'sentiment_analysis',
                'developer_activity',
                'community_growth',
                'google_trends'
            ]
            
            for result in results:
                indicator_name = result.indicator_name
                if indicator_name in valid_scores:
                    indicator_data[f"{indicator_name}_score"] = result.score
            
            # Prepare the insert data
            insert_data = {
                "symbol": symbol
            }
            
            # Add indicator-specific data (scores)
            insert_data.update(indicator_data)
            
            return insert_data
        except Exception as e:
            logger.error(f"Error processing social results for {symbol}: {e}")
            return None

    @staticmethod
    def save_social_results(results: List, symbol: str, conn=None) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Save the social indicators results to the database.
        
        Args:
            results: List of social indicator results (IndicatorResult objects)
            symbol: Cryptocurrency symbol
            conn: Optional database connection (if not provided, will create one)
        
        Returns:
            Tuple of (SQL query, parameters) if conn is None, otherwise executes the query and returns None
        """
        if not results:
            logger.warning(f"No social results to save for {symbol}")
            return None
        
        table = SocialRepository._get_table_name()
        
        try:
            # Process the results to get the data for insertion
            insert_data = SocialRepository.process_social_results(results, symbol)
            if not insert_data:
                return None
                
            if conn:
                # Use the connection directly with DatabaseRepository
                DatabaseRepository.insert_or_update(table, insert_data, "symbol", conn)
                return None
            else:
                # Build the SQL query dynamically for batch operations
                fields = list(insert_data.keys())
                placeholders = [f"%({field})s" for field in fields]
                
                query = f"""
                INSERT INTO {table} ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (symbol) 
                DO UPDATE SET 
                    {', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field != 'symbol'])}
                """
                
                return query, insert_data
        except Exception as e:
            logger.error(f"Error saving social results for {symbol}: {e}")
            raise

    @staticmethod
    def save_social_results_batch(results_dict: Dict[str, List], conn=None) -> bool:
        """
        Save social results for multiple symbols in a single transaction.
        
        Args:
            results_dict: Dictionary mapping symbol to list of social indicator results
            conn: Optional database connection (if not provided, will create one)
            
        Returns:
            True if successful, False otherwise
        """
        if not results_dict:
            logger.warning("No social results to save")
            return True
        
        try:
            table = SocialRepository._get_table_name()
            data_list = []
            
            # Prepare all data for batch insert
            for symbol, results in results_dict.items():
                if not results:
                    continue
                    
                # Process the results for this symbol
                processed_data = SocialRepository.process_social_results(results, symbol)
                if processed_data:
                    data_list.append(processed_data)
            
            if not data_list:
                return True
                
            # Use DatabaseRepository for batch insert
            success = DatabaseRepository.batch_insert_or_update(table, data_list, "symbol", conn)
            
            if success:
                logger.info(f"Successfully saved social results for {len(data_list)} symbols")
            
            return success
        except Exception as e:
            logger.error(f"Error batch saving social results: {e}")
            return False

    @staticmethod
    def get_latest_social(symbols: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the latest social indicators from the database.
        
        Args:
            symbols: Optional list of cryptocurrency symbols to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of social indicator results as dictionaries
        """
        table = SocialRepository._get_table_name()
        
        try:
            if symbols:
                query = f"""
                SELECT * FROM {table}
                WHERE symbol IN %s
                ORDER BY analysis_date DESC
                LIMIT %s
                """
                return DatabaseRepository.execute_query_to_dict(query, (tuple(symbols), limit))
            else:
                query = f"""
                SELECT * FROM {table}
                ORDER BY analysis_date DESC
                LIMIT %s
                """
                return DatabaseRepository.execute_query_to_dict(query, (limit,))
        except Exception as e:
            logger.error(f"Error retrieving social indicators: {e}")
            return []
