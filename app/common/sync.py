import requests
from models.alch_model import Usuario, TipoTarea, SubtipoTarea, Inhabilidad, Organismo, Grupo,  Dominio
from datetime import datetime
import common.logger_config as logger_config
import uuid
from db.alchemy_db import db
import os

def sync_request(url, entity_id):
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta=os.environ.get('PUSHER_USUARIO_CONSULTA')
    url=url+'?id='+entity_id+'&usuario_consulta='+usuario_consulta
    print("###########################################")
    print("url:",url)
    print("usuario_consulta:",usuario_consulta)
    print("entity id:",entity_id)
    print("###########################################")
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
                               id_user_actualizacion=id_user,
                               base = True,
                               origen_externo = True,
                               nivel='act'
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
            query_tipo_tarea.base = True
            query_tipo_tarea.origen_externo = True
            query_tipo_tarea.nivel = 'act'

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

def sync_fuero(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['id'] is not None:
        #Buscar si existe la inhabilidad en la base de datos
        query_fuero = db.session.query(Dominio).filter(Dominio.id == resp['data']['id']).first()
        if query_fuero is None:
            #hago insert de la inhabilidad
            nuevo_fuero = Dominio(id=uuid.uuid4(),
                               id_dominio_ext=resp['data']['id'],   
                               descripcion=resp['data']['descripcion'],
                               descripcion_corta=resp['data']['descripcion_corta'],
                               fecha_actualizacion=datetime.now(),
                               habilitado=resp['data']['habilitado'],
                               eliminado=not(resp['data']['habilitado']),
                               prefijo=resp['data']['prefijo'],   
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_fuero)

        else:
            print("existe el fuero en la base de datos:", resp['data']['id'])
            #hago el update de fuero
            query_fuero.id_dominio_ext = resp['data']['id']
            query_fuero.descripcion = resp['data']['descripcion']
            query_fuero.descripcion_corta = resp['data']['descripcion_corta']
            query_fuero.fecha_actualizacion=datetime.now()
            query_fuero.habilitado = resp['data']['habilitado']
            query_fuero.eliminado = not(resp['data']['habilitado'])
            query_fuero.prefijo = resp['data']['prefijo']
            query_fuero.id_user_actualizacion=id_user
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
                               id_inhabilidad_ext=resp['data']['id'], 
                               fecha_desde=resp['data']['fecha_desde'], 
                               fecha_hasta=resp['data']['fecha_hasta'], 
                               id_organismo=resp['data']['id_organismo'],
                               id_juez=resp['data']['id_juez'],
                               tipo =resp['data']['tipo'],
                               descripcion=resp['data']['descripcion'],
                               habilitado=resp['data']['habilitado'],
                               eliminado=not(resp['data']['habilitado']),
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_inhabilidad)

        else:
            #hago update de la inhabilidad
            query_inhabilidad.id_inhabilidad_ext = resp['data']['id']
            query_inhabilidad.fecha_desde = resp['data']['fecha_desde']
            query_inhabilidad.fecha_hasta = resp['data']['fecha_hasta']
            query_inhabilidad.id_organismo = resp['data']['id_organismo']
            query_inhabilidad.id_juez = resp['data']['id_juez']
            query_inhabilidad.tipo =resp['data']['tipo']
            query_inhabilidad.descripcion = resp['data']['descripcion']
            query_inhabilidad.habilitado = resp['data']['habilitado']
            query_inhabilidad.eliminado = not(resp['data']['habilitado'])
            query_inhabilidad.id_ext = resp['data']['id']
            query_inhabilidad.fecha_actualizacion=datetime.now()
            query_inhabilidad.id_user_actualizacion=id_user

        db.session.commit()
    return resp

""" def sync_grupo(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['id'] is not None:
        #Buscar si existe el organismo en la base de datos
        query_organismo = db.session.query(Grupo).filter(Grupo.id == resp['data']['id']).first()
        if query_organismo is None:
            #hago insert del organismo
            nuevo_organismo = Grupo(id=uuid.uuid4(),
                               id_organismo=resp['data']['id'],
                               nombre=resp['data']['descripcion'], 
                               circunscripcion_judicial=resp['data']['circunscripcion_judicial'],    
                               descripcion=resp['data']['descripcion'],
                               descripcion_corta=resp['data']['descripcion_corta'],
                               id_dominio=resp['data']['id_fuero'],
                               eliminado=not(resp['data']['habilitado']),
                               fecha_actualizacion=datetime.now(),
                               fecha_creacion=datetime.now(),
                               id_user_actualizacion=id_user,
                               base = True,
                            )
            db.session.add(nuevo_organismo)

        else:
            #hago update del organismo
            query_organismo.descricion = resp['data']['descripcion']
            query_organismo.descripcion_corta = resp['data']['descripcion_corta'] 
            query_organismo.circunscripcion_judicial = resp['data']['circunscripcion_judicial']
            query_organismo.eliminado = not(resp['data']['habilitado'])
            query_organismo.nombre = resp['data']['descripcion']
            query_organismo.id_dominio = resp['data']['id_fuero']
            query_organismo.fecha_actualizacion=datetime.now()
            query_organismo.fecha_creacion = datetime.now()
            query_organismo.id_user_actualizacion=id_user
            query_organismo.base = True

        db.session.commit()
    return resp """

