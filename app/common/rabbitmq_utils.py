import pika
import json
import os
from flask import current_app
from alchemy_db import db
from models.alch_model import Parametros, Usuario, TipoTarea, SubtipoTarea, Organismo, Inhabilidad
import requests
import uuid
from sqlalchemy import text
from datetime import datetime
from common.utils import verifica_username

def generar_update(entity, campos, valid_attributes, db_session=None, sqlalchemy_obj=None):
    if entity in ['tipo_act_juzgado', 'tipo_act_parte']:
        if not sqlalchemy_obj or not db_session:
            raise ValueError("Se necesita el objeto SQLAlchemy y la sesión para esta entidad especial.")
        
        print("Registro encontrado en", entity, ", actualizando... ID:", valid_attributes.get('id'))

        for key, value in valid_attributes.items():
            if key == 'id':
                sqlalchemy_obj.id_ext = value
            elif key == 'descripcion':
                sqlalchemy_obj.nombre = value
            elif key == 'descripcion_corta':
                sqlalchemy_obj.codigo_humano = value
            elif key == 'habilitado':
                sqlalchemy_obj.eliminado = not value
            else:
                setattr(sqlalchemy_obj, key, value)

        sqlalchemy_obj.fecha_actualizacion = datetime.now()
        db_session.commit()

        return None, None  # No hay query ni valores, ya se ejecutó el commit
    
    else:
        return construct_update_query(entity, campos, valid_attributes)
    
def generar_insert(entity, campos, valid_attributes, db_session=None, sqlalchemy_model_class=None):
    if entity in ['tipo_act_juzgado', 'tipo_act_parte']:
        if not sqlalchemy_model_class or not db_session:
            raise ValueError("Se necesita el modelo SQLAlchemy y la sesión para esta entidad especial.")
        
        nuevo_obj = sqlalchemy_model_class()

        for key, value in valid_attributes.items():
            if key == 'id':
                nuevo_obj.id_ext = value
            elif key == 'descripcion':
                nuevo_obj.nombre = value
            elif key == 'descripcion_corta':
                nuevo_obj.codigo_humano = value
            elif key == 'habilitado':
                nuevo_obj.eliminado = not value
            else:
                setattr(nuevo_obj, key, value)

        nuevo_obj.fecha_actualizacion = datetime.now()
        db_session.add(nuevo_obj)
        db_session.commit()

        return None, None  # No hay query ni valores, ya se insertó

    else:
        return construct_insert_query(entity, campos, valid_attributes)
    

def construct_update_query(entity, campos, valid_attributes):
    if entity == 'usuario':
        original_id = valid_attributes.get('id')
        valid_attributes['id_persona_ext'] = original_id  # original va en id_pers_ext
    # Filter campos to only include fields present in valid_attributes
    update_fields = [field for field in campos if field in valid_attributes and field != 'id']
    
    # Construct the SET clause
    set_clause = ', '.join([f"{field} = :{field}" for field in update_fields])
    query = f'UPDATE tareas.{entity} SET {set_clause} WHERE id = :id'
    values = {field: valid_attributes[field] for field in update_fields}
    values['id'] = valid_attributes['id']
    return query, values

def construct_insert_query(entity, campos, valid_attributes):
    if entity == 'usuario':
        new_id = str(uuid.uuid4())  # nuevo UUID
        original_id = valid_attributes.get('id')

        valid_attributes['id'] = new_id  # nuevo UUID como id
        valid_attributes['id_persona_ext'] = original_id  # original va en id_pers_ext


    # Filter campos to only include fields present in valid_attributes
    insert_fields = [field for field in campos if field in valid_attributes]
    
    # Construct the column names part of the query
    columns = ', '.join(insert_fields)
    
    # Construct the placeholders for values
    placeholders = ', '.join([f":{field}" for field in insert_fields])
    
    # Arma la consulta completa.
    query = f'INSERT INTO tareas.{entity} ({columns}) VALUES ({placeholders})'
    
    # Crea el diccionario de valores en el mismo orden.
    values = {field: valid_attributes[field] for field in insert_fields}
    
    return query, values

