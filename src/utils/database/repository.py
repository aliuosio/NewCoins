#!/usr/bin/env python3
"""
Generic database repository pattern implementation for centralized database operations.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple, Union, TypeVar, Generic, Callable
import psycopg2
from psycopg2.extras import execute_values

from .connection import DBConnection

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DatabaseRepository:
    """
    Generic repository for database operations following the repository pattern.
    Centralizes common database operations to reduce code duplication.
    """
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch_all: bool = True, 
                      conn = None) -> Union[List[Tuple], Tuple, None]:
        """
        Execute a database query and return the results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_all: If True, return all rows, otherwise return a single row
            conn: Optional existing database connection
            
        Returns:
            Query results as a list of tuples, a single tuple, or None
        """
        close_conn = False
        try:
            if conn is None:
                conn = DBConnection().__enter__()
                close_conn = True
                
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                if fetch_all:
                    return cur.fetchall()
                else:
                    return cur.fetchone()
                    
        except Exception as e:
            logger.exception(f"Database query error: {str(e)}")
            return [] if fetch_all else None
        finally:
            if close_conn and conn:
                conn.commit()
                DBConnection().putconn(conn)
    
    @staticmethod
    def execute_query_to_dict(query: str, params: tuple = None, fetch_all: bool = True,
                             conn = None) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Execute a database query and return results as dictionaries.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_all: If True, return all rows as a list of dictionaries, otherwise return a single dictionary
            conn: Optional existing database connection
            
        Returns:
            Query results as dictionaries, or None if no results
        """
        close_conn = False
        try:
            if conn is None:
                conn = DBConnection().__enter__()
                close_conn = True
                
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cur.description]
                
                if fetch_all:
                    rows = cur.fetchall()
                    if not rows:
                        return []
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    row = cur.fetchone()
                    if not row:
                        return None
                    return dict(zip(columns, row))
                    
        except Exception as e:
            logger.exception(f"Database query error: {str(e)}")
            return [] if fetch_all else None
        finally:
            if close_conn and conn:
                conn.commit()
                DBConnection().putconn(conn)
    
    @staticmethod
    def get_table_columns(table_name: str, conn = None) -> List[str]:
        """
        Get the column names for a table.
        
        Args:
            table_name: Name of the table
            conn: Optional existing database connection
            
        Returns:
            List of column names
        """
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position;
        """
        rows = DatabaseRepository.execute_query(query, (table_name,), True, conn)
        return [row[0] for row in rows] if rows else []
    
    @staticmethod
    def get_all_records(table_name: str, order_by: str = None, conn = None) -> List[Dict[str, Any]]:
        """
        Get all records from a table.
        
        Args:
            table_name: Name of the table to query
            order_by: Optional column to order by
            conn: Optional existing database connection
            
        Returns:
            List of records as dictionaries
        """
        query = f"SELECT * FROM {table_name}"
        if order_by:
            query += f" ORDER BY {order_by}"
        return DatabaseRepository.execute_query_to_dict(query, None, True, conn)
    
    @staticmethod
    def get_record_by_id(table_name: str, id_column: str, id_value: Any, conn = None) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.
        
        Args:
            table_name: Name of the table to query
            id_column: Name of the ID column
            id_value: Value of the ID to look for
            conn: Optional existing database connection
            
        Returns:
            Record as dictionary or None if not found
        """
        query = f"SELECT * FROM {table_name} WHERE {id_column} = %s"
        return DatabaseRepository.execute_query_to_dict(query, (id_value,), False, conn)
    
    @staticmethod
    def get_records_by_ids(table_name: str, id_column: str, id_values: List[Any], 
                          order_by: str = None, limit: int = None, conn = None) -> List[Dict[str, Any]]:
        """
        Get multiple records by their IDs.
        
        Args:
            table_name: Name of the table to query
            id_column: Name of the ID column
            id_values: List of ID values to look for
            order_by: Optional column to order by
            limit: Optional maximum number of records to return
            conn: Optional existing database connection
            
        Returns:
            List of records as dictionaries
        """
        query = f"SELECT * FROM {table_name} WHERE {id_column} IN %s"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        return DatabaseRepository.execute_query_to_dict(query, (tuple(id_values),), True, conn)
    
    @staticmethod
    def insert_or_update(table_name: str, data: Dict[str, Any], 
                         id_column: str = None, conn = None) -> Optional[Any]:
        """
        Insert or update a record in the database.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column names and values
            id_column: Name of the ID column for UPSERT operations (if None, simple INSERT)
            conn: Optional existing database connection
            
        Returns:
            ID of the inserted/updated record if available, otherwise None
        """
        close_conn = False
        try:
            if conn is None:
                conn = DBConnection().__enter__()
                close_conn = True
            
            with conn.cursor() as cur:
                fields = list(data.keys())
                placeholders = [f"%({field})s" for field in fields]
                
                if id_column and id_column in data:
                    # Build UPSERT query
                    query = f"""
                    INSERT INTO {table_name} ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                    ON CONFLICT ({id_column}) 
                    DO UPDATE SET 
                        {', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field != id_column])}
                    RETURNING {id_column}
                    """
                else:
                    # Build simple INSERT query
                    query = f"""
                    INSERT INTO {table_name} ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                    RETURNING {id_column if id_column else fields[0]}
                    """
                
                cur.execute(query, data)
                result = cur.fetchone()
                
                if close_conn:
                    conn.commit()
                
                return result[0] if result else None
                
        except Exception as e:
            logger.exception(f"Error inserting/updating record in {table_name}: {str(e)}")
            return None
        finally:
            if close_conn and conn:
                conn.commit()
                DBConnection().putconn(conn)
    
    @staticmethod
    def batch_insert_or_update(table_name: str, data_list: List[Dict[str, Any]], 
                              id_column: str = None, conn = None) -> bool:
        """
        Insert or update multiple records in a single transaction.
        
        Args:
            table_name: Name of the table
            data_list: List of dictionaries containing column names and values
            id_column: Name of the ID column for UPSERT operations (if None, simple INSERT)
            conn: Optional existing database connection
            
        Returns:
            True if successful, False otherwise
        """
        if not data_list:
            return True
            
        close_conn = False
        try:
            if conn is None:
                conn = DBConnection().__enter__()
                close_conn = True
            
            # Get the actual columns from the database schema
            valid_columns = DatabaseRepository.get_table_columns(table_name, conn)
            if not valid_columns:
                logger.error(f"Could not retrieve columns for table {table_name}")
                return False
                
            # Filter out fields that don't exist in the database schema
            filtered_data_list = []
            for data in data_list:
                filtered_data = {k: v for k, v in data.items() if k in valid_columns}
                filtered_data_list.append(filtered_data)
            
            # If we filtered out all fields, return early
            if not filtered_data_list[0]:
                logger.error(f"No valid fields found for table {table_name}")
                return False
            
            with conn.cursor() as cur:
                # Use the filtered data
                fields = list(filtered_data_list[0].keys())
                
                if id_column and id_column in fields:
                    # Process each record individually for UPSERT
                    for data in filtered_data_list:
                        placeholders = [f"%({field})s" for field in fields]
                        query = f"""
                        INSERT INTO {table_name} ({', '.join(fields)})
                        VALUES ({', '.join(placeholders)})
                        ON CONFLICT ({id_column}) 
                        DO UPDATE SET 
                            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field != id_column])}
                        """
                        cur.execute(query, data)
                else:
                    # Use execute_values for bulk insert
                    values = [[data.get(field) for field in fields] for data in filtered_data_list]
                    query = f"""
                    INSERT INTO {table_name} ({', '.join(fields)})
                    VALUES %s
                    """
                    execute_values(cur, query, values)
                
                if close_conn:
                    conn.commit()
                
                return True
                
        except Exception as e:
            logger.exception(f"Error batch inserting/updating records in {table_name}: {str(e)}")
            return False
        finally:
            if close_conn and conn:
                conn.commit()
                DBConnection().putconn(conn)
