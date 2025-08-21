from apiflask import APIBlueprint
from flask import g, request
import decorators.role as rol
import controller.full_sync as full_sync
import common.utils as utils
import common.error_handling as error_handling
import common.exceptions as exceptions
import common.auth as auth_token
import common.logger_config as logger_config
import traceback

full_sync_b = APIBlueprint('full_sync_blueprint', __name__)

#################Before requests ##################
@full_sync_b.before_request
def before_request():
    if request.method == 'OPTIONS':
        return  # Skip custom logic for OPTIONS requests
    
    #jsonHeader = auth_token.verify_header() or {}
    #g.username = jsonHeader.get('user_name', '')
    #g.type = jsonHeader.get('type', '')
    #g.rol = jsonHeader.get('user_rol', '')

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all tipos de tareas from Pusher',
    summary='Full Sync Tipos Tareas',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/tipos_tareas')
#@rol.require_role(['admin', 'superadmin'])  # Restrict to admin users
def sync_all_tipos_tareas():
    try:
        # Get user ID for audit trail
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        print("id_user:",id_user)
        
        # Perform full sync
        print("calling full_sync_tipos_tareas")
        print("******************************")
        success_count, error_count = full_sync.full_sync_tipos_tareas(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        traceback.print_exc()
        logger_config.logger.error(f"Error in full sync tipos tareas: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all usuarios from Pusher',
    summary='Full Sync Usuarios',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/usuarios')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_usuarios():
    try:
        id_user = utils.get_username_id(g.username)
        success_count, error_count = full_sync.full_sync_usuarios(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync usuarios: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all organismos from Pusher',
    summary='Full Sync Organismos',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/organismos')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_organismos():
    try:
        id_user = utils.get_username_id(g.username)
        success_count, error_count = full_sync.full_sync_organismos(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync organismos: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all fuero from Pusher',
    summary='Full Sync Fuero',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/fuero')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_fuero():
    try:
        id_user = utils.get_username_id(g.username)
        success_count, error_count = full_sync.full_sync_fuero(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync fuero: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all inhabilidad from Pusher',
    summary='Full Sync Inhabilidad',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/inhabilidad')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_inhabilidad():
    try:
        id_user = utils.get_username_id(g.username)
        success_count, error_count = full_sync.full_sync_inhabilidad(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync inhabilidad: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all subtipo tarea from Pusher',
    summary='Full Sync Subtipo Tarea',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/subtipo_tarea')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_subtipo_tarea():
    try:
        id_user = utils.get_username_id(g.username)
        success_count, error_count = full_sync.full_sync_subtipo_tarea(id_user)
        
        return {
            "success": True,
            "message": f"Full sync completed: {success_count} successful, {error_count} errors",
            "data": {
                "success_count": success_count,
                "error_count": error_count
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync subtipo tarea: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all entities from Pusher',
    summary='Full Sync All Entities',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/all')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_entities():
    try:
        #id_user = utils.get_username_id(g.username)
        results = full_sync.full_sync_all()
        
        return {
            "success": True,
            "message": "Full sync of all entities completed",
            "data": results
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync all entities: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Get sync status and statistics',
    summary='Sync Status',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/status')
#@rol.require_role(['admin', 'superadmin'])
def get_sync_status():
    try:
        # You can implement status tracking here
        # For now, return basic info
        return {
            "success": True,
            "message": "Sync system is operational",
            "data": {
                "last_sync": "Not implemented yet",
                "sync_enabled": True,
                "entities_supported": ["tipo_act_juzgado", "usuario", "organismo", "fuero", "inhabilidad", "subtipo_act_juzgado"]
            }
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error getting sync status: {err}")
        raise exceptions.ValidationError(err)
