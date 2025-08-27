from apiflask import APIFlask, HTTPTokenAuth
from flask import send_from_directory
import threading
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy

from blueprints.groups import groups_b
from blueprints.usuario import usuario_b
from blueprints.tarea import tarea_b
from blueprints.herarquia import herarquia_b
from blueprints.actuacion import actuacion_b
from blueprints.expediente import expediente_b
from blueprints.nota import nota_b
from blueprints.label import label_b
from blueprints.alerta import alerta_b
from blueprints.endpoint import ep_b
from blueprints.dominio import dominio_b
from blueprints.organismo import organismo_b
from blueprints.full_sync import full_sync_b
# from blueprints.endpoint_json import ep_bj
from blueprints.fix_stuck_in_idle_connections import fix_b
from blueprints.URL import ep_url
from blueprints.ai_assistant import ai_assistant
from common.auditoria  import after_flush  # Importa el archivo que contiene el evento after_flush
from config.config import Config
from common.error_handling import register_error_handlers
from common.api_key import *
from common.chk_messagges import *
import sys
from models.alch_model import Base
from db.alchemy_db import db
from flask_caching import Cache
sys.setrecursionlimit(100)
import common.cache as cache_common
import threading
import redis
import common.exceptions as exceptions
from database_setup import DatabaseSetup


def is_redis_available(): 
    """One-liner Redis availability check"""
    try:
        print("testing redis connection")
        return redis.Redis(
            host=cache_common.redis_host,
            port=cache_common.redis_port,
            db=cache_common.redis_db,
            username=cache_common.redis_user if cache_common.redis_uses_password else None,
            password=cache_common.redis_password if cache_common.redis_uses_password else None,
            socket_connect_timeout=2
        ).ping()
    except redis.ConnectionError as e:
        print("Redis connection error:", e)
        return False

