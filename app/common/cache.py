from flask_caching import Cache
import os


cache = Cache()

print("CACHE MODULE INITIALIZED")

# Define cache timeout variables
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour
CACHE_TIMEOUT_LONG = (3600 * 6 ) # 6 hours

# Leer configuraciones de Redis desde variables de entorno

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))
redis_user = os.getenv('REDIS_USER', 'default')

""" redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))
redis_db = int(os.getenv('REDIS_DB'))
redis_user = os.getenv('REDIS_USER') """
print("REDIS CONFIGURATION:")

redis_password = os.getenv('REDIS_PASSWORD', None)
redis_prefix = os.getenv('CACHE_KEY_PREFIX', None)  # Namespace for keys

""" redis_password = os.getenv('REDIS_PASSWORD')
redis_prefix = os.getenv('CACHE_KEY_PREFIX')  # Namespace for keys """
print(f"Host: {redis_host}, Port: {redis_port}, DB: {redis_db}, User: {redis_user}, Password: {redis_password}, PREFIX: {redis_prefix}")