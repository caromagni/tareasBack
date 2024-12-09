import pika
import json
import os
from flask import current_app

# Establecer la conexión con el servidor RabbitMQ
def conectar_rabbitmq1():
    global connection
    global channel
    #'172.17.0.3'
    connection_parameter=pika.ConnectionParameters(host='172.17.0.3', port=5672, virtual_host='/', credentials=pika.PlainCredentials('tareas', 'tareas'))
    connection = pika.BlockingConnection(connection_parameter)
    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola en la que quieres enviar los mensajes
    channel.queue_declare(queue='expte_params', durable=True)
    #channel.queue_declare(queue='txout', durable=True)     
    return connection, channel 

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
      #'password': current_app.config['RABBITMQ_PASSWORD'],
      #'host': current_app.config['RABBITMQ_HOST'],
      #'port': int(current_app.config['RABBITMQ_PORT']),
      #'vhost': current_app.config['RABBITMQ_VHOST']
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
    
    

""" 
def on_message_received(ch, method, properties, body):
    print(f" [x] Received {body}")
    # Convertir el mensaje JSON a un diccionario
    #return "Mensaje recibido" """

    
# Consumir mensajes de la cola
def callback(ch, method, properties, body):
    #mensaje = json.loads(body)
    #objeto = json.loads(body.decode('utf-8'))
    """ entity = objeto['entity_type'].lower()
    action = objeto['action']
    entity_id = objeto['entity_id']
    url = objeto['url']
    
    ms =mensaje.get("msg")
    fecha = mensaje.get("fecha") """
    print(f" [x] Received {body}")

def recibir_de_rabbitmq():
    conectar_rabbitmq1()
    channel.basic_consume(queue='expte_params',
                    auto_ack=True,
                    on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    
