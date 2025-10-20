import requests
import os
from db.alchemy_db import db
import common.utils as utils
import common.sync as sync
import common.logger_config as logger_config
from datetime import datetime
import traceback    
import json
import time
import re

def full_sync_tipos_tareas(clasificacion=None, id_user=None,url_post=None,is_subtipo=False):
    """Sync all tipos de tareas from Pusher"""
    logger_config.logger.info("Starting full sync of tipos de tareas...")
    
    #getting all the records at once and then pass them one by one to the sync_tipo_tarea function
    usher_apikey = os.environ.get('PUSHER_API_KEY')
    system_apikey = os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
    url_post=""
    base_url=""
    entity=""
    if clasificacion=="parte":
        #https://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-parte/
        base_url = os.environ.get('PUSHER_URL_TIPOS_TAREAS_PARTE', '')
        url_post = os.environ.get('PUSHER_URL_TIPOS_TAREAS_PARTE_POST', '')
        print("BASE URL: ",base_url)
        print("URL POST: ",url_post)
        entity="TIPO_ACT_PARTE"

    if clasificacion=="juzgado":
        print("clasificacion from controller: ",clasificacion)
        #https://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-juzgado/
        base_url = os.environ.get('PUSHER_URL_TIPOS_TAREAS_JUZGADO', '')
        url_post=os.environ.get('PUSHER_URL_TIPOS_TAREAS_JUZGADO_POST', '')
        entity="TIPO_ACT_JUZGADO"
        print("BASE URL: ",base_url)
        print("URL POST: ",url_post)
   
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    sync_url = f"{base_url}{usuario_consulta}"
    logger_config.logger.info("Obtained records from pusher")
    logger_config.logger.debug(f"sync_url: {sync_url}")
    logger_config.logger.debug(f"url_post: {url_post}")
    logger_config.logger.debug(f"usuario_consulta: {usuario_consulta}")
    logger_config.logger.debug(f"headers: {headers}")
    logger_config.logger.debug(f"id_user: {id_user}")
   
    logger_config.logger.debug("******************************")
    response = requests.get(headers=headers,url=sync_url)
  
    tipos_data = response.json()
    logger_config.logger.debug("******************************")
    logger_config.logger.debug(f"tipos_data: {tipos_data}")
    logger_config.logger.debug("******************************")
   
    success_count = 0
    error_count = 0
    
    
    if not tipos_data or 'data' not in tipos_data:
        logger_config.logger.error("No data received from Pusher for tipos de tareas")
        return 0, 1

    for tipo_data in tipos_data['data']:
        try:
            id = tipo_data['id']
            logger_config.logger.debug(f"tipo_data: {tipo_data}")
            logger_config.logger.debug("******************************")
            logger_config.logger.info(f'sending URL: {url_post}')
            logger_config.logger.debug(f'id_user: {id_user}')
            logger_config.logger.debug('USER FROM CONTROLLER BEFORE SYNC')
            logger_config.logger.debug(f'entity: {entity}')
            logger_config.logger.debug(f'id: {id}')
            sync.sync_tipo_tarea(clasificacion,entity, tipo_data['id'],url_post, id_user)
            success_count += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing tipo tarea {tipo_data.get('id', 'unknown')}: {e}")
            error_count += 1
       
        time.sleep(0.2)
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    

def full_sync_usuarios(id_user=None):
    """Sync all usuarios from Pusher"""
    logger_config.logger.info("Starting full sync of usuarios...")
    usher_apikey = os.environ.get('PUSHER_API_KEY')
    system_apikey = os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
    base_url = os.environ.get('PUSHER_URL_USUARIOS', '')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    sync_url = f"{base_url}{usuario_consulta}"
    sync_url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/usuario/"
    logger_config.logger.info("Obtained records from pusher")
    logger_config.logger.debug(f"sync_url: {sync_url}")
    logger_config.logger.debug(f"usuario_consulta: {usuario_consulta}")
    logger_config.logger.debug(f"headers: {headers}")
    logger_config.logger.debug(f"id_user: {id_user}")
   
    logger_config.logger.debug("******************************")
    response = requests.get(headers=headers,url=sync_url)
  
    usuarios_data = response.json()
    logger_config.logger.debug(f"usuarios_data: {usuarios_data}")
    logger_config.logger.debug("******************************")
   
    success_count = 0
    error_count = 0
    if not usuarios_data or 'data' not in usuarios_data:
        logger_config.logger.error("No data received from Pusher for usuarios")
        return 0, 1

    for usuario_data in usuarios_data['data']:
        try:
            logger_config.logger.debug(f"usuarios_data: {usuario_data}")
            logger_config.logger.debug("******************************")
            logger_config.logger.debug(f'sending URL: {sync_url_post}')
            
            sync.sync_usuario(usuario_data['id'],sync_url_post, id_user)
            success_count += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing usuario {usuario_data.get('id', 'unknown')}: {e}")
            error_count += 1
       
        time.sleep(0.1)
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
 
 
            
         

