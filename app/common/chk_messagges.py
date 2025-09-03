from time import sleep
import uwsgi
from common.rabbitmq_utils import RabbitMQHandler
from db.alchemy_db import db
import time
import pika
# Consumir mensajes de la cola
#def chk_messagges(app, session_factory):
def chk_messagges(app, session):    
    tiempo=10
    handler = RabbitMQHandler()
    handler.connect()
    while True:
        if handler.channel:
            with app.app_context():
                print("---- RUNNING CHECK MESSAGES ----")
                try:
                    handler.start_consuming()
                    sleep(tiempo)
                except (pika.exceptions.AMQPHeartbeatTimeout, pika.exceptions.AMQPConnectorStackTimeout) as e:
                    print(f"Connection error: {e}")
                    time.sleep(5)
                    handler.connect()
                except Exception as e:
                    print("Error en chk_messagges:", e)
                    time.sleep(5)
                    handler.connect()
              
            
