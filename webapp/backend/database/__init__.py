"""
Database utilities for the webapp backend.
"""

# Export helper functions
from .helpers import (
    execute_query_to_dict,
    get_all_records,
    get_record_by_id,
    get_record_or_404,
    get_cached_data,
    execute_query_with_error_handling,
    execute_collection_query
)

# Export specialized repositories
from .repositories import (
    AnalysisRepository,
    CoinRepository,
    CronRepository
)

__all__ = [
    # Helper functions
    'execute_query_to_dict',
    'get_all_records',
    'get_record_by_id',
    'get_record_or_404',
    'get_cached_data',
    'execute_query_with_error_handling',
    'execute_collection_query',
    
    # Repositories
    'AnalysisRepository',
    'CoinRepository',
    'CronRepository'
]
