import requests
from models.alch_model import Usuario, TipoTarea, Inhabilidad, Organismo
from datetime import date, timedelta, datetime
from common.logger_config import logger
import uuid
from alchemy_db import db
import os

def sync_request(url, entity_id):
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta=os.environ.get('PUSHER_USUARIO_CONSULTA')
    url=url+'?id='+entity_id+'&usuario_consulta='+usuario_consulta
    r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
    
    resp=r.json()
    print("json roles:",resp)
    return resp

def sync_tipo_tarea(entity_id, url,id_user):

    resp= sync_request(url, entity_id)
    print("json roles:",resp)
    if resp and resp['data']['id'] is not None:
        #Buscar si existe el tipo de tarea en la base de datos
        query_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id_ext == resp['data']['id']).first()
        if query_tipo_tarea is None:
            #hago insert del tipo de tarea
            nuevo_tipo_tarea = TipoTarea(id=uuid.uuid4(),
                               id_ext=resp['data']['id'], 
                               nombre=resp['data']['descripcion'], 
                               codigo_humano=resp['data']['descripcion_corta'], 
                               eliminado=not(resp['data']['habilitado']),
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_tipo_tarea)
        else:
            #hago update del tipo de tarea
            query_tipo_tarea.nombre = resp['data']['descripcion']
            query_tipo_tarea.codigo_humano = resp['data']['descripcion_corta'] 
            query_tipo_tarea.eliminado = not(resp['data']['habilitado'])
            query_tipo_tarea.id_ext = resp['data']['id']
            query_tipo_tarea.fecha_actualizacion=datetime.now()
            query_tipo_tarea.id_user_actualizacion=id_user

        db.session.commit()
    return resp

def sync_usuario(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['username'] is not None:
        #Buscar el usuario en la base de datos
        query_usr = db.session.query(Usuario).filter(Usuario.username == resp['data']['username']).first()
        if query_usr is None:
            #hago insert del usuario
            nuevo_usuario = Usuario(id=uuid.uuid4(),
                               username=resp['data']['username'], 
                               email=resp['data']['email'], 
                               nombre=resp['data']['nombre'], 
                               apellido=resp['data']['apellido'], 
                               id_ext = resp['data']['id'],
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user,
                               eliminado=not(resp['data']['habilitado']),
                               dni =resp['data']['nro_documento'],
                               suspendido=False)

   
            db.session.add(nuevo_usuario)
        else:
            #hago update del usuario
            query_usr.username = resp['data']['username']
            query_usr.email = resp['data']['email']
            query_usr.nombre = resp['data']['nombre']
            query_usr.apellido = resp['data']['apellido']
            query_usr.fecha_actualizacion=datetime.now()
            query_usr.id_user_actualizacion=id_user
            query_usr.eliminado=not(resp['data']['habilitado'])
            query_usr.dni =resp['data']['nro_documento']
            query_usr.suspendido=False    
    
    db.session.commit()
    return resp

def sync_inhabilidad(entity_id, url,id_user):
 
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['id'] is not None:
        #Buscar si existe la inhabilidad en la base de datos
        query_inhabilidad = db.session.query(Inhabilidad).filter(Inhabilidad.id_ext == resp['data']['id']).first()
        if query_inhabilidad is None:
            #hago insert de la inhabilidad
            nuevo_inhabilidad = Inhabilidad(id=uuid.uuid4(),
                               id_ext=resp['data']['id'], 
                               fecha_desde=resp['data']['fecha_desde'], 
                               fecha_hasta=resp['data']['fecha_hasta'], 
                               id_organismo=resp['data']['id_organismo'],
                               id_juez=resp['data']['id_juez'],
                               tipo =resp['data']['tipo'],
                               descripcion=resp['data']['descripcion'],
                               habilitado=resp['data']['habilitado'],
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_inhabilidad)

        else:
            #hago update de la inhabilidad
            query_inhabilidad.fecha_desde = resp['data']['fecha_desde']
            query_inhabilidad.fecha_hasta = resp['data']['fecha_hasta']
            query_inhabilidad.id_organismo = resp['data']['id_organismo']
            query_inhabilidad.id_juez = resp['data']['id_juez']
            query_inhabilidad.tipo =resp['data']['tipo']
            query_inhabilidad.descripcion = resp['data']['descripcion']
            query_inhabilidad.habilitado = resp['data']['habilitado']
            query_inhabilidad.id_ext = resp['data']['id']
            query_inhabilidad.fecha_actualizacion=datetime.now()
            query_inhabilidad.id_user_actualizacion=id_user

        db.session.commit()
    return resp

def sync_organismo(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['id'] is not None:
        #Buscar si existe el organismo en la base de datos
        query_organismo = db.session.query(Organismo).filter(Organismo.id_ext == resp['data']['id']).first()
        if query_organismo is None:
            #hago insert del organismo
            nuevo_organismo = Organismo(id=uuid.uuid4(),
                               id_ext=resp['data']['id'], 
                               descripcion=resp['data']['descripcion'],
                               descripcion_corta=resp['data']['descripcion_corta'],
                               id_fuero=resp['data']['id_fuero'],
                               instancia=resp['data']['instancia'],
                               habilitado=resp['data']['habilitado'],
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_organismo)

        else:
            #hago update del organismo
            query_organismo.descricion = resp['data']['descripcion']
            query_organismo.descripcion_corta = resp['data']['descripcion_corta'] 
            query_organismo.id_fuero = resp['data']['id_fuero']
            query_organismo.instancia = resp['data']['instancia']
            query_organismo.habilitado = resp['data']['habilitado']
            query_organismo.id_ext = resp['data']['id']
            query_organismo.fecha_actualizacion=datetime.now()
            query_organismo.id_user_actualizacion=id_user

        db.session.commit()
    return resp

def sync_cu(entity_id, url,id_user):
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta=os.environ.get('PUSHER_USUARIO_CONSULTA')
    url=url+'?id='+entity_id+'&usuario_consulta='+usuario_consulta
    r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
    
    resp=r.json()
    print("json roles:",resp)    
    return resp

