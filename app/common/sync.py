import requests
from models.alch_model import Usuario, TipoTarea, SubtipoTarea, TipoTareaDominio, Inhabilidad, Organismo, Grupo,  Dominio
from datetime import datetime
import common.logger_config as logger_config
import uuid
from db.alchemy_db import db
import os
import traceback
import time
from common.utils import normalize_spanish_text

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

def sync_tipo_tarea(entity, entity_id, url,id_user=None):
    try:
        print("receiving URL MOFO from sync_tipo_tarea",url)
        print("passing to sync_request")
        print("*"*50)   
        print("Entity:",entity)
        print("id_user:",id_user)
        resp= sync_request(url, entity_id)
        print("json resp:",resp)
        print("aca esta la info de pusher")
     
        if resp and resp['data']['id'] is not None:
            #Buscar si existe el tipo de tarea en la base de datos
            x_dominio_ext = 'd36d2054-073c-4b9c-bd3d-baf93009091a'
                #id Juzgado de Paz de Lavalle de la tabla organismo
            x_organismo_ext = 'c7452ea9d-0698-4a36-afda-f5ae2fa55d63'

            query_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id_ext == resp['data']['id']).first()
            if query_tipo_tarea is None:
                #hago insert del tipo de tarea
                
                nuevo_tipo_tarea = TipoTarea(id=uuid.uuid4(),
                                id_ext=resp['data']['id'], 
                                clasificacion_ext=entity,
                                nombre=normalize_spanish_text(resp['data']['descripcion']), 
                                codigo_humano=normalize_spanish_text(resp['data']['descripcion_corta']), 
                                eliminado=not(resp['data']['habilitado']),
                                fecha_actualizacion=datetime.now(),
                                id_user_actualizacion=id_user if id_user else None,
                                base = True,
                                origen_externo = True,
                                nivel='act',
                                id_dominio_ext=x_dominio_ext,
                                id_organismo_ext=x_organismo_ext
                                )
                db.session.add(nuevo_tipo_tarea)
                # Flush to get the ID
                db.session.flush()
                
                nuevo_tipo_tarea_dominio = TipoTareaDominio(id=uuid.uuid4(),
                                                       id_tipo_tarea=nuevo_tipo_tarea.id,
                                                       id_dominio_ext=x_dominio_ext,
                                                       id_organismo_ext=x_organismo_ext,
                                                       eliminado=False,
                                                       fecha_actualizacion=datetime.now(),
                                                       id_user_actualizacion=id_user if id_user else None
                                                       )
                db.session.add(nuevo_tipo_tarea_dominio)
            else:
                query_tipo_tarea_dominio = db.session.query(TipoTareaDominio).filter(TipoTareaDominio.id_tipo_tarea == query_tipo_tarea.id, TipoTareaDominio.id_dominio == x_dominio, TipoTareaDominio.id_organismo == x_organismo).first()
                if query_tipo_tarea_dominio is None:
                    #hago insert del tipo de tarea dominio
                    nuevo_tipo_tarea_dominio = TipoTareaDominio(id=uuid.uuid4(),
                                                            id_tipo_tarea=query_tipo_tarea.id,
                                                            id_dominio_ext=x_dominio_ext,
                                                            id_organismo_ext=x_organismo_ext,
                                                            eliminado=False,
                                                            fecha_actualizacion=datetime.now(),
                                                            id_user_actualizacion=id_user if id_user else None
                                                           )
                    db.session.add(nuevo_tipo_tarea_dominio)
                #hago update del tipo de tarea
                query_tipo_tarea.nombre = normalize_spanish_text(resp['data']['descripcion'])
                query_tipo_tarea.codigo_humano = normalize_spanish_text(resp['data']['descripcion_corta']) 
                query_tipo_tarea.eliminado = not(resp['data']['habilitado'])
                query_tipo_tarea.id_ext = resp['data']['id']
                query_tipo_tarea.clasificacion_ext = entity
                query_tipo_tarea.fecha_actualizacion=datetime.now()
                query_tipo_tarea.id_user_actualizacion=id_user if id_user else None
                query_tipo_tarea.base = True
                query_tipo_tarea.origen_externo = True
                query_tipo_tarea.nivel = 'act'
                query_tipo_tarea.id_dominio_ext = x_dominio_ext
                query_tipo_tarea.id_organismo_ext = x_organismo_ext

            db.session.commit()
            return resp
    except Exception as e:
        print("Error al sincronizar el tipo de tarea:",e)
        traceback.print_exc()
        db.session.rollback()
        return None




