"""
Core utilities - Cache management and helper functions.
"""
from django.core.cache import cache
from typing import Optional, Any
import hashlib
import json


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a consistent cache key from arguments.
    
    Args:
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        str: A unique cache key
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def get_cached_or_set(key: str, callable_func, timeout: int = 300) -> Any:
    """
    Get value from cache or set it by calling the provided function.
    
    Args:
        key: Cache key
        callable_func: Function to call if cache miss
        timeout: Cache timeout in seconds (default: 5 minutes)
    
    Returns:
        Cached or computed value
    """
    value = cache.get(key)
    if value is None:
        value = callable_func()
        cache.set(key, value, timeout)
    return value


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match (e.g., 'salon_*')
    
    Returns:
        Number of keys deleted
    """
    # Note: This requires django-redis backend
    from django_redis import get_redis_connection
    conn = get_redis_connection("default")
    
    keys = conn.keys(f"salon:{pattern}")
    if keys:
        return conn.delete(*keys)
    return 0


def invalidate_salon_cache(salon_id: int) -> None:
    """
    Invalidate all cache entries related to a salon.
    
    Args:
        salon_id: ID of the salon
    """
    cache.delete(f'salon_detail_{salon_id}')
    cache.delete(f'salon_rating_{salon_id}')
    invalidate_cache_pattern(f'salon_list_*')


def invalidate_stylist_cache(stylist_id: int) -> None:
    """
    Invalidate all cache entries related to a stylist.
    
    Args:
        stylist_id: ID of the stylist
    """
    cache.delete(f'stylist_rating_{stylist_id}')
    cache.delete(f'stylist_availability_{stylist_id}_*')
