"""
Cache implementation that follows SOLID principles.
Separates concerns into distinct components.
"""
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from .interfaces import ICache


class Cache(ICache):
    """
    File-based cache implementation.
    Follows SOLID principles:
    - Single Responsibility: Handles caching
    - Open/Closed: Can be extended with new caching strategies
    - Interface Segregation: Implements ICache interface
    - Dependency Inversion: Can be replaced with other implementations
    """
    
    def __init__(self, 
                 cache_dir: str, 
                 cache_duration: int = 3600):
        """
        Initialize the cache
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration: Duration in seconds to keep cached data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_duration = cache_duration
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data by key
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if exists and not expired, None otherwise
        """
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None
            
        try:
            # Check if cache is expired
            if time.time() - cache_file.stat().st_mtime > self.cache_duration:
                cache_file.unlink()
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data['data']
                
        except Exception as e:
            raise CacheError(f"Error reading cache for {key}: {str(e)}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set data in cache with TTL
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds (optional)
        """
        cache_file = self._get_cache_file(key)
        
        try:
            data = {
                'data': value,
                'timestamp': time.time(),
                'ttl': ttl or self.cache_duration
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            raise CacheError(f"Error writing cache for {key}: {str(e)}")
    
    def clear(self) -> None:
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob('*'):
            try:
                cache_file.unlink()
            except Exception as e:
                raise CacheError(f"Error clearing cache: {str(e)}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key"""
        # Use MD5 hash of the key to create a safe filename
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"cache_{hash_key}.json"
