from time import sleep
import uwsgi
from common.rabbitmq_utils import RabbitMQHandler
from alchemy_db import db

# Consumir mensajes de la cola
#def chk_messagges(app, session_factory):
def chk_messagges(app, session):    
    tiempo=10
    handler = RabbitMQHandler()
    handler.connect()
    while True:
        if handler.channel:
            with app.app_context():
                session = db.session()
                print("---- RUNNING CHECK MESSAGES ----")
                try:
                    handler.start_consuming()
                    sleep(tiempo)
                except Exception as e:
                    print("Error en chk_messagges:", e)
                    #session.rollback()
              
            
