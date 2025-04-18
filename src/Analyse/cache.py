"""
Cache implementation for API responses and other data
"""
import os
import time
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Cache:
    """
    Cache implementation for storing and retrieving API responses
    
    Uses both in-memory cache and disk-based persistence
    """
    
    def __init__(self, cache_dir: str, cache_duration: int = 3600):
        """
        Initialize the cache
        
        Args:
            cache_dir: Directory to store cached files
            cache_duration: Duration in seconds for which cached data is valid
        """
        self._cache_dir = Path(cache_dir)
        self._cache_duration = cache_duration
        
        # In-memory cache for faster access
        self._cache = {}  # type: Dict[str, Dict[str, Any]]
        self._cache_expiry = {}  # type: Dict[str, float]
        
        # Ensure cache directory exists
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized cache with directory: {cache_dir}")
        logger.info(f"Cache duration set to: {cache_duration}s")
    
    def _get_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a unique cache key based on URL and parameters
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Unique cache key as string
        """
        # Create a hash of the URL and parameters for unique cache key
        key_data = url + (json.dumps(params, sort_keys=True) if params else "")
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached data if available and not expired
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Cached data if available and not expired, None otherwise
        """
        cache_key = self._get_cache_key(url, params)
        current_time = time.time()
        
        # Check in-memory cache first
        if cache_key in self._cache and current_time < self._cache_expiry[cache_key]:
            logger.debug(f"Cache hit (memory): {cache_key}")
            return self._cache[cache_key]
        
        # Check disk cache if not in memory
        cache_file = self._cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                # Check if cache is still valid
                if current_time < cached_data.get('_expiry', 0):
                    logger.debug(f"Cache hit (disk): {cache_key}")
                    # Update in-memory cache
                    self._cache[cache_key] = cached_data['data']
                    self._cache_expiry[cache_key] = cached_data['_expiry']
                    return cached_data['data']
            except Exception as e:
                logger.error(f"Error reading cache file {cache_file}: {str(e)}")
        
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def set(self, url: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> None:
        """
        Store data in cache
        
        Args:
            url: API endpoint URL
            data: Data to cache
            params: Query parameters
        """
        cache_key = self._get_cache_key(url, params)
        current_time = time.time()
        expiry_time = current_time + self._cache_duration
        
        # Store in memory
        self._cache[cache_key] = data
        self._cache_expiry[cache_key] = expiry_time
        
        # Store on disk
        cache_file = self._cache_dir / f"{cache_key}.json"
        cache_data = {
            'data': data,
            '_expiry': expiry_time
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.debug(f"Cached data for {cache_key}")
        except Exception as e:
            logger.error(f"Error writing cache file {cache_file}: {str(e)}")
    
    def clear(self) -> None:
        """
        Clear all cached data
        """
        # Clear in-memory cache
        self._cache.clear()
        self._cache_expiry.clear()
        
        # Clear disk cache
        for cache_file in self._cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"Error removing cache file {cache_file}: {str(e)}")
        
        logger.info("Cache cleared")
