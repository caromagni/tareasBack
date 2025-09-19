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
@full_sync_b.get('/full_sync/tipos_tareas_juzgado')
#@rol.require_role(['admin', 'superadmin'])  # Restrict to admin users
def sync_all_tipos_tareas_juzgado():
    try:
        # Get user ID for audit trail
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        logger_config.logger.debug(f"id_user: {id_user}")
        
        # Perform full sync
        logger_config.logger.info("calling full_sync_tipos_tareas")
        logger_config.logger.debug("******************************")
        clasificacion="juzgado"
        full_sync.full_sync_tipos_tareas(clasificacion,id_user,False)
        
        return {
            "success": True,
            "message": f"Batch job finished, see logs for more detail",
           
        }
    
    except Exception as err:
        traceback.print_exc()
        logger_config.logger.error(f"Error in full sync tipos tareas: {err}")
        raise exceptions.ValidationError(err)


@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all tipos de tareas from Pusher',
    summary='Full Sync Tipos Tareas',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)

@full_sync_b.get('/full_sync/tipos_tareas_parte')
#@rol.require_role(['admin', 'superadmin'])  # Restrict to admin users.
def sync_all_tipos_tareas_parte():
    try:
        # Get user ID for audit trail
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        logger_config.logger.debug(f"id_user: {id_user}")
        
        # Perform full sync

        clasificacion="parte"
        logger_config.logger.info("calling full_sync_tipos_tareas")
        logger_config.logger.debug("******************************")
        print("clasificacion: ",clasificacion)
        full_sync.full_sync_tipos_tareas(clasificacion,id_user,True)
        
        return {
            "success": True,
            "message": f"Batch job finished, see logs for more detail",
           
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
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        logger_config.logger.debug(f"id_user: {id_user}")
        full_sync.full_sync_usuarios(id_user)
        
        return {
            "success": True,
            "message": f"Batch job finished, see logs for more detail",
           
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
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        print("id_user:",id_user)
        full_sync.full_sync_organismos(id_user)
        
        return {
            "success": True,
            "message": f"Batch job finished, see logs for more detail",
           
        }
    
    except Exception as err:
        logger_config.logger.error(f"Error in full sync usuarios: {err}")
        raise exceptions.ValidationError(err)



#sync dominios
@full_sync_b.doc(   
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all dominios from Pusher',
    summary='Full Sync Dominios',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)
@full_sync_b.get('/full_sync/dominios')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_dominios():
    try:
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        logger_config.logger.debug(f"id_user: {id_user}")
        full_sync.full_sync_dominios(id_user)
        
        return {
            "success": True,
            "message": f"Batch job finished, see logs for more detail",
           
        }
    
    except Exception as err:
        print(traceback.format_exc())
        logger_config.logger.error(f"Error in full sync dominios: {err}")
        raise exceptions.ValidationError(err)

@full_sync_b.doc(
    security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth': []}],
    description='Full sync of all fuero from Pusher',
    summary='Full Sync Fuero',
    responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'}
)

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
@full_sync_b.get('/full_sync/tipo_tarea_parte')
#@rol.require_role(['admin', 'superadmin'])
def sync_all_tipo_tarea_parte():
    try:
         # Get user ID for audit trail
        if g is not None:
            if 'username' in g:

                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-parte/"
        clasificacion="tipo_act_parte"
        #url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-juzgado/"
        #clasificacion="tipo_act_juzgado"
        success_count, error_count = full_sync.full_sync_tipos_tareas_parte(clasificacion, id_user,url_post,False)

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
        # Get user ID for audit trail
        if g is not None:
            if 'username' in g:
                id_user = utils.get_username_id(g.username)
            else:
                id_user = None
        else:
            id_user = None
        
        logger_config.logger.info("Starting full sync of all entities...")
        logger_config.logger.debug(f"id_user: {id_user}")
        
        # Initialize results tracking
        results = {}
        total_success = 0
        total_errors = 0

        logger_config.logger.info("Syncing fuero/DOMINIOS...")
        try:
            success_count, error_count = full_sync.full_sync_dominios(id_user)
            results['fuero'] = {"status": "completed", "success": True, "success_count": success_count, "error_count": error_count}
            total_success += 1
        except Exception as e:
            print(traceback.format_exc())
            logger_config.logger.error(f"Error syncing fuero: {e}")
            results['fuero'] = {"status": "failed", "error": str(e), "success": False}
            total_errors += 1

        logger_config.logger.info("3. Syncing organismos...")
        try:
            full_sync.full_sync_organismos(id_user)
            results['organismos'] = {"status": "completed", "success": True}
            total_success += 1
        except Exception as e:
            print(traceback.format_exc())
            logger_config.logger.error(f"Error syncing organismos: {e}")
            results['organismos'] = {"status": "failed", "error": str(e), "success": False}
            total_errors += 1
        
        
        # Sync all entities sequentially
        logger_config.logger.info("1. Syncing tipos_tareas...")
        try:
            url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-juzgado/"
            clasificacion="juzgado"
            full_sync.full_sync_tipos_tareas_juzgado(clasificacion, id_user,url_post,False)
            results['tipos_tareas'] = {"status": "completed", "success": True}
            total_success += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing tipos_tareas: {e}")
            results['tipos_tareas'] = {"status": "failed", "error": str(e), "success": False}
            total_errors += 1

         # Sync all entities sequentially
        logger_config.logger.info("1. Syncing subtipos_tareas...")
        try:
            url_post="http://dev-backend.usher.pjm.gob.ar/api/v1/tipo-act-parte/"
            clasificacion="parte"
            full_sync.full_sync_tipos_tareas_parte(clasificacion,id_user,url_post,True)
            results['subtipos_tareas'] = {"status": "completed", "success": True}
            total_success += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing subtipos_tareas: {e}")
            results['subtipos_tareas'] = {"status": "failed", "error": str(e), "success": False}
            total_errors += 1
        
        logger_config.logger.info("2. Syncing usuarios...")
        try:
            full_sync.full_sync_usuarios(id_user)
            results['usuarios'] = {"status": "completed", "success": True}
            total_success += 1
        except Exception as e:
            logger_config.logger.error(f"Error syncing usuarios: {e}")
            results['usuarios'] = {"status": "failed", "error": str(e), "success": False}
            total_errors += 1
        
        
       
        logger_config.logger.info(f"Full sync completed. Total successful: {total_success}, Total failed: {total_errors}")
        
        return {
            "success": True,
            "message": f"Full sync of all entities completed. {total_success} successful, {total_errors} failed.",
            "data": {
                "summary": {
                    "total_success": total_success,
                    "total_errors": total_errors
                },
                "details": results
            }
        }
    
    except Exception as err:
        traceback.print_exc()
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