def sync_organismo(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['id'] is not None:
        #Buscar si existe el organismo en la base de datos
        query_organismo = db.session.query(Organismo).filter(Organismo.id == resp['data']['id']).first()
        if query_organismo is None:
            #hago insert del organismo
            nuevo_organismo = Organismo(id=uuid.uuid4(),
                               id_organismo_ext=resp['data']['id'],
                               circunscripcion_judicial=resp['data']['circunscripcion_judicial'],    
                               descripcion=resp['data']['descripcion'],
                               descripcion_corta=resp['data']['descripcion_corta'],
                               id_fuero=resp['data']['id_fuero'],
                               habilitado=resp['data']['habilitado'],
                               eliminado=not(resp['data']['habilitado']),
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user,
                               id_tarea_grupo_base=resp['data']['id_tarea_grupo_base']
                            )
            db.session.add(nuevo_organismo)

        else:
            #hago update del organismo
            query_organismo.id_organismo_ext = resp['data']['id']
            query_organismo.descricion = resp['data']['descripcion']
            query_organismo.descripcion_corta = resp['data']['descripcion_corta'] 
            query_organismo.circunscripcion_judicial = resp['data']['circunscripcion_judicial']
            query_organismo.habilitado = resp['data']['habilitado']
            query_organismo.eliminado = not(resp['data']['habilitado'])
            query_organismo.id_fuero = resp['data']['id_fuero']
            query_organismo.fecha_actualizacion=datetime.now()
            query_organismo.id_user_actualizacion=id_user
            query_organismo.id_tarea_grupo_base = resp['data']['id_tarea_grupo_base']

        db.session.commit()
        print("Organismo sincronizado:", resp['data']['id'])
    return resp

def sync_subtipo_tarea(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json:",resp)
    json = {'data': {'id': '701fee35-c87d-4157-85f0-6a2aacad1198', 'descripcion': 'Auto de Regulación de Honorarios', 'descripcion_corta': 'auto-reg-honorarios', 'observaciones': '.', 'id_tipo_act_juzgado': '901a84ee-86e1-497e-ba7f-72f4223d7565', 'descripcion_tipo_act_juzgado': 'Auto', 'habilitado_tipo_act_juzgado': True, 'username': 'simperiale@jus.mendoza.gov.ar', 'nombre_usuario': 'Silvia', 'apellido_usuario': 'Imperiale', 'fecha_creacion': '04-07-2024 12:21', 'fecha_actualizacion': '11-06-2025 11:48', 'habilitado': True}}
    if resp and resp['data']['id'] is not None:
        query_subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id_ext == resp['data']['id']).first()
        if query_subtipo is None:
            query_tipo= db.session.query(TipoTarea).filter(TipoTarea.id_ext == resp['data']['id_tipo_act_juzgado']).first()
            if query_tipo is not None:
            #hago insert del organismo
                nuevo_subtipo = SubtipoTarea(id=uuid.uuid4(),
                                id_ext=resp['data']['id'],
                                id_tipo =query_tipo.id,
                                nombre=resp['data']['descripcion'],
                                nombre_corto=resp['data']['descripcion_corta'],
                                eliminado=not(resp['data']['habilitado']),
                                fecha_actualizacion=datetime.now(),
                                id_user_actualizacion=id_user,
                                base = True,
                                origen_externo = True
                                )
                db.session.add(nuevo_subtipo)
                db.session.commit()

        else:
            #hago update del subtipo
            #busco el tipo de tarea asociado al subtipo
            query_tipo= db.session.query(TipoTarea).filter(TipoTarea.id_ext == resp['data']['id_tipo_act_juzgado']).first()
            if query_tipo is not None:
                query_subtipo.nombre = resp['data']['descripcion']
                query_subtipo.nombre_corto = resp['data']['descripcion_corta']
                query_subtipo.id_ext = resp['data']['id']
                query_subtipo.id_tipo =query_tipo.id
                query_subtipo.eliminado = not(resp['data']['habilitado'])
                query_subtipo.id_user_actualizacion = id_user
                query_subtipo.fecha_actualizacion=datetime.now()
                query_subtipo.base = True
                query_subtipo.origen_externo = True

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

