from apiflask import APIFlask
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
from .blueprints.fix_stuck_in_idle_connections import fix_b
from .models.alch_model import Base
from .common.auditoria  import after_flush  # Importa el archivo que contiene el evento after_flush
from .config import Config

def create_app():

    print("Creating app..")
    app = APIFlask(__name__)
    
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{Config.POSGRESS_USER}:{Config.POSGRESS_PASSWORD}@psql.beta.hwc.pjm.gob.ar:5432/tareas"
    app.config['SERVERS'] = Config.SERVERS
    app.config['DESCRIPTION'] = Config.DESCRIPTION

    # Initialize the SQLAlchemy engine and session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Attach the session to the app instance
    app.session = Session

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Access-Control-Allow-Methods", "Access-Control-Allow-Origin"]}})


    
    app.register_blueprint(groups_b)
    app.register_blueprint(herarquia_b)
    app.register_blueprint(usuario_b)
    app.register_blueprint(tarea_b)
    app.register_blueprint(fix_b)
    app.register_blueprint(actuacion_b)
    app.register_blueprint(expediente_b)
    # Register custom error handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
