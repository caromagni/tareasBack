import pika
import json
import os
from db.alchemy_db import db
from flask import g
import common.utils as utils
import traceback
import common.sync  as sync
import common.logger_config as logger_config

queue_name = os.environ.get('RABBITMQ_QUEUE_NAME')

def check_updates_new( rabbit_message: dict):
        
        entity = rabbit_message.get('entity_type').lower()
        action = rabbit_message.get('action')
        entity_id = rabbit_message.get('entity_id')
        empty_stuff = rabbit_message.get('empty_stuff')
        url = rabbit_message.get('url').lower()
        
        if not entity:
            logger_config.logger.info("No se ha especificado una entidad.")
            return
        if not action:
            logger_config.logger.info("No se ha especificado una acción.")
            return
        if not entity_id:
            logger_config.logger.info("No se ha especificado un ID de entidad.")
            return
        if not url:
            logger_config.logger.info("No se ha especificado una URL.")
            return
        print("##################################################")
        logger_config.logger.info(f"entity: {entity}")
        logger_config.logger.info("Before query to Parametros")
   

        if action in ["POST", "PUT"]:
            usher_apikey = os.environ.get('USHER_API_KEY')
            system_apikey = os.environ.get('SYSTEM_NAME')
            headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
            params = {"usuario_consulta": "csolanilla@mail.jus.mendoza.gov.ar"}
            id_user = utils.get_username_id('pusher')
            g.id_user = id_user
            #print("id user: ", id_user)
            print("entity: ", entity)
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
                        res=sync.sync_organismo(entity_id, url, id_user)
                    case 'inhabilidad':
                        #ejecutar insert o update para inhabilidad
                        res=sync.sync_inhabilidad(entity_id, url, id_user)
                    case 'fuero':
                        print("ejecutar insert o update para fuero")
                        #ejecutar insert o update para fuero
                        res=sync.sync_fuero(entity_id, url, id_user)    
                    case 'subtipo_act_juzgado':
                        #ejecutar insert o update para subtipo_tarea
                        res=sync.sync_subtipo_tarea(entity_id, url, id_user)    
                    case _:
                       
                        logger_config.logger.info(f" {entity} is not subscribed")
            
            except Exception as e:
                print(traceback.format_exc())
                #print("Error en check_updates:", e)
                logger_config.logger.info(f"Error en check_updates: {e}")                         

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
                self.channel.queue_declare(queue=queue_name, durable=True, passive=True)
                logger_config.logger.info("RabbitMQ conectado.")
                return
            except pika.exceptions.ChannelClosedByBroker as e:
                if e.reply_code == 404:
                    #el canal se cierra cuando passive=True
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(queue=queue_name, durable=True)
                else:
                    raise

    def callback(self, ch, method, properties, body):
        try:
            logger_config.logger.info(f"Mensaje procesado: {body.decode('utf-8')}")
            self.objeto = json.loads(body.decode('utf-8'))
            #with current_app.app_context():
            #    self.process_message(db.session)
          
            print(f" [x] Received {body}")

            #ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmamos que se procesó correctamente
            message = json.loads(body.decode('utf-8'))
            check_updates_new(message)
            ch.basic_ack(delivery_tag=method.delivery_tag) # consume message
 

        except Exception as e:
            logger_config.logger.error(f"Error procesando el mensaje: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            #reintentar o descartar el mensaje (requeue=False)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Rechazamos el mensaje y lo reencolamos
            
    # def process_message(self, session):
    #     if not self.objeto:
    #         print("No se recibió un objeto válido.")
    #         return

    #     entity = self.objeto.get('entity_type', '').lower()
    #     action = self.objeto.get('action', '')
    #     entity_id = self.objeto.get('entity_id', '')
    #     url = self.objeto.get('url', '')

        #check_updates(session, entity, action, entity_id, url)
        
        #check_updates_new(session, entity, action, entity_id, url)


    def start_consuming(self):
        if not self.channel:
            logger_config.logger.error("No se puede consumir mensajes sin conexión.")
            raise Exception("No se puede consumir mensajes sin conexión.")

        self.channel.basic_consume(queue=queue_name, 
                                   auto_ack=False, 
                                   on_message_callback=self.callback
                )
        logger_config.logger.info("[*] Waiting for messages. To exit press CTRL+C")
        try:
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger_config.logger.info("Consumo de mensajes detenido manualmente.")
            raise Exception("Consumo de mensajes detenido manualmente.")
       
    

