import pika
import json
import os
from flask import current_app
from sqlalchemy import event
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.inspection import inspect
from datetime import datetime, date
from models.alch_model import Parametros, Usuario, TipoTarea, SubtipoTarea
import json
import uuid
from common.functions import get_user_ip
import requests

# Establecer la conexión con el servidor RabbitMQ
def conectar_rabbitmq1():
    global connection
    global channel
    
    rabbitmq_params = {
      #'user': current_app.config['RABBITMQ_USER'],
      'user': os.environ.get('RABBITMQ_USER'),
      'password': os.environ.get('RABBITMQ_PASSWORD'),
      'host': os.environ.get('RABBITMQ_HOST'),
      'port': int(os.environ.get('RABBITMQ_PORT', 5672)),
      'vhost': os.environ.get('RABBITMQ_VHOST')
    }

    try:
        connection_parameter=pika.ConnectionParameters(host=rabbitmq_params['host'],
                                                port=rabbitmq_params['port'],
                                                virtual_host=rabbitmq_params['vhost'],
                                                credentials=pika.PlainCredentials(rabbitmq_params['user'],  rabbitmq_params['password']))

        #connection_parameter=pika.ConnectionParameters(host='172.17.0.3', port=5672, virtual_host='/', credentials=pika.PlainCredentials('tareas', 'tareas'))
        connection = pika.BlockingConnection(connection_parameter)
        channel = connection.channel()

    # Declarar la cola en la que quieres enviar los mensajes
        channel.queue_declare(queue='expte_params', durable=True, passive=True)
    #channel.queue_declare(queue='txout', durable=True)     
        return connection, channel 
    except Exception as e:
        print("Error en conectar_rabbitmq1: ",e)
        return None, None

# Establecer la conexión con el servidor RabbitMQ
def conectar_rabbitmq():
    global connection
    global channel
    rabbitmq_params = {
      #'user': current_app.config['RABBITMQ_USER'],
      'user': os.environ.get('RABBITMQ_USER'),
      'password': os.environ.get('RABBITMQ_PASSWORD'),
      'host': os.environ.get('RABBITMQ_HOST'),
      'port': int(os.environ.get('RABBITMQ_PORT', 5672)),
      'vhost': os.environ.get('RABBITMQ_VHOST')
    }

    #credentials = pika.PlainCredentials(rabbitmq_params['user'], rabbitmq_params['password'])

    """ connection_parameter=pika.ConnectionParameters(host=rabbitmq_params['host'],
                                                port=rabbitmq_params['port'],
                                                virtual_host=rabbitmq_params['vhost'],
                                                credentials=pika.PlainCredentials(rabbitmq_params['user'],  rabbitmq_params['password']))
    connection = pika.BlockingConnection(connection_parameter) """
    #######################
    #172.17.0.2
    #host='192.168.68.201'
    connection_parameter=pika.ConnectionParameters(host='172.17.0.3', port=5672, virtual_host='/', credentials=pika.PlainCredentials('tareas', 'tareas'))
    connection = pika.BlockingConnection(connection_parameter)
    channel = connection.channel()

    # Declarar la cola en la que quieres enviar los mensajes
    channel.queue_declare(queue='expte_params', durable=True)
    #channel.queue_declare(queue='txout', durable=True)     
    print("Conexión establecida con RabbitMQ - ", connection)
    print("Canal establecido con RabbitMQ - ", channel)
    return connection, channel 
    
    
   
# Consumir mensajes de la cola
def callback(ch, method, properties, body):
    global objeto
    print(f" [x] Received {body}")
    objeto = json.loads(body.decode('utf-8'))
    


def recibir_de_rabbitmq():
    global objeto
    conectar_rabbitmq1()
    channel.basic_consume(queue='expte_params',
                    auto_ack=True,
                    on_message_callback=callback)
    entity = objeto['entity_type'].lower()
    action = objeto['action']
    entity_id = objeto['entity_id']
    url = objeto['url']
    print("entity: ", entity)
    print("action: ", action)
    print("entity_id: ", entity_id)
    print("url: ", url)
    check_updates(entity, action, entity_id, url)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def check_updates(entity='', action='', entity_id=None, url=''):
    session: scoped_session = current_app.session
    res = session.query(Parametros).filter(Parametros.table == entity).first()
    if res:
        campos = res.columns
        if action == "POST" or action == "PUT":
            # hago un request a la API de usher para obtener el objeto completo
            url = url + '?id=' + entity_id        
            
            # en lugar de token, utilizo api key
            usher_apikey = os.environ.get('USHER_API_KEY')
            headers = {'x-api-key': usher_apikey, 'x-api-system': os.environ.get('SYSTEM_NAME')}

            
            params = {
                    "usuario_consulta": "csolanilla@mail.jus.mendoza.gov.ar",
                }

            response = requests.get(url, params=params, headers=headers).json()
            
            attributes = response['data']

            # Filtrar solo los atributos que existen en las columnas de la entidad
            valid_attributes = {key: value for key, value in attributes.items() if key in campos}
            print("valid_attributes: ", valid_attributes)

            if entity == 'usuario':
                query = session.query(Usuario).filter(Usuario.id_persona_ext == entity_id).first()
                if query:
                    print("Usuario encontrado")
                    for key, value in valid_attributes.items():
                        setattr(query, key, value)
                    session.commit()
                    print("Actualizaciones realizadas")

            #elif entity == 'tipo_tarea':

    
    return "Actualizaciones realizadas"
    