def full_sync_organismos(id_user=None):
    """Sync all organismos from Pusher"""
    logger_config.logger.info("Starting full sync of organismos...")


    usher_apikey = os.environ.get('PUSHER_API_KEY')
    system_apikey = os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
    base_url = os.environ.get('PUSHER_URL_ORGANISMOS', '')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    sync_url = f"{base_url}{usuario_consulta}"
    sync_url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/organismo/"
    logger_config.logger.info("Obtained records from pusher")
    logger_config.logger.debug(f"sync_url: {sync_url}")
    logger_config.logger.debug(f"usuario_consulta: {usuario_consulta}")
    logger_config.logger.debug(f"headers: {headers}")
    logger_config.logger.debug(f"id_user: {id_user}")
   
    logger_config.logger.debug("******************************")
    response = requests.get(headers=headers,url=sync_url)
  
    organismos_data = response.json()
    logger_config.logger.debug(f"organismos_data: {organismos_data}")
    logger_config.logger.debug("******************************")
   
    success_count = 0
    error_count = 0
    if not organismos_data or 'data' not in organismos_data:
        logger_config.logger.error("No data received from Pusher for usuarios")
        return 0, 1

    for fuero_data in organismos_data['data']:
        try:
            logger_config.logger.debug(f"organismos_data: {fuero_data}")
            logger_config.logger.debug("******************************")
            logger_config.logger.debug(f'sending URL: {sync_url_post}')
            
            sync.sync_organismo(fuero_data['id'],sync_url_post, id_user)
            success_count += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing usuario {fuero_data.get('id', 'unknown')}: {e}")
            error_count += 1
       
        time.sleep(0.1)
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    
    
    success_count = 0
    error_count = 0
def full_sync_dominios(id_user=None):
    """Sync all dominios from Pusher"""
    logger_config.logger.info("Starting full sync of dominios...")


    usher_apikey = os.environ.get('PUSHER_API_KEY')
    system_apikey = os.environ.get('PUSHER_API_SYSTEM')
   
    headers = {'x-api-key': usher_apikey, 'x-api-system':system_apikey}
    base_url = os.environ.get('PUSHER_URL_DOMINIOS', '')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    sync_url = f"{base_url}{usuario_consulta}"
    sync_url_post="https://dev-backend.usher.pjm.gob.ar/api/v1/fuero/"
    logger_config.logger.info("Obtained records from pusher")
    logger_config.logger.debug(f"sync_url: {sync_url}")
    logger_config.logger.debug(f"usuario_consulta: {usuario_consulta}")
    logger_config.logger.debug(f"headers: {headers}")
    logger_config.logger.debug(f"id_user: {id_user}")
   
    logger_config.logger.debug("******************************")
    response = requests.get(headers=headers,url=sync_url)
  
    dominios_data = response.json()
    logger_config.logger.debug(f"fueros_data: {dominios_data}")
    logger_config.logger.debug("******************************")
   
    success_count = 0
    error_count = 0
    if not dominios_data or 'data' not in dominios_data:
        logger_config.logger.error("No data received from Pusher for fueros")
        return 0, 1

    for dominio_data in dominios_data['data']:
        try:
            logger_config.logger.debug(f"fueros_data: {dominio_data}")
            logger_config.logger.debug("******************************")
            logger_config.logger.debug(f'sending URL: {sync_url_post}')
            
            sync.sync_dominio(dominio_data['id'],sync_url_post, id_user)
            success_count += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing usuario {dominio_data.get('id', 'unknown')}: {e}")
            error_count += 1
       
        time.sleep(0.1)
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    
    return success_count, error_count

def full_sync_inhabilidad(id_user=None):
    """Sync all inhabilidad from Pusher"""
    logger_config.logger.info("Starting full sync of inhabilidad...")
    
    inhabilidad_data = sync.inhabilidad()
    
    if not inhabilidad_data or 'data' not in inhabilidad_data:
        logger_config.logger.error("No data received from Pusher for inhabilidad")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for inhabilidad_item in inhabilidad_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', '')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}&tipo_entidad=inhabilidad"
            
            sync.sync_inhabilidad(inhabilidad_item['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced inhabilidad: {inhabilidad_item.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing inhabilidad {inhabilidad_item.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count

def full_sync_subtipo_tarea(id_user=None,url_post=None):
    """Sync all subtipo tarea from Pusher"""
    logger_config.logger.info("Starting full sync of subtipo tarea...")
    
    subtipo_data = sync.subtipo_tarea()
    
    if not subtipo_data or 'data' not in subtipo_data:
        logger_config.logger.error("No data received from Pusher for subtipo_act_juzgado")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for subtipo_item in subtipo_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', '')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}&tipo_entidad=subtipo_act_juzgado"
            
            sync.sync_subtipo_tarea(subtipo_item['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced subtipo tarea: {subtipo_item.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing subtipo tarea {subtipo_item.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count


