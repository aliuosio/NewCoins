#!/usr/bin/env python3
"""
Repository for cryptocurrency analysis data operations.
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

from ..repository import DatabaseRepository

logger = logging.getLogger(__name__)

class AnalysisRepository:
    """
    Repository for cryptocurrency analysis data operations.
    Implements the repository pattern for analysis-specific database operations.
    """
    
    @staticmethod
    def _get_table_name() -> str:
        """Get the analysis table name from environment variables"""
        return os.getenv('POSTGRES_ANALYSIS_TABLE', 'analyse_technical')
    
    @staticmethod
    def process_analysis_results(results: List, symbol: str) -> Dict[str, Any]:
        """
        Process analysis results and extract data for database storage.
        
        Args:
            results: List of indicator results
            symbol: Cryptocurrency symbol
            
        Returns:
            Dictionary of processed data ready for database insertion
        """
        if not results:
            return None
            
        try:
            # Calculate overall scores - filter out None values (not applicable indicators)
            valid_results = [r for r in results if r.score is not None]
            total_score = sum(r.score for r in valid_results)
            
            # For max_score, we only count the indicators that are applicable
            max_score = sum(r.max_score for r in valid_results)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            # Calculate percentage for informational purposes only
            percentage = round(percentage, 2)
            
            # Prepare indicator-specific data
            indicator_data = {}
            raw_data = {}
            
            for result in results:
                indicator_name = result.indicator_name
                
                # Handle not applicable indicators
                if result.score is None:
                    indicator_data[f"{indicator_name}_score"] = None
                    if indicator_name in ("pre_sale_vesting", "smart_contract_audit"):
                        indicator_data[f"{indicator_name}_applicable"] = False
                else:
                    indicator_data[f"{indicator_name}_score"] = result.score
                    if indicator_name in ("pre_sale_vesting", "smart_contract_audit"):
                        indicator_data[f"{indicator_name}_applicable"] = True
                
                # Store raw details for future reference
                raw_data[indicator_name] = result.details
            
            # Extract additional data points if available
            additional_data = {}
            
            # Market cap and supply data
            for result in results:
                if result.indicator_name == "token_distribution" and hasattr(result, "details"):
                    details = result.details
                    if "circulating_supply" in details:
                        additional_data["circulating_supply"] = details["circulating_supply"]
                    if "total_supply" in details:
                        additional_data["total_supply"] = details["total_supply"]
            
            # Trading volume data
            for result in results:
                if result.indicator_name == "trading_volume" and hasattr(result, "details"):
                    details = result.details
                    if "total_volume_24h" in details:
                        additional_data["trading_volume_24h"] = details["total_volume_24h"]
            
            # Vesting data
            for result in results:
                if result.indicator_name == "pre_sale_vesting" and hasattr(result, "details"):
                    details = result.details
                    if "upcoming_unlocks" in details:
                        additional_data["upcoming_unlocks"] = details["upcoming_unlocks"]
                    if "days_to_next_unlock" in details:
                        additional_data["days_to_next_unlock"] = details["days_to_next_unlock"]
                    if "unlock_percentage" in details:
                        # Remove % sign if present and convert to float
                        unlock_pct = details["unlock_percentage"]
                        if isinstance(unlock_pct, str) and "%" in unlock_pct:
                            unlock_pct = float(unlock_pct.replace("%", ""))
                        additional_data["unlock_percentage"] = unlock_pct
            
            # Audit data
            for result in results:
                if result.indicator_name == "smart_contract_audit" and hasattr(result, "details"):
                    details = result.details
                    if "audit_date" in details:
                        additional_data["audit_date"] = details["audit_date"]
                    if "audit_firm" in details:
                        additional_data["audit_firm"] = details["audit_firm"]
                    if "vulnerabilities" in details:
                        vuln_text = details["vulnerabilities"]
                        if vuln_text and isinstance(vuln_text, str):
                            # Parse "X critical, Y major" format
                            parts = vuln_text.split(",")
                            for part in parts:
                                if "critical" in part:
                                    additional_data["vulnerabilities_critical"] = int(part.split()[0])
                                if "major" in part:
                                    additional_data["vulnerabilities_major"] = int(part.split()[0])
            
            # Prepare the insert data
            insert_data = {
                "symbol": symbol
            }
            
            # Add indicator-specific data (scores)
            insert_data.update(indicator_data)
            insert_data.update(additional_data)
            
            return insert_data
        except Exception as e:
            logger.error(f"Error processing analysis results for {symbol}: {e}")
            return None

    @staticmethod
    def save_analysis_results(results: List, symbol: str, conn=None) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Save the analysis results to the database.
        
        Args:
            results: List of indicator results
            symbol: Cryptocurrency symbol
            conn: Optional database connection (if not provided, will create one)
        
        Returns:
            Tuple of (SQL query, parameters) if conn is None, otherwise executes the query and returns None
        """
        if not results:
            logger.warning(f"No analysis results to save for {symbol}")
            return None
        
        table = AnalysisRepository._get_table_name()
        
        try:
            # Process the results to get the data for insertion
            insert_data = AnalysisRepository.process_analysis_results(results, symbol)
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
            logger.error(f"Error saving analysis results for {symbol}: {e}")
            raise

    @staticmethod
    def save_analysis_results_batch(results_dict: Dict[str, List], conn=None) -> bool:
        """
        Save analysis results for multiple symbols in a single transaction.
        
        Args:
            results_dict: Dictionary mapping symbol to list of indicator results
            conn: Optional database connection (if not provided, will create one)
            
        Returns:
            True if successful, False otherwise
        """
        if not results_dict:
            logger.warning("No analysis results to save")
            return True
        
        try:
            # Process each symbol's results and collect data for batch insert
            data_list = []
            for symbol, results in results_dict.items():
                if not results:
                    continue
                    
                # Process the results for this symbol
                processed_data = AnalysisRepository.process_analysis_results(results, symbol)
                if processed_data:
                    data_list.append(processed_data)
            
            if not data_list:
                return True
                
            # Use DatabaseRepository for batch insert
            table = AnalysisRepository._get_table_name()
            success = DatabaseRepository.batch_insert_or_update(table, data_list, "symbol", conn)
            
            if success:
                logger.info(f"Successfully saved analysis results for {len(data_list)} symbols")
            
            return success
        except Exception as e:
            logger.error(f"Error batch saving analysis results: {e}")
            return False

    @staticmethod
    def get_latest_analysis(symbols: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the latest analysis results from the database.
        
        Args:
            symbols: Optional list of cryptocurrency symbols to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of analysis results as dictionaries
        """
        table = AnalysisRepository._get_table_name()
        
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
            logger.error(f"Error retrieving analysis results: {e}")
            return []
