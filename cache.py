import time
from threading import Lock

_cache = {}
_cache_lock = Lock()

def cache_set(key, value, ttl=60):
    """Set a cache entry with a time-to-live (in seconds)."""
    with _cache_lock:
        _cache[key] = (value, time.time() + ttl)

def cache_get(key):
    """Retrieve a cache entry if it hasn't expired; else return None."""
    with _cache_lock:
        entry = _cache.get(key)
        if not entry:
            return None
        value, expires = entry
        if time.time() > expires:
            _cache.pop(key, None)
            return None
        return value

def cache_clear():
    """Clear all cached entries."""
    with _cache_lock:
        _cache.clear()
