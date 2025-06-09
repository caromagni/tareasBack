from flask_caching import Cache

cache = Cache()

print("CACHE MODULE INITIALIZED")

# Define cache timeout variables
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour
CACHE_TIMEOUT_LONG = (3600 * 6 ) # 6 hours
