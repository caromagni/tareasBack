from apiflask import APIFlask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .blueprints.groups import groups_b
from .blueprints.usuario import usuario_b
from .alch_model import Base
from .config import Config
def create_app():

    print("Creating app..")
    app = APIFlask(__name__)
    
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+Config.POSGRESS_USER+":"+Config.POSGRESS_PASSWORD+"@psql.beta.hwc.pjm.gob.ar:5432/tareas"
    
    # Initialize the SQLAlchemy engine and session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Attach the session to the app instance

    @app.route("/")
    def base_url():
        return "<p>Hello, World!</p>"



    app.session = Session
    
    app.register_blueprint(groups_b)
    app.register_blueprint(usuario_b)

    with app.app_context():
       
        return app

if __name__ == '__main__':
    app = create_app()
    CORS(app, expose_headers=["x-suggested-filename"],resources={r"/*": {"origins":"http://doesnotwork.com","methods": ["GET", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"],"allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"]}})
        
    app.run()
