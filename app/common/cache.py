from flask_caching import Cache
import os


# Define cache timeout variables
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour
CACHE_TIMEOUT_LONG = (3600 * 6 ) # 6 hours

# Leer configuraciones de Redis desde variables de entorno

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))
redis_user = os.getenv('REDIS_USER', 'default')
redis_uses_password = os.getenv('REDIS_USES_PASSWORD', 'true').lower() == 'true'
cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
print("REDIS CONFIGURATION:")

redis_password = os.getenv('REDIS_PASSWORD', '')
redis_prefix = os.getenv('CACHE_KEY_PREFIX', None)  # Namespace for keys
#print(f"Host: {redis_host}, Port: {redis_port}, DB: {redis_db}, User: {redis_user}, Password_last_char: {redis_password[-1]}, PREFIX: {redis_prefix}, Enabled: {cache_enabled}")

cache = Cache()