def create_app():
    # Optionally run database setup before app starts
    
        # If you have a run() or setup() method, call it here:
        
        # For now, just instantiate as a placeholder
    print("Creating app..")
    app = APIFlask(__name__)
    # app.config['CACHE_TYPE'] = 'RedisCache'  # Tipo de caché
    # cache_common.cache_enabled=Config.CACHE_ENABLED

    if cache_common.cache_enabled == False :
        print("Using NullCache, caching is disabled")
        app.config['CACHE_TYPE'] = 'NullCache'  # Tipo de caché
    else:
        if is_redis_available():
            print("Redis is available, using RedisCache")
            app.config['CACHE_TYPE'] = 'RedisCache'
            app.config['CACHE_REDIS_URL'] = "redis://"+cache_common.redis_user+":"+cache_common.redis_password+"@"+cache_common.redis_host+":"+str(cache_common.redis_port)+"/"+str(cache_common.redis_db) 
        # ... Redis config
        else:
            print("Redis is not available, using SimpleCache")
            app.config['CACHE_TYPE'] = 'SimpleCache'

    # Configurar Redis como backend de caché
    if(cache_common.redis_uses_password==True):
        print("Using Redis with password")
    #    app.config['CACHE_REDIS_USERNAME'] = cache_common.redis_user
     #   app.config['CACHE_REDIS_PASSWORD'] = cache_common.redis_password
    app.config['CACHE_KEY_PREFIX'] = cache_common.redis_prefix  

   

    app.config['CACHE_DEFAULT_TIMEOUT'] = cache_common.CACHE_TIMEOUT_MEDIUM  # Tiempo de caché predeterminado (en segundos)
                         
    
    app.config['JWT_PUBLIC_KEY'] = Config.JWT_PUBLIC_KEY
    app.config['JWT_ALGORITHM'] = Config.JWT_ALGORITHM
    app.config['JWT_DECODE_AUDIENCE'] = Config.JWT_DECODE_AUDIENCE
    app.config['JWT_IDENTITY_CLAIM'] = Config.JWT_IDENTITY_CLAIM
     # Initialize cache with app
    
    cache_common.cache.init_app(app)

    print(cache_common.cache)
    app.security_schemes = {  # equals to use config SECURITY_SCHEMES
        'ApiKeyAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-key'
        },
        'ApiKeySystemAuth':{
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-system'
        },
        'BearerAuth': {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT'
        },
        'UserRoleAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'x-user-role'
        }    
    }
    
    app.config['LOG_LEVEL'] = Config.LOG_LEVEL

    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{Config.POSGRESS_USER}:{Config.POSGRESS_PASSWORD}@{Config.POSGRESS_BASE}"
    app.config['SERVERS'] = Config.SERVERS
    app.config['DESCRIPTION'] = Config.DESCRIPTION
    app.config['MAX_ITEMS_PER_RESPONSE'] = Config.MAX_ITEMS_PER_RESPONSE
    app.config['SHOW_SQLALCHEMY_LOG_MESSAGES'] = Config.SHOW_SQLALCHEMY_LOG_MESSAGES
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
   
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_size': Config.SQLALCHEMY_POOL_SIZE,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800  # 30 minutos
    }
    #################RabbitMQ#################
    app.config['RABBITMQ_USER'] = Config.RABBITMQ_USER
    app.config['RABBITMQ_PASSWORD'] = Config.RABBITMQ_PASSWORD
    app.config['RABBITMQ_HOST'] = Config.RABBITMQ_HOST
    app.config['RABBITMQ_PORT'] = Config.RABBITMQ_PORT
    app.config['RABBITMQ_VHOST'] = Config.RABBITMQ_VHOST
    
    # Initialize the SQLAlchemy engine and session
    print("#####################")
    print("SQLAlchemy:",app.config['SQLALCHEMY_DATABASE_URI'])
    print("######################")
      # Create tables based on the models defined in Base
    db.init_app(app)
    
    with app.app_context():
        #db.create_all()
        if Config.RUN_DB_CREATION=='1':
            Base.metadata.create_all(db.engine, checkfirst=True)
   

    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"], "allow_headers": ["Content-Type", "authorization", "Authorization" , "X-Requested-With", "Accept", "Access-Control-Allow-Methods", "Access-Control-Allow-Origin", "x-api-key", "x-api-system", "x-user-role"]}})
    
    @app.route('/docs_sphinx/<path:filename>')
    def serve_sphinx_docs(filename):
        return send_from_directory('_build/html', filename)

    @app.route('/docs_sphinx/')
    def index():
        return send_from_directory('_build/html', 'index.html')
    
    app.register_blueprint(groups_b)
    app.register_blueprint(herarquia_b)
    app.register_blueprint(usuario_b)
    app.register_blueprint(tarea_b)
    app.register_blueprint(actuacion_b)
    app.register_blueprint(expediente_b)
    app.register_blueprint(nota_b)
    app.register_blueprint(label_b)
    app.register_blueprint(alerta_b)
    app.register_blueprint(ai_assistant)
    app.register_blueprint(ep_b)
    app.register_blueprint(ep_url)
    app.register_blueprint(dominio_b)
    app.register_blueprint(organismo_b)
    app.register_blueprint(full_sync_b)

    # Kubernetes liveness probe
    @app.route('/livez')
    def livez():
        return {'status': 'live'}, 200

    # Kubernetes readiness probe
    @app.route('/readyz')
    def readyz():
        try:
            db.session.execute('SELECT 1')
            return {'status': 'ready'}, 200
        except Exception as e:
            return {'status': 'unavailable', 'error': str(e)}, 503

  
    ###Api Key
    print("#####################")
    print("Iniciando servidor...")
    print("#####################\n")
    fresh_api_key=generate_api_key()
    ##Genera el prefijo
    prefix = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
    full_fresh_api_key =f"{prefix}-{fresh_api_key}"
    print("INSTRUCTIONS:")
    print("1. COPIAR API KEY GENERADO (SOLO SE VERA 1 VEZ)")
    hashed_fresh_api_key = hash_api_key(fresh_api_key)
    
    print(fresh_api_key+"- Full api-key: "+full_fresh_api_key)
    print("2. GUARDAR API KEY EN UN LUGAR SEGURO Y COMPARTIR A CLIENTE EXTERNO")
    print("3. SI SE PIERDE API KEY, GENERAR UNA NUEVA")
    print("4. AGREGAR NUEVA LINEA EN EL ARCHIVO DE CONFIGURACION DE API KEYS USANDO EL HASH DE LA API KEY, NO GUARDAR LA API KEY ORIGINAL! (api_keys.json)")
    hashed_fresh_api_key = base64.b64encode(hash_api_key(fresh_api_key)).decode('utf-8')
    full_hashed_fresh_api_key =f"{prefix}-{hashed_fresh_api_key}"
    print(hashed_fresh_api_key+"- Full hashed apy key: "+full_hashed_fresh_api_key)
    print("5. SI SE DESEA VERIFICAR LA API KEY, USAR LA FUNCION verify_api_key() pasando 3 paramentros, el hash de la api key, la api key(que viene del request) y el nombre de la aplicacion") 

    # Register custom error handlers
    exceptions.register_error_handlers(app)
    
    ############### CODIGO PARA LANZAR THREADS ################
    if uwsgi.worker_id() == 1: #if id is 1 then this thread should run. disabled for now with any long number
        thread = threading.Thread(target=chk_messagges, args=(app, db.session))
        thread.daemon = True
        thread.start()
        print("Hilo de recepción de mensajes iniciado.") 
        

    return app

app = create_app()
application = app 

if __name__ == "__main__":
   
    with app.app_context():
        print("RUN_DB_SETUP: ", Config.RUN_DB_SETUP)
        print("HARDCODING RUN_DB_SETUP to true")
       
        if Config.RUN_DB_SETUP=='1':
            print("******************************************")
            print("Running DatabaseSetup before app starts... __name__ == __main__")
            print("******************************************")
            setup = DatabaseSetup()
            setup.run()
    app.run()
else:
    print("going to run the app in else block")
    
    with app.app_context():
        print("RUN_DB_SETUP: ", Config.RUN_DB_SETUP)
        print("HARDCODING RUN_DB_SETUP to true")
     
        if Config.RUN_DB_SETUP=='1':
            print("******************************************")
            print("Running DatabaseSetup before app starts... Else block")
            print("******************************************")
            setup = DatabaseSetup()
            setup.run()
   