def check_updates(session, entity='', action='', entity_id=None, url=''):
        print("Checking updates...")
        print(datetime.now())

        res = db.session.query(Parametros).filter(Parametros.table == entity).first()
        if not res:
            print(f"No se encontró la tabla {entity} en los parámetros.")
            #raise Exception(f"No se encontró la tabla {entity} en los parámetros para actualizar.")
            return

        campos = res.columns

        print("campos: ", campos)
        if action in ["POST", "PUT"]:
            print("action: ", action)
            #usher_apikey = os.environ.get('USHER_API_KEY', 'default_apikey')
            usher_apikey = os.environ.get('USHER_API_KEY')
            #system_apikey = os.environ.get('SYSTEM_API_KEY', 'default_system')
            system_apikey = os.environ.get('SYSTEM_NAME')
            print("usher_apikey: ", usher_apikey)
            print("system_apikey: ", system_apikey)
            headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
            params = {"usuario_consulta": "csolanilla@mail.jus.mendoza.gov.ar"}
            id_user = verifica_username('pusher')
            print("id user: ", id_user)
            try:
                response = requests.get(url, params=params, headers=headers).json()
                attributes_list = response['data']
                print("#"*50)
                attributes = next((attr for attr in attributes_list if attr.get('id') == entity_id), None)

                if not attributes:
                    print(f"No se encontró un registro en 'data' con id: {entity_id}")
                    return

                valid_attributes = {key: value for key, value in attributes.items() if key in campos}
                """ valid_attributes = [{key: value for key, value in attributes.items() if key in campos}
                                    for attributes in attributes_list] """
                
                if 'fecha_actualizacion' in valid_attributes:
                   #if not valid_attributes['fecha_actualizacion']:
                        print(datetime.now())
                        valid_attributes['fecha_actualizacion'] = datetime.now()

                if 'id_user_actualizacion' in valid_attributes:
                    if not valid_attributes['id_user_actualizacion']:
                        valid_attributes['id_user_actualizacion'] = id_user
                    else:
                        valid_attributes['id_user_actualizacion'] = verifica_username(valid_attributes['id_user_actualizacion'])      

                print("valid_attributes: ", valid_attributes)
                print("entity_id: ", entity_id)
                if entity=='tipo_act_juzgado' or entity=='tipo_act_parte':
                    query = db.session.query(TipoTarea).filter(TipoTarea.id_ext == entity_id).first()
                if entity == 'usuario':
                    query = db.session.query(Usuario).filter(Usuario.id_persona_ext == entity_id).first()
                    if query is None:
                        query = db.session.query(Usuario).filter(Usuario.username == valid_attributes['email']).first()
                if entity == 'organismo':
                    query = db.session.query(Organismo).filter(Organismo.id == entity_id).first()
                if entity == 'inhabilidad':
                    query = db.session.query(Inhabilidad).filter(Inhabilidad.id == entity_id).first()    
                
                if query is not None:
                    #Updates

                    query_final, values = generar_update(
                                entity,
                                campos,
                                valid_attributes,
                                db_session=db.session,
                                sqlalchemy_obj=query  # el objeto ya cargado de la BD
                            )
                    
                else:
                    #Inserts
                    #Agregar entity=='tipo_act_juzgado' or entity=='tipo_act_parte'
                    query_final, values = generar_insert(
                                entity,
                                campos,
                                valid_attributes,
                                db_session=db.session,
                                sqlalchemy_model_class= TipoTarea  # el objeto ya cargado de la BD
                            )

                print("#"*50)
                print("query_final: ", query_final)  
                print("values: ", values) 
                if query_final and values:
                        db.session.execute(text(query_final), values)
                        db.session.commit()
                        print("Actualizaciones realizadas.")

            except Exception as e:
                print("Error en check_updates:", e)


class RabbitMQHandler:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.objeto = None

    def connect(self):
        rabbitmq_params = {
            'user': os.environ.get('RABBITMQ_USER', 'guest'),
            'password': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
            'host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'port': int(os.environ.get('RABBITMQ_PORT', 5672)),
            'vhost': os.environ.get('RABBITMQ_VHOST', '/')
        }

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
            self.channel.queue_declare(queue='expte_params', durable=True, passive=True)
            print("RabbitMQ conectado.")
        except Exception as e:
            print("Error conectando a RabbitMQ:", e)
            self.connection, self.channel = None, None


    def callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")
        self.objeto = json.loads(body.decode('utf-8'))
        with current_app.app_context():
            self.process_message(db.session)

    def process_message(self, session):
        if not self.objeto:
            print("No se recibió un objeto válido.")
            return

        entity = self.objeto.get('entity_type', '').lower()
        action = self.objeto.get('action', '')
        entity_id = self.objeto.get('entity_id', '')
        url = self.objeto.get('url', '')

        check_updates(session, entity, action, entity_id, url)


    def start_consuming(self):
        if not self.channel:
            print("No se puede consumir mensajes sin conexión.")
            raise Exception("No se puede consumir mensajes sin conexión.")

        self.channel.basic_consume(queue='expte_params', auto_ack=True, on_message_callback=self.callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Consumo de mensajes detenido manualmente.")
            raise Exception("Consumo de mensajes detenido manualmente.")
       
    

