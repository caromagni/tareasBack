from apiflask import APIFlask, HTTPTokenAuth
from flask import send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.common.error_handling import register_error_handlers
from .blueprints.groups import groups_b
from .blueprints.usuario import usuario_b
from .blueprints.tarea import tarea_b
from .blueprints.herarquia import herarquia_b
from .blueprints.actuacion import actuacion_b
from .blueprints.expediente import expediente_b
from .blueprints.nota import nota_b
from .blueprints.fix_stuck_in_idle_connections import fix_b
from .models.alch_model import Base
from .common.auditoria  import after_flush  # Importa el archivo que contiene el evento after_flush
from .config import Config
from app.api_key import *


def create_app():

    print("Creating app..")
    app = APIFlask(__name__)
    
    app.config['JWT_PUBLIC_KEY'] = Config.JWT_PUBLIC_KEY
    app.config['JWT_ALGORITHM'] = Config.JWT_ALGORITHM
    app.config['JWT_DECODE_AUDIENCE'] = Config.JWT_DECODE_AUDIENCE
    app.config['JWT_IDENTITY_CLAIM'] = Config.JWT_IDENTITY_CLAIM


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

    # Initialize the SQLAlchemy engine and session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Attach the session to the app instance
    app.session = Session

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Access-Control-Allow-Methods", "Access-Control-Allow-Origin"]}})


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
    app.register_blueprint(fix_b)
    app.register_blueprint(actuacion_b)
    app.register_blueprint(expediente_b)
    app.register_blueprint(nota_b)

    
    ###Api Key
    print("#####################")
    print("Iniciando servidor...")
    print("#####################\n")
    fresh_api_key=generate_api_key()
    print("INSTRUCTIONS:")
    print("1. COPIAR API KEY GENERADO (SOLO SE VERA 1 VEZ)")
    hashed_fresh_api_key = hash_api_key(fresh_api_key)
    print(fresh_api_key)
    print("2. GUARDAR API KEY EN UN LUGAR SEGURO Y COMPARTIR A CLIENTE EXTERNO")
    print("3. SI SE PIERDE API KEY, GENERAR UNA NUEVA")
    print("4. AGREGAR NUEVA LINEA EN EL ARCHIVO DE CONFIGURACION DE API KEYS USANDO EL HASH DE LA API KEY, NO GUARDAR LA API KEY ORIGINAL! (api_keys.json)")
    hashed_fresh_api_key = base64.b64encode(hash_api_key(fresh_api_key)).decode('utf-8')
    print(hashed_fresh_api_key)
    print("5. SI SE DESEA VERIFICAR LA API KEY, USAR LA FUNCION verify_api_key() pasando 3 paramentros, el hash de la api key, la api key(que viene del request) y el nombre de la aplicacion") 

    # Register custom error handlers
    register_error_handlers(app)

    

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

