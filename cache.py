# In utils.py or a new cache.py
import time

_cache = {}

def cache_set(key, value, ttl=60):
    _cache[key] = (value, time.time() + ttl)

def cache_get(key):
    value, expires = _cache.get(key, (None, 0))
    if time.time() > expires:
        _cache.pop(key, None)
        return None
    return value
