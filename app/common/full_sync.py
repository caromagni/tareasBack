import requests
import os
from db.alchemy_db import db
import common.utils as utils
import common.sync as sync
import common.logger_config as logger_config
from datetime import datetime
import traceback

def get_all_entities_from_pusher(entity_type):
    """Get all entities of a specific type from Pusher API"""
    x_api_key = os.environ.get('PUSHER_API_KEY')
    x_api_system = os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    
    # Base URL already includes desc_sistema=tareas&usuario_consulta=
    base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
    
    # Just add the entity type and usuario_consulta value
    url = f"{base_url}{usuario_consulta}&tipo_entidad={entity_type}"
    
    headers = {'x-api-key': x_api_key, 'x-api-system': x_api_system}
    
    try:
        logger_config.logger.info(f"Fetching all {entity_type} from Pusher: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        logger_config.logger.info(f"Received {len(data.get('data', []))} {entity_type} from Pusher")
        return data
    except Exception as e:
        logger_config.logger.error(f"Error getting all {entity_type}: {e}")
        return None

def full_sync_tipos_tareas(id_user=None):
    """Sync all tipos de tareas from Pusher"""
    logger_config.logger.info("Starting full sync of tipos de tareas...")
    
    # Get all tipos de tareas from Pusher
    tipos_data = get_all_entities_from_pusher('tipo_act_juzgado')
    
    if not tipos_data or 'data' not in tipos_data:
        logger_config.logger.error("No data received from Pusher for tipos de tareas")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for tipo_data in tipos_data['data']:
        try:
            # Use existing sync function for each entity
            # We need to construct the URL for individual sync

            #https://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-juzgado/?habilitado=H&rows=10&sortfield=descripcion&sortorder=ASC
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-juzgado/?habilitado=H&rows=1000&usuario_consulta=')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}"
            
            sync.sync_tipo_tarea(tipo_data['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced tipo tarea: {tipo_data.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing tipo tarea {tipo_data.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count

def full_sync_usuarios(id_user=None):
    """Sync all usuarios from Pusher"""
    logger_config.logger.info("Starting full sync of usuarios...")
    
    usuarios_data = get_all_entities_from_pusher('usuario')
    
    if not usuarios_data or 'data' not in usuarios_data:
        logger_config.logger.error("No data received from Pusher for usuarios")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for usuario_data in usuarios_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}&tipo_entidad=usuario"
            
            sync.sync_usuario(usuario_data['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced usuario: {usuario_data.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing usuario {usuario_data.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count

def full_sync_organismos(id_user=None):
    """Sync all organismos from Pusher"""
    logger_config.logger.info("Starting full sync of organismos...")
    
    organismos_data = get_all_entities_from_pusher('organismo')
    
    if not organismos_data or 'data' not in organismos_data:
        logger_config.logger.error("No data received from Pusher for organismos")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for organismo_data in organismos_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}&tipo_entidad=organismo"
            
            sync.sync_organismo(organismo_data['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced organismo: {organismo_data.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing organismo {organismo_data.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count

def full_sync_fuero(id_user=None):
    """Sync all fuero from Pusher"""
    logger_config.logger.info("Starting full sync of fuero...")
    
    fuero_data = get_all_entities_from_pusher('fuero')
    
    if not fuero_data or 'data' not in fuero_data:
        logger_config.logger.error("No data received from Pusher for fuero")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for fuero_item in fuero_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
            usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
            sync_url = f"{base_url}{usuario_consulta}&tipo_entidad=fuero"
            
            sync.sync_fuero(fuero_item['id'], sync_url, id_user)
            success_count += 1
            logger_config.logger.info(f"Successfully synced fuero: {fuero_item.get('id', 'unknown')}")
        except Exception as e:
            logger_config.logger.error(f"Error syncing fuero {fuero_item.get('id', 'unknown')}: {e}")
            error_count += 1
    
    logger_config.logger.info(f"Full sync completed: {success_count} successful, {error_count} errors")
    return success_count, error_count

def full_sync_inhabilidad(id_user=None):
    """Sync all inhabilidad from Pusher"""
    logger_config.logger.info("Starting full sync of inhabilidad...")
    
    inhabilidad_data = get_all_entities_from_pusher('inhabilidad')
    
    if not inhabilidad_data or 'data' not in inhabilidad_data:
        logger_config.logger.error("No data received from Pusher for inhabilidad")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for inhabilidad_item in inhabilidad_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
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

def full_sync_subtipo_tarea(id_user=None):
    """Sync all subtipo tarea from Pusher"""
    logger_config.logger.info("Starting full sync of subtipo tarea...")
    
    subtipo_data = get_all_entities_from_pusher('subtipo_act_juzgado')
    
    if not subtipo_data or 'data' not in subtipo_data:
        logger_config.logger.error("No data received from Pusher for subtipo_act_juzgado")
        return 0, 1
    
    success_count = 0
    error_count = 0
    
    for subtipo_item in subtipo_data['data']:
        try:
            # Use existing sync function for each entity
            base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
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

def full_sync_all(id_user=None):
    """Sync all entity types from Pusher"""
    logger_config.logger.info("Starting full sync of all entities...")
    
    results = {}
    
    # Sync all entity types
    entity_types = ['tipo_act_juzgado', 'usuario', 'organismo', 'fuero', 'inhabilidad', 'subtipo_act_juzgado']
    
    for entity_type in entity_types:
        try:
            logger_config.logger.info(f"Starting sync of {entity_type}...")
            
            if entity_type == 'tipo_act_juzgado':
                results[entity_type] = full_sync_tipos_tareas(id_user)
            elif entity_type == 'usuario':
                results[entity_type] = full_sync_usuarios(id_user)
            elif entity_type == 'organismo':
                results[entity_type] = full_sync_organismos(id_user)
            elif entity_type == 'fuero':
                results[entity_type] = full_sync_fuero(id_user)
            elif entity_type == 'inhabilidad':
                results[entity_type] = full_sync_inhabilidad(id_user)
            elif entity_type == 'subtipo_act_juzgado':
                results[entity_type] = full_sync_subtipo_tarea(id_user)
                
            logger_config.logger.info(f"Completed sync of {entity_type}: {results[entity_type]}")
            
        except Exception as e:
            logger_config.logger.error(f"Error in full sync of {entity_type}: {e}")
            results[entity_type] = (0, 1)
    
    logger_config.logger.info(f"Full sync of all entities completed: {results}")
    return results