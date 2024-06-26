from apiflask import APIFlask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
#from flask_jwt_extended import JWTManager
from app.common.error_handling import register_error_handlers
from .blueprints.groups import groups_b
from .blueprints.usuario import usuario_b
from .blueprints.tarea import tarea_b
from .models.alch_model import Base
from .config import Config

def create_app():

    print("Creating app..")
    app = APIFlask(__name__)
    CORS(app, expose_headers=["x-suggested-filename"])
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+Config.POSGRESS_USER+":"+Config.POSGRESS_PASSWORD+"@psql.beta.hwc.pjm.gob.ar:5432/tareas"
    app.config['SERVERS'] = Config.SERVERS
    app.config['DESCRIPTION'] = Config.DESCRIPTION

    # Initialize the SQLAlchemy engine and session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Attach the session to the app instance
    app.session = Session
    
    app.register_blueprint(groups_b)
    app.register_blueprint(usuario_b)
    app.register_blueprint(tarea_b)

    #jwt = JWTManager(app=app)
    # Registra manejadores de errores personalizados
    register_error_handlers(app)
    
    with app.app_context():
       
        return app

if __name__ == '__main__':
    app = create_app()
    app.run()
