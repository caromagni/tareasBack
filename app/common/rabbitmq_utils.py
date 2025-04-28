import pika
import json
import time
import os
from flask import current_app
from alchemy_db import db
from models.alch_model import Parametros, Usuario, TipoTarea, SubtipoTarea, Organismo, Inhabilidad
import requests
import uuid
from sqlalchemy import text
from datetime import datetime
from common.utils import verifica_username
from flask import g
import common.sync  as sync



def check_updates_new(session, entity='', action='', entity_id=None, url=''):
        print("Checking updates...")
        print(datetime.now())
        print("entity a buscar: ", entity)
        res = db.session.query(Parametros).filter(Parametros.table == entity).first()
        if not res:
            print(f"No se encontró la tabla {entity} en los parámetros.")
            return

        campos = res.columns

        print("campos: ", campos)
        if action in ["POST", "PUT"]:
            print("action: ", action)
            usher_apikey = os.environ.get('USHER_API_KEY')
            system_apikey = os.environ.get('SYSTEM_NAME')
            headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
            params = {"usuario_consulta": "csolanilla@mail.jus.mendoza.gov.ar"}
            id_user = verifica_username('pusher')
            g.id_user = id_user
            print("id user: ", id_user)
            try:
                match entity:
                    case 'tipo_act_juzgado':
                        #ejecutar insert o update para tipo_tarea
                        res=sync.sync_tipo_tarea(entity_id, url, id_user)
                    case 'tipo_act_parte':
                        #ejecutar insert o update para tipo_tarea
                        res=sync.sync_tipo_tarea(entity_id, url, id_user)
                    case 'usuario':
                        #ejecutar insert o update para usuario
                        res=sync.sync_usuario(entity_id, url, id_user)
                    case 'organismo':
                        #ejecutar insert o update para organismo
                        res=sync.sync_cu(entity_id, url, id_user)
                    case 'inhabilidad':
                        #ejecutar insert o update para inhabilidad
                        res=sync.sync_cu(entity_id, url, id_user)
                    case _:
                        print(f"La entidad {entity} no está soportada para sincronización.")
            
            except Exception as e:
                     print("Error en check_updates:", e)                         

class RabbitMQHandler:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.objeto = None
        self.max_retries = 5

    def connect(self):
        rabbitmq_params = {
            'user': os.environ.get('RABBITMQ_USER', 'guest'),
            'password': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
            'host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'port': int(os.environ.get('RABBITMQ_PORT', 5672)),
            'vhost': os.environ.get('RABBITMQ_VHOST', '/')
        }
        retry_count = 0
        while retry_count < self.max_retries:

            try:
                connection_params = pika.ConnectionParameters(
                    host=rabbitmq_params['host'],
                    port=rabbitmq_params['port'],
                    virtual_host=rabbitmq_params['vhost'],
                    credentials=pika.PlainCredentials(
                        rabbitmq_params['user'], rabbitmq_params['password']
                    )
                )
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='tareas_params', durable=True, passive=True)
                print("RabbitMQ conectado.")
                return
            except pika.exceptions.ChannelClosedByBroker as e:
                if e.reply_code == 404:
                    #el canal se cierra cuando passive=True
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(queue='tareas_params', durable=True)
                else:
                    raise
            """      
            except Exception as e:
                retry_count += 1
                print(f" Error conectando a RabbitMQ (intento {retry_count}): {e}")
                print(f" Reintentando en 10 segundos...")
                time.sleep(10) """


    def callback(self, ch, method, properties, body):
        #ch.basic_ack(delivery_tag=method.delivery_tag)
        #print(f" [x] Received {body}")
        try:
            self.objeto = json.loads(body.decode('utf-8'))
            with current_app.app_context():
                self.process_message(db.session)
           
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmamos que se procesó correctamente
            print(f" [x] Received {body}")
        except Exception as e:
            print("Error procesando el mensaje:", e)
            #ch.basic_ack(delivery_tag=method.delivery_tag)
            #reintentar o descartar el mensaje (requeue=False)
            #ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Rechazamos el mensaje y lo reencolamos
            
            

    def process_message(self, session):
        if not self.objeto:
            print("No se recibió un objeto válido.")
            return

        entity = self.objeto.get('entity_type', '').lower()
        action = self.objeto.get('action', '')
        entity_id = self.objeto.get('entity_id', '')
        url = self.objeto.get('url', '')

        #check_updates(session, entity, action, entity_id, url)
        check_updates_new(session, entity, action, entity_id, url)


    def start_consuming(self):
        if not self.channel:
            print("No se puede consumir mensajes sin conexión.")
            raise Exception("No se puede consumir mensajes sin conexión.")

        self.channel.basic_consume(queue='tareas_params', 
                                   auto_ack=False, 
                                   on_message_callback=self.callback
                )
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("Consumo de mensajes detenido manualmente.")
            raise Exception("Consumo de mensajes detenido manualmente.")
       
    

