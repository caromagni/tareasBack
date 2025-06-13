from common.cache import cache as cache_common
import time
def is_cache_healthy():
    """Check if cache is actually working"""
    if cache_common is None:
        return False
    try:
        # Try a simple operation
        cache_common.set('health_check', 'ok', timeout=1)
        return cache_common.get('health_check') == 'ok'
    except Exception:
        return False

def maybe_cache(timeout=600):
    def decorator(func):
    
        
        if is_cache_healthy():
            print("CACHE wrapper initialized - Redis is healthy"+"&&"*100)
            time.sleep(10)
            try:
                return cache_common.memoize(timeout)(func)
            except Exception as e:
                print(f"CACHE memoize failed: {e}")
                return func
        else:
            time.sleep(10)
            print("CACHE wrapper failed - Redis unhealthy, fallback to normal execution"+"&&"*100)
            return func
    return decorator