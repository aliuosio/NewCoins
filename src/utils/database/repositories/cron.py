#!/usr/bin/env python3
"""
Repository for cronjob data operations.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from ..repository import DatabaseRepository

logger = logging.getLogger(__name__)

class CronRepository:
    """
    Repository for cronjob data operations.
    Implements the repository pattern for cronjob-specific database operations.
    """
    
    @staticmethod
    def _get_table_name() -> str:
        """Get the cronjobs table name"""
        return "cronjobs"
    
    @staticmethod
    def save_cronjob(schedule: str, command: str) -> bool:
        """
        Save a new cronjob record to the database.
        
        Args:
            schedule: Cron schedule expression
            command: Command to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "schedule": schedule,
                "command": command,
                "created_at": datetime.now()
            }
            
            table = CronRepository._get_table_name()
            DatabaseRepository.insert_or_update(table, data)
            return True
        except Exception as e:
            logger.exception(f"Error saving cronjob: {str(e)}")
            return False

    @staticmethod
    def get_cronjobs() -> List[Tuple]:
        """
        Get all cronjobs from the database.
        
        Returns:
            List of cronjob records as tuples (id, schedule, command, created_at)
        """
        table = CronRepository._get_table_name()
        query = f"SELECT id, schedule, command, created_at FROM {table} ORDER BY created_at DESC"
        return DatabaseRepository.execute_query(query) or []
    
    @staticmethod
    def get_cronjobs_as_dict() -> List[Dict[str, Any]]:
        """
        Get all cronjobs from the database as dictionaries.
        
        Returns:
            List of cronjob records as dictionaries
        """
        table = CronRepository._get_table_name()
        query = f"SELECT id, schedule, command, created_at FROM {table} ORDER BY created_at DESC"
        return DatabaseRepository.execute_query_to_dict(query) or []
    
    @staticmethod
    def delete_cronjob(cronjob_id: int) -> bool:
        """
        Delete a cronjob from the database.
        
        Args:
            cronjob_id: ID of the cronjob to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            table = CronRepository._get_table_name()
            query = f"DELETE FROM {table} WHERE id = %s"
            DatabaseRepository.execute_query(query, (cronjob_id,))
            return True
        except Exception as e:
            logger.exception(f"Error deleting cronjob: {str(e)}")
            return False
