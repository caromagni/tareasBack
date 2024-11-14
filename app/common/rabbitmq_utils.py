import pika
import json
from flask import current_app

# Establecer la conexión con el servidor RabbitMQ

def conectar_rabbitmq():
    global connection
    global channel
    #http://192.168.70.27
    #192.168.68.201
    #connection_parameter=pika.ConnectionParameters(host='192.168.70.27', port=15672, virtual_host='/', credentials=pika.PlainCredentials('tareas', '123321'))
    connection_parameter=pika.ConnectionParameters(host='192.168.70.27', port=5672, virtual_host='/', credentials=pika.PlainCredentials('tareas', 'tareas'))
    #connection_parameter=pika.ConnectionParameters(host='192.168.68.201', port=5672, virtual_host='/', credentials=pika.PlainCredentials('tareas', '123321'))
    connection = pika.BlockingConnection(connection_parameter)
    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola en la que quieres enviar los mensajes
    channel.queue_declare(queue='txin', durable=True)
    channel.queue_declare(queue='txout', durable=True)     
    print("Conexión establecida con RabbitMQ - ", connection)
    print("Canal establecido con RabbitMQ - ", channel)
    return connection, channel 

def enviar_a_rabbitmq(msg):
    # Crear el mensaje que quieres enviar (en este caso, un diccionario JSON)
    mensaje = {
        "msg": msg
    }
    print("Mensaje a enviar: ", mensaje)
    conectar_rabbitmq()
    print ("Conexión: ", connection)
    # Convertir el mensaje a formato JSON
    mensaje_json = json.dumps(msg)

    # Publicar el mensaje en la cola
    channel.basic_publish(exchange='',
                          routing_key='txin',
                          body=mensaje_json)
    print(f" [x] Enviado a RabbitMQ: {mensaje_json}")

    # Cerrar la conexión con el servidor RabbitMQ
    connection.close()


def on_message_received(ch, method, properties, body):
    print(f" [x] Received {body}")
    # Convertir el mensaje JSON a un diccionario
    #return "Mensaje recibido"

    
# Consumir mensajes de la cola
def callback(ch, method, properties, body):
    mensaje = json.loads(body)
    ms =mensaje.get("msg")
    fecha = mensaje.get("fecha")
    print(f" [x] Received {body}")
    print(f" [x] Received {ms} - {fecha}")

def recibir_de_rabbitmq():
    conectar_rabbitmq()
    channel.basic_consume(queue='txin',
                    auto_ack=True,
                    on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    
