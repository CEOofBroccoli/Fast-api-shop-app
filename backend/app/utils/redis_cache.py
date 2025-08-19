import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable, TypeVar
from functools import wraps
from datetime import timedelta
import json
import pickle

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for cache decorator

# Redis connection configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "redis_password")
REDIS_DB = int(os.environ.get("REDIS_DB", 0))


class RedisCache:
    """
    Redis cache implementation for FastAPI.
    
    Provides methods for storing and retrieving objects in Redis,
    with support for JSON serializable objects and binary data using pickle.
    """
    _instance = None
    _client = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                    db=REDIS_DB,
                    decode_responses=False,  # We handle encoding/decoding manually
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self._client.ping()
                logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
                self._client = None
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage in Redis."""
        try:
            # Try JSON first for simple types
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            # Fallback to pickle for complex objects
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from Redis."""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to pickle
            return pickle.loads(data)
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to store
            expire: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            return False
            
        try:
            serialized_value = self._serialize(value)
            result = self._client.set(key, serialized_value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self._client:
            return None
            
        try:
            data = self._client.get(key)
            if data is None:
                return None
            # Ensure data is bytes before deserializing
            if not isinstance(data, bytes):
                data = str(data).encode('utf-8')
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self._client:
            return False
            
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self._client:
            return False
            
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all cache entries."""
        if not self._client:
            return False
            
        try:
            result = self._client.flushdb()
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to flush cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._client:
            return {"status": "disconnected"}
            
        try:
            info = self._client.info()
            # Ensure info is a dict, not an awaitable
            if hasattr(info, '__await__'):
                # This shouldn't happen with sync redis client, but handle it
                logger.warning("Got awaitable from Redis info(), using fallback stats")
                return {"status": "connected", "error": "async_response_received"}
            
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A") if isinstance(info, dict) else "N/A",
                "connected_clients": info.get("connected_clients", 0) if isinstance(info, dict) else 0,
                "total_commands_processed": info.get("total_commands_processed", 0) if isinstance(info, dict) else 0,
                "keyspace_hits": info.get("keyspace_hits", 0) if isinstance(info, dict) else 0,
                "keyspace_misses": info.get("keyspace_misses", 0) if isinstance(info, dict) else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}


# Create global cache instance
cache = RedisCache()


def cached(
    expire: int = 300,
    prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator for caching function results.
    
    Args:
        expire: Cache expiration time in seconds (default: 5 minutes)
        prefix: Prefix for cache keys
        key_builder: Custom function to build cache keys
        
    Usage:
        @cached(expire=600, prefix="user:")
        def get_user(user_id: int):
            return fetch_user_from_db(user_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder
                key_parts = [prefix, func.__name__]
                if args:
                    key_parts.extend([str(arg) for arg in args])
                if kwargs:
                    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire=expire)
            return result
        
        return wrapper
    return decorator


# Async version of the cache decorator
def cached_async(
    expire: int = 300,
    prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Async version of the cache decorator.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key (same as sync version)
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [prefix, func.__name__]
                if args:
                    key_parts.extend([str(arg) for arg in args])
                if kwargs:
                    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, expire=expire)
            return result
        
        return wrapper
    return decorator