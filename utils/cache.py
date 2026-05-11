"""
Simple in-memory cache to reduce Supabase API calls.
Caches product data for 5 minutes so pages load instantly.
"""
import time
from threading import Lock

_cache = {}
_lock = Lock()

def cache_get(key):
    """Get value from cache if not expired"""
    with _lock:
        if key in _cache:
            value, expiry = _cache[key]
            if time.time() < expiry:
                return value
            else:
                del _cache[key]
    return None

def cache_set(key, value, ttl=300):
    """Store value in cache with TTL in seconds (default 5 min)"""
    with _lock:
        _cache[key] = (value, time.time() + ttl)

def cache_delete(key):
    """Delete a specific cache key"""
    with _lock:
        _cache.pop(key, None)

def cache_clear_prefix(prefix):
    """Delete all keys starting with prefix"""
    with _lock:
        keys_to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del _cache[k]

def cache_clear_all():
    """Clear entire cache"""
    with _lock:
        _cache.clear()
