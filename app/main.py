
from apiflask import APIFlask, HTTPTokenAuth
from flask import send_from_directory
import threading
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import DeclarativeBase

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker, scoped_session

from blueprints.groups import groups_b
from blueprints.usuario import usuario_b
from blueprints.tarea import tarea_b
from blueprints.herarquia import herarquia_b
from blueprints.actuacion import actuacion_b
from blueprints.expediente import expediente_b
from blueprints.nota import nota_b
from blueprints.label import label_b
from blueprints.fix_stuck_in_idle_connections import fix_b
from blueprints.ai_assistant import ai_assistant
from models.alch_model import Base
from common.auditoria  import after_flush  # Importa el archivo que contiene el evento after_flush
from config import Config
from common.error_handling import register_error_handlers
from common.api_key import *
from common.chk_messagges import *
import sys
from models.alch_model import Base
from alchemy_db import db
from flask_caching import Cache
sys.setrecursionlimit(100)
from cache import cache  # Import the shared cache instance
import threading

def create_app():

    print("Creating app..")
    app = APIFlask(__name__)
    app.config['CACHE_TYPE'] = 'SimpleCache'  # Ensure cache type is set
    app.config['CACHE_DEFAULT_TIMEOUT'] = 500  # Optional default timeout
#      ___ __  __ ____  _     _____ __  __ _____ _   _ _____  _    ____     
# |_ _|  \/  |  _ \| |   | ____|  \/  | ____| \ | |_   _|/ \  |  _ \    
#  | || |\/| | |_) | |   |  _| | |\/| |  _| |  \| | | | / _ \ | |_) |   
#  | || |  | |  __/| |___| |___| |  | | |___| |\  | | |/ ___ \|  _ <    
# |___|_|  |_|_| __|_____|_____|_|  |_|_____|_| \_| |_/_/   \_\_| \_\   
#  / ___|  / \  / ___| | | | ____|  / ___| |   / _ \| __ )  / \  | |    
# | |     / _ \| |   | |_| |  _|   | |  _| |  | | | |  _ \ / _ \ | |    
# | |___ / ___ \ |___|  _  | |___  | |_| | |__| |_| | |_) / ___ \| |___ 
#  \____/_/ __\_\____|_| |_|_____|  \____|_____\___/|____/_/   \_\_____|
# |  _ \_ _/ ___|  / \  | __ )| |   | ____|                             
# | | | | |\___ \ / _ \ |  _ \| |   |  _|                               
# | |_| | | ___) / ___ \| |_) | |___| |___                              
# |____/___|____/_/   \_\____/|_____|_____|                             
    app.config['CACHE_ENABLED'] = True  # Global toggle TRAER ESTO DESDE EL CONFIGS INICIAL
    app.config['JWT_PUBLIC_KEY'] = Config.JWT_PUBLIC_KEY
    app.config['JWT_ALGORITHM'] = Config.JWT_ALGORITHM
    app.config['JWT_DECODE_AUDIENCE'] = Config.JWT_DECODE_AUDIENCE
    app.config['JWT_IDENTITY_CLAIM'] = Config.JWT_IDENTITY_CLAIM
     # Initialize cache with app
    cache.init_app(app)
    print("CACHE MODULE INITIALIZED")
    print(cache)
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
        }
    }
   
    app.config['DEBUG'] = True
   
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{Config.POSGRESS_USER}:{Config.POSGRESS_PASSWORD}@{Config.POSGRESS_BASE}"
    app.config['SERVERS'] = Config.SERVERS
    app.config['DESCRIPTION'] = Config.DESCRIPTION
    app.config['MAX_ITEMS_PER_RESPONSE'] = Config.MAX_ITEMS_PER_RESPONSE
    app.config['SHOW_SQLALCHEMY_LOG_MESSAGES'] = Config.SHOW_SQLALCHEMY_LOG_MESSAGES
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

    #################RabbitMQ#################
    app.config['RABBITMQ_USER'] = Config.RABBITMQ_USER
    app.config['RABBITMQ_PASSWORD'] = Config.RABBITMQ_PASSWORD
    app.config['RABBITMQ_HOST'] = Config.RABBITMQ_HOST
    app.config['RABBITMQ_PORT'] = Config.RABBITMQ_PORT
    app.config['RABBITMQ_VHOST'] = Config.RABBITMQ_VHOST
    
    # Initialize the SQLAlchemy engine and session
   

    db.init_app(app)
   
   
    #engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False, pool_pre_ping=True)
    #Base.metadata.create_all(engine)
    #Session = scoped_session(sessionmaker(bind=engine))
    
    # Attach the session to the app instance
    #app.session = Session

    # Enable CORS
    #CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"], "allow_headers": "*"}})

    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"], "allow_headers": ["Content-Type", "authorization", "Authorization" , "X-Requested-With", "Accept", "Access-Control-Allow-Methods", "Access-Control-Allow-Origin"]}})
    #CORS(app)
    
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
    #app.register_blueprint(fix_b)
    app.register_blueprint(actuacion_b)
    app.register_blueprint(expediente_b)
    app.register_blueprint(nota_b)
    app.register_blueprint(label_b)
    app.register_blueprint(ai_assistant)

    from flask import request, make_response

   # Alternatively, for more granular control
    # @app.after_request
    # def add_cors_headers(response):
    #     response.headers['Access-Control-Allow-Credentials'] = 'true'
    #     response.headers['Vary'] = 'Origin'
    #     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:2500'
    #     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    #     response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    #     return response

# # Handle OPTIONS preflight request explicitly
#     @app.route("/<path:dummy>", methods=["OPTIONS"])
#     def options_handler(dummy):
#         # Ensure you've imported make_response and request
#         response = make_response()
#         allowed_origins = ["http://localhost:2500", "http://localhost:3000"]
#         request_origin = request.headers.get("Origin")

#         if request_origin in allowed_origins:
#             response.headers["Access-Control-Allow-Origin"] = request_origin
        
#         # Add 'Access-Control-Allow-Credentials' if using cookies/authentication
#         response.headers["Access-Control-Allow-Credentials"] = "true"

#         response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
#         response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
#         response.headers["Access-Control-Expose-Headers"] = "Content-Range, X-Content-Range"
        
#         return response

    
    
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
    register_error_handlers(app)
    
    ############### CODIGO PARA LANZAR THREADS ################
    """ if uwsgi.worker_id() == 1:
        thread = threading.Thread(target=chk_messagges, args=(app, db.session))
        thread.daemon = True
        thread.start()
        print("Hilo de recepción de mensajes iniciado.") """
        

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
else:
    app = create_app()
   
    application = app
