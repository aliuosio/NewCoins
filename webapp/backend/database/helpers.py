#!/usr/bin/env python3
"""
Database helper utilities for the webapp backend.
"""
import logging
import os
import time
from typing import Dict, List, Any, Union, Tuple, Optional
from fastapi import HTTPException

from src.utils.database.repository import DatabaseRepository

logger = logging.getLogger(__name__)

# Cache settings - can be reused across modules
API_CACHE_ENABLED = os.getenv("API_CACHE_ENABLED", "true").lower() == "true"
API_CACHE_DURATION = int(os.getenv("API_CACHE_DURATION", "300"))  # 5 minutes default

# In-memory cache dictionary - can be shared across modules
_cache: Dict[str, Dict[str, Any]] = {}

def execute_query_to_dict(query: str, params: tuple = None, fetch_all: bool = True) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
    """
    Execute a database query and return results as dictionaries.
    
    Args:
        query: SQL query to execute
        params: Query parameters
        fetch_all: If True, return all rows as a list of dictionaries, otherwise return a single dictionary
        
    Returns:
        Query results as dictionaries, or None if no results
    """
    return DatabaseRepository.execute_query_to_dict(query, params, fetch_all)

def get_all_records(table_name: str, order_by: str = None) -> List[Dict[str, Any]]:
    """
    Get all records from a table.
    
    Args:
        table_name: Name of the table to query
        order_by: Optional column to order by
        
    Returns:
        List of records as dictionaries
    """
    return DatabaseRepository.get_all_records(table_name, order_by)

def get_record_by_id(table_name: str, id_column: str, id_value: Any) -> Optional[Dict[str, Any]]:
    """
    Get a single record by ID.
    
    Args:
        table_name: Name of the table to query
        id_column: Name of the ID column
        id_value: Value of the ID to look for
        
    Returns:
        Record as dictionary or None if not found
    """
    return DatabaseRepository.get_record_by_id(table_name, id_column, id_value)

def get_record_or_404(table_name: str, id_column: str, id_value: Any, error_message: str = None) -> Dict[str, Any]:
    """
    Get a single record by ID or raise a 404 error if not found.
    
    Args:
        table_name: Name of the table to query
        id_column: Name of the ID column
        id_value: Value of the ID to look for
        error_message: Optional custom error message
        
    Returns:
        Record as dictionary
        
    Raises:
        HTTPException: If record not found
    """
    result = get_record_by_id(table_name, id_column, id_value)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=error_message or f"Record with {id_column}='{id_value}' not found in {table_name}."
        )
    return result

def get_cached_data(cache_key: str, data_fetcher_func, *args, **kwargs) -> Any:
    """
    Get data from cache or fetch it using the provided function if not in cache or expired.
    
    Args:
        cache_key: Unique key for the cache entry
        data_fetcher_func: Function to call to fetch the data if not in cache
        *args, **kwargs: Arguments to pass to the data_fetcher_func
        
    Returns:
        Cached or freshly fetched data
    """
    if API_CACHE_ENABLED:
        cache_entry = _cache.get(cache_key)
        
        if cache_entry:
            # Check if cache is still valid
            current_time = time.time()
            if current_time - cache_entry["timestamp"] < API_CACHE_DURATION:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cache_entry["data"]
            else:
                logger.debug(f"Cache expired for key: {cache_key}")
    
    # Fetch fresh data
    data = data_fetcher_func(*args, **kwargs)
    
    # Cache the result if caching is enabled
    if API_CACHE_ENABLED:
        _cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    return data

def execute_query_with_error_handling(query_func, error_message: str, *args, **kwargs) -> Any:
    """
    Execute a query function with standardized error handling.
    
    Args:
        query_func: Function to execute
        error_message: Error message prefix to use in case of exception
        *args, **kwargs: Arguments to pass to the query function
        
    Returns:
        Result of the query function
        
    Raises:
        HTTPException: If an error occurs during execution
    """
    try:
        return query_func(*args, **kwargs)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"{error_message}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")

def execute_collection_query(query_func, error_message: str, *args, **kwargs) -> List[Any]:
    """
    Execute a query function that returns a collection with standardized error handling.
    Returns an empty list instead of raising an exception on error.
    
    Args:
        query_func: Function to execute that returns a collection
        error_message: Error message prefix to use in case of exception
        *args, **kwargs: Arguments to pass to the query function
        
    Returns:
        Collection result from the query function or empty list on error
    """
    try:
        return execute_query_with_error_handling(query_func, error_message, *args, **kwargs)
    except HTTPException:
        logger.warning(f"Returning empty list due to {error_message.lower()}")
        return []