def sync_usuario(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json roles:",resp)    
    if resp and resp['data']['username'] is not None:
        #Buscar el usuario en la base de datos
        print("LOOKING FOR EXISTING USER IN DB")
        print("*"*50)
        query_usr = db.session.query(Usuario).filter(Usuario.username == resp['data']['username']).first()
        print("query_usr:",query_usr)
        print("*"*50)
        if query_usr is None:
            print("NO EXISTE EL USUARIO EN LA BASE DE DATOS CREANDO NUEVO USUARIO")
            print("*"*50)
            #hago insert del usuario
            nuevo_usuario = Usuario(id=uuid.uuid4(),
                               username=resp['data']['username'], 
                               email=resp['data']['email'], 
                               nombre=normalize_spanish_text(resp['data']['nombre']), 
                               apellido=normalize_spanish_text(resp['data']['apellido']), 
                               id_ext = resp['data']['id'],
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user,
                               eliminado=not(resp['data']['habilitado']),
                               dni =resp['data']['nro_documento'],
                               suspendido=False)

   
            db.session.add(nuevo_usuario)
        else:
            print("EXISTE EL USUARIO EN LA BASE DE DATOS ACTUALIZANDO USUARIO")
            print("username:",query_usr.username)
            print("email:",query_usr.email)
            print("nombre:",query_usr.nombre)
            print("apellido:",query_usr.apellido)
            print("id_ext:",query_usr.id_ext)
            print("fecha_actualizacion:",query_usr.fecha_actualizacion)
            print("id_user_actualizacion:",query_usr.id_user_actualizacion)
            print("eliminado:",query_usr.eliminado)
            print("dni:",query_usr.dni)
            print("id:",query_usr.id)
            print("*"*50)
            #hago update del usuario
            query_usr.username = resp['data']['username']
            query_usr.email = resp['data']['email']
            query_usr.nombre = normalize_spanish_text(resp['data']['nombre'])
            query_usr.apellido = normalize_spanish_text(resp['data']['apellido'])
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
        query_fuero = db.session.query(Dominio).filter(Dominio.id_dominio_ext == resp['data']['id']).first()
        if query_fuero is None:
            nuevo_fuero = Dominio(id=uuid.uuid4(),
                               id_dominio_ext=resp['data']['id'],   
                               descripcion=normalize_spanish_text(resp['data']['descripcion']),
                               descripcion_corta=normalize_spanish_text(resp['data']['descripcion_corta']),
                               fecha_actualizacion=datetime.now(),
                               eliminado=not(resp['data']['habilitado']),
                               prefijo=resp['data']['prefijo'],   
                               id_user_actualizacion=id_user
                            )
            db.session.add(nuevo_fuero)

        else:
            print("existe el fuero en la base de datos:", resp['data']['id'])
            #hago el update de fuero
            query_fuero.id_dominio_ext = resp['data']['id']
            query_fuero.descripcion = normalize_spanish_text(resp['data']['descripcion'])
            query_fuero.descripcion_corta = normalize_spanish_text(resp['data']['descripcion_corta'])
            query_fuero.fecha_actualizacion=datetime.now()
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
                               descripcion=normalize_spanish_text(resp['data']['descripcion']),
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
            query_inhabilidad.eliminado = not(resp['data']['habilitado'])
            query_inhabilidad.id_ext = resp['data']['id']
            query_inhabilidad.fecha_actualizacion=datetime.now()
            query_inhabilidad.id_user_actualizacion=id_user

        db.session.commit()
    return resp



def sync_organismo(entity_id, url,id_user):
    try:
        resp = sync_request(url, entity_id)
        print("json roles:",resp)    
        if resp and resp['data']['id'] is not None:
            #Buscar si existe el organismo en la base de datos
            query_organismo = db.session.query(Organismo).filter(Organismo.id_organismo_ext == resp['data']['id']).first()
            if query_organismo is None:
                #hago insert del organismo
                print("INSERTING NEW ORGANISMO")
                print("*"*50)
                id_nuevo_organismo = uuid.uuid4()
                nuevo_organismo = Organismo(id=id_nuevo_organismo,
                               id_organismo_ext=resp['data']['id'],
                               circunscripcion_judicial=normalize_spanish_text(resp['data']['circunscripcion_judicial']),    
                               descripcion=normalize_spanish_text(resp['data']['descripcion']),
                               descripcion_corta=normalize_spanish_text(resp['data']['descripcion_corta']),
                               id_dominio_ext=resp['data']['id_fuero'],
                               habilitado=resp['data']['habilitado'],
                               eliminado=not(resp['data']['habilitado']),
                               fecha_actualizacion=datetime.now(),
                               id_user_actualizacion=id_user,
                               id_tarea_grupo_base=resp['data']['id_tarea_grupo_base']
                            )
                db.session.add(nuevo_organismo)

                query_dominio= db.session.query(Dominio).filter(Dominio.id_dominio_ext == resp['data']['id_fuero']).first()
                db.session.flush()
             
                print("dominio_ext:",query_dominio.id_dominio_ext)
                print("id_dominio:",query_dominio.id)
            

                nuevo_grupo = Grupo(id=uuid.uuid4(),
                                    #id_organismo = id_nuevo_organismo,
                                    id_organismo_ext = resp['data']['id'],
                                    id_dominio_ext = resp['data']['id_fuero'],
                                    #id_dominio = query_dominio.id,
                                    nombre = normalize_spanish_text(resp['data']['descripcion']),
                                    descripcion = normalize_spanish_text(resp['data']['descripcion']),
                                    id_user_actualizacion = id_user,
                                    fecha_actualizacion = datetime.now(),
                                    fecha_creacion = datetime.now(),
                                    eliminado = not(resp['data']['habilitado']),
                                    suspendido = False,
                                    base = True
                                    )
                db.session.add(nuevo_grupo)

            else:
                #hago update del organismo
                print("UPDATING ORGANISMO")
                print("*"*50)
                query_organismo.id_organismo_ext = resp['data']['id']
                query_organismo.descricion = normalize_spanish_text(resp['data']['descripcion'])
                query_organismo.descripcion_corta = normalize_spanish_text(resp['data']['descripcion_corta'])
                query_organismo.circunscripcion_judicial = normalize_spanish_text(resp['data']['circunscripcion_judicial'])
                query_organismo.habilitado = resp['data']['habilitado']
                query_organismo.eliminado = not(resp['data']['habilitado'])
                query_organismo.id_dominio_ext = resp['data']['id_fuero']
                query_organismo.fecha_actualizacion=datetime.now()
                query_organismo.id_user_actualizacion=id_user
                query_organismo.id_tarea_grupo_base = resp['data']['id_tarea_grupo_base']

                query_grupo = db.session.query(Grupo).filter(Grupo.id_organismo_ext == query_organismo.id_organismo_ext).first()
                if query_grupo is not None:
                    query_grupo.id_dominio_ext = resp['data']['id_fuero']
                    query_grupo.nombre = normalize_spanish_text(resp['data']['descripcion'])
                    query_grupo.descripcion = normalize_spanish_text(resp['data']['descripcion'])
                    query_grupo.id_user_actualizacion = id_user
                    query_grupo.fecha_actualizacion = datetime.now()
                    query_grupo.eliminado = not(resp['data']['habilitado'])
                    query_grupo.base = True
                else:
                    nuevo_grupo = Grupo(id=uuid.uuid4(),
                                    #id_organismo = query_organismo.id, 
                                    id_nuevo_organismo_ext = resp['data']['id'],
                                    id_dominio_ext = resp['data']['id_fuero'],
                                    nombre = normalize_spanish_text(resp['data']['descripcion']),
                                    descripcion = normalize_spanish_text(resp['data']['descripcion']),
                                    id_user_actualizacion = id_user,
                                    fecha_actualizacion = datetime.now(),
                                    fecha_creacion = datetime.now(),
                                    eliminado = not(resp['data']['habilitado']),
                                    suspendido = False,
                                    base = True
                                    )
                    db.session.add(nuevo_grupo)    

            db.session.commit()
            print("Organismo y grupo sincronizado:", resp['data']['id'])
        return resp
    except Exception as e:
        print("Error al sincronizar el organismo:", e)
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return None

def sync_dominio(entity_id, url,id_user):
    try:
        resp = sync_request(url, entity_id)
        print("json roles:",resp)    
        if resp and resp['data']['id'] is not None:
            #Buscar si existe el dominio en la base de datos
            query_dominio = db.session.query(Dominio).filter(Dominio.id_dominio_ext == resp['data']['id']).first()
            if query_dominio is None:
                #hago insert del dominio
                print("INSERTING NEW DOMINIO")
                print("*"*50)
                nuevo_dominio = Dominio(
                    id=uuid.uuid4(),
                    id_dominio_ext=resp['data']['id'],
                    descripcion=normalize_spanish_text(resp['data']['descripcion']),
                    descripcion_corta=normalize_spanish_text(resp['data']['descripcion_corta']),
                    prefijo=resp['data']['prefijo'],
                    fecha_actualizacion=datetime.now(),
                    habilitado=resp['data']['habilitado'],
                    eliminado=not(resp['data']['habilitado']),
                    id_user_actualizacion=id_user
                )
                db.session.add(nuevo_dominio)
            else:
                #hago update del dominio
                print("UPDATING DOMINIO")
                print("*"*50)
                query_dominio.descripcion = normalize_spanish_text(resp['data']['descripcion'])
                query_dominio.descripcion_corta = normalize_spanish_text(resp['data']['descripcion_corta'])
                query_dominio.prefijo = resp['data']['prefijo']
                query_dominio.habilitado = resp['data']['habilitado']
                query_dominio.eliminado = not(resp['data']['habilitado'])
                query_dominio.fecha_actualizacion = datetime.now()
                query_dominio.id_user_actualizacion = id_user

            db.session.commit()
            print("Dominio sincronizado:", resp['data']['id'])
        return resp
    except Exception as e:
        print("Error al sincronizar el dominio:", e)
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return None

def sync_subtipo_tarea(entity_id, url,id_user):
    resp = sync_request(url, entity_id)
    print("json:",resp)
    #json = {'data': {'id': '701fee35-c87d-4157-85f0-6a2aacad1198', 'descripcion': 'Auto de Regulación de Honorarios', 'descripcion_corta': 'auto-reg-honorarios', 'observaciones': '.', 'id_tipo_act_juzgado': '901a84ee-86e1-497e-ba7f-72f4223d7565', 'descripcion_tipo_act_juzgado': 'Auto', 'habilitado_tipo_act_juzgado': True, 'username': 'simperiale@jus.mendoza.gov.ar', 'nombre_usuario': 'Silvia', 'apellido_usuario': 'Imperiale', 'fecha_creacion': '04-07-2024 12:21', 'fecha_actualizacion': '11-06-2025 11:48', 'habilitado': True}}
    if resp and resp['data']['id'] is not None:
        query_subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id_ext == resp['data']['id']).first()
        if query_subtipo is None:
            query_tipo= db.session.query(TipoTarea).filter(TipoTarea.id_ext == resp['data']['id_tipo_act_juzgado']).first()
            if query_tipo is not None:
            #hago insert del organismo
                nuevo_subtipo = SubtipoTarea(id=uuid.uuid4(),
                                id_ext=resp['data']['id'],
                                id_tipo =query_tipo.id,
                                nombre=normalize_spanish_text(resp['data']['descripcion']),
                                nombre_corto=normalize_spanish_text(resp['data']['descripcion_corta']),
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

