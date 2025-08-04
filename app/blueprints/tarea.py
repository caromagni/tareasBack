import schemas.schemas as schema
import models.tarea_model as tarea_model
import common.error_handling as error_handling
import common.exceptions as exceptions
import decorators.role as rol
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app
from common.cache import *




tarea_b = APIBlueprint('tarea_blueprint', __name__)


#################Before requests ##################
@tarea_b.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')
     
    
####################TIPO DE TAREA######################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de Tipos de Tarea', summary='Tipos de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tarea')
@tarea_b.output(schema.TipoTareaSubtipoCountOut)
@tarea_b.input(schema.TipoTareaGetIn, location='query')
@rol.require_role()
def get_tipoTareas(query_data: dict):
    try:
        user_name = g.username
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nivel=None
        origen_externo=None
        suspendido=None
        eliminado=None
        nombre=None

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if (request.args.get('nivel') is not None):
            nivel=request.args.get('nivel')
        if (request.args.get('origen_externo') is not None):
            origen_externo=request.args.get('origen_externo') 
        if (request.args.get('suspendido') is not None):
            suspendido = request.args.get('suspendido')
        if (request.args.get('eliminado') is not None):
            eliminado = request.args.get('eliminado')
        if (request.args.get('nombre') is not None):
            nombre = request.args.get('nombre')    

        res, cant = tarea_model.get_all_tipo_tarea(page,per_page, nivel, origen_externo, suspendido, eliminado, nombre)
    
        
        data = {
                "count": cant,
                "data": schema.TipoTareaSubtipoOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Alta de un nuevo Tipos de Tarea', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(schema.TipoTareaIn)
@rol.require_role()
def post_tipo_tarea(json_data: dict):
    try:
        username = g.username
        res = tarea_model.insert_tipo_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert de tipo de tarea",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
        
        
        return schema.TipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)  
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Modificación de un Tipos de Tarea', summary='Modificación de un Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/tipo_tarea/<string:tipo_tarea_id>')
@tarea_b.input(schema.TipoTareaPatchIn)
@rol.require_role()
def update_tipotarea(tipo_tarea_id:str,json_data: dict):
    try:
        username=g.username
        res = tarea_model.update_tipo_tarea(username, tipo_tarea_id,**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en modificación de tipo de tarea",
                    "error_description":"No se pudo modificar el tipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
        
        
        return schema.TipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)  
    
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
@rol.require_role()
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        username=g.username
        res = tarea_model.delete_tipo_tarea(username, id)
        if res is None:
            raise exceptions.DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    

    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)
    
###############################SUBTIPO_TAREA################################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de Subtipos de Tareas', summary='Subtipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/subtipo_tarea')
@tarea_b.output(schema.SubtipoTareaCountOut)
@tarea_b.input(schema.SubtipoTareaGetIn, location='query')
@rol.require_role()
def get_subtipoTarea(query_data: dict):
    try:
        cant=0
        page=1
        id_tipo_tarea=None
        eliminado=None
        suspendido=None
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea')
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')
        if(request.args.get('suspendido') is not None):
            suspendido = request.args.get('suspendido')    

        #print("id_tipo_tarea:",id_tipo_tarea)

        res, cant = tarea_model.get_all_subtipo_tarea(page, per_page, id_tipo_tarea, eliminado, suspendido)
        
        data = {
                "count": cant,
                "data": schema.SubtipoTareaOut().dump(res, many=True)
            }
        
        
        return data
    
   
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Alta de un nuevo Subtipos de Tarea', summary='Alta de Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/subtipo_tarea')
@tarea_b.input(schema.SubtipoTareaIn)
@rol.require_role()
def post_subtipo_tarea(json_data: dict):
    try:
        username=g.username
        res = tarea_model.insert_subtipo_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert subtipo de tarea",
                    "error_description":"No se pudo insertar el subtipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
        
        
        return schema.SubtipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)  

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Modificación de un Subtipos de Tarea', summary='Modificación de un Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/subtipo_tarea/<string:subtipo_id>')
@tarea_b.input(schema.SubtipoTareaPatchIn)
@rol.require_role()
def update_subtipotarea(subtipo_id:str,json_data: dict):
    try:
        username = g.username
        res = tarea_model.update_subtipo_tarea(username, subtipo_id,**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en modificar subtipo de tarea",
                    "error_description":"No se pudo modificar el subtipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
        
        return schema.SubtipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Baja de Subtipo de Tarea', summary='Baja de subtipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/subtipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
@rol.require_role()
def del_subtipo_tarea(id: str):
    try:
        username=g.username
        res = tarea_model.delete_subtipo_tarea(username, id)
        if res is None:
            raise exceptions.DataNotFound("Subtipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id subtipo de tarea": id,
                    "Subtipo de tarea": res.nombre
                } 
        
        return result
 
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)
        
################################TAREAS################################
#@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de tarea con notas', summary='Consulta de tareas con notas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/tarea_notas')
@tarea_b.input(schema.TareaNotasGetIn, location='query')
@tarea_b.output(schema.TareaCountOut)
@rol.require_role()
def get_tareas(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        prioridad=None
        estado=None
        cant=0
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        titulo=request.args.get('titulo')
        id_expediente=request.args.get('id_expediente')
        id_actuacion=request.args.get('id_actuacion')
        if(request.args.get('prioridad') is not None):
            prioridad=int(request.args.get('prioridad'))
        if(request.args.get('estado') is not None):
            estado = int(request.args.get('estado'))    
        eliminado=request.args.get('eliminado')
        id_tipo_tarea=request.args.get('id_tipo_tarea')
        id_usuario_asignado=request.args.get('id_usuario_asignado')
        id_tarea=request.args.get('id_tarea')
        fecha_desde=request.args.get('fecha_desde')
        fecha_hasta=request.args.get('fecha_hasta')
        tiene_notas=request.args.get('tiene_notas')
        print("right before the get_all_tarea_detalle call")
        print("Id tarea:",id_tarea)
        res,cant = tarea_model.get_all_tarea(page,per_page, titulo, id_expediente, id_actuacion, id_tipo_tarea, id_usuario_asignado, id_tarea, fecha_desde, fecha_hasta, prioridad, estado, eliminado, tiene_notas)    
        data = {
                "count": cant,
                "data": schema.TareaOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 



@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de tareas', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/tarea')
@tarea_b.input(schema.TareaGetIn, location='query')
@tarea_b.output(schema.TareaCountAllOut)
@rol.require_role()
def get_tareas_detalle(query_data: dict):
    try:
        print("ENTRANDO A GET TAREAS")
        username = g.get('username')
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        prioridad=None
        estado=None
        cant=0
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        titulo=request.args.get('titulo')
        label=request.args.get('label')
        id_expediente=request.args.get('id_expediente')
        id_expte_ext = request.args.get('id_expte_ext')
        id_actuacion=request.args.get('id_actuacion')
        id_actuacion_ext = request.args.get('id_actuacion_ext')
        if(request.args.get('prioridad') is not None):
            prioridad=int(request.args.get('prioridad'))
        if(request.args.get('estado') is not None):
            estado = int(request.args.get('estado'))    
        eliminado=request.args.get('eliminado')
        id_tipo_tarea=request.args.get('id_tipo_tarea')
        id_usuario_asignado=request.args.get('id_usuario_asignado')
        grupos=request.args.get('grupos')
        labels=request.args.get('labels')
        id_tarea=request.args.get('id_tarea')
        fecha_desde=request.args.get('fecha_desde')
        fecha_hasta=request.args.get('fecha_hasta')
        fecha_fin_desde=request.args.get('fecha_fin_desde')
        fecha_fin_hasta=request.args.get('fecha_fin_hasta')
        tiene_notas=request.args.get('tiene_notas')
        res,cant = tarea_model.get_all_tarea_detalle(username, page,per_page, titulo, label, labels, id_expediente, id_expte_ext, id_actuacion, id_actuacion_ext, id_tipo_tarea, id_usuario_asignado, grupos, id_tarea, fecha_desde, fecha_hasta, fecha_fin_desde, fecha_fin_hasta, prioridad, estado, eliminado, tiene_notas)    
        # res,cant = tarea_model.get_all_tarea_detalle(page)    

        data = {
                "count": cant,
                "data": schema.TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_detalle/<string:id_tarea>')
@tarea_b.output(schema.TareaIdOut(many=True))
@rol.require_role()
def get_tarea(id_tarea:str):
    try:
        res = tarea_model.get_tarea_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise exceptions.DataNotFound("Tarea no encontrada")

        
        return res

    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}],description='Consulta de usuarios x tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_historia_usr/<string:id_tarea>')
@tarea_b.output(schema.TareaHIstoriaUserIdOut(many=True))
@rol.require_role()
def get_tarea_historia_usr(id_tarea:str):
    try:
        res = tarea_model.get_tarea_historia_usr_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise exceptions.DataNotFound("Tarea no encontrada")

        
        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de tarea por ID de grupo', summary='Tarea por Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_grupo')
@tarea_b.output(schema.TareaCountAllOut)
@rol.require_role()
def get_tareas_grupo():    
    try:
        logger.info("ENTRANDO A GET TAREAS GRUPO")
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        username = g.get('username')
        #username ='simperiale@ju.mendoza.gov.ar'
        #res, cant = get_tarea_grupo_by_id(username, page, per_page) 
        res, cant = tarea_model.get_tarea_grupo(username, page, per_page)
        
        data = {
                "count": cant,
                "data": schema.TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)     

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/usuario_tarea/<string:tarea_id>')
@tarea_b.output(schema.TareaUsuarioOut(many=True))
@rol.require_role()
def get_usuarios_asignados(tarea_id:str):
    try:    
        res = tarea_model.usuarios_tarea(tarea_id)

        return res

    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

#@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Asignación de tarea a usuario', summary='Asignación a usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
#@tarea_b.post('/tarea_usr')
#@tarea_b.input(TareaUsuarioIn)
#@tarea_b.output(TareaOut)
def post_usuario_tarea(json_data: dict):
    try:
        username = g.get('username')
        res, msg = tarea_model.insert_usuario_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error_description":"Error en insert usuario_tarea",
                    "error":msg
                } 
            res = schema.MsgErrorOut().dump(result)
            return res

        result={
                    "valido":"true",
                    "id_usuario": res.id_usuario,
                    "id_tarea": res.id_tarea,
                    "Msg":"Tarea asignada"
                } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Update de Tarea', summary='Update de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/tarea/<string:tarea_id>')
@tarea_b.input(schema.TareaPatchIn)
@rol.require_role()
def patch_tarea(tarea_id: str, json_data: dict):
    try:
        username = g.get('username')

        res = tarea_model.update_tarea(tarea_id, username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        return schema.TareaPatchAllOut().dump(res)    
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas')
@tarea_b.input(schema.TareaPatchLoteIn)
@rol.require_role()
def patch_lote_tareas(json_data: dict):
    try:
        username = g.get('username')
   
        res = tarea_model.update_lote_tareas(username, **json_data)
        
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        
        return schema.TareaPatchLoteOut().dump(res)    
        
     
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

################V2 LOTE TAREAS####################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas_v2')
@tarea_b.input(schema.TareaPatchLoteV2In)
@rol.require_role()
def patch_lote_tareasv2(json_data: dict):
    try:
        username = g.get('username')

        res = tarea_model.update_lote_tareas_v2(username, **json_data)
        
        
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        
        return schema.TareaPatchLoteV2Out().dump(res)    
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.post('/tarea')
@tarea_b.input(schema.TareaIn)
@tarea_b.output(schema.TareaOut)
@rol.require_role()
def post_tarea(json_data: dict):
    try:
        print("#"*50)
        print("Inserta tarea")
        print(json_data)
        print("**** G OBJECT *****")
        username = g.get('username')
        type_header = g.get('type')
        
        if type_header == 'api_key':
            logger.info("API KEY ORIGIN")
            res = tarea_model.insert_tarea(**json_data)
        else:    
            if type_header == 'JWT':
                logger.info("JWT ORIGIN")
                res = tarea_model.insert_tarea(username, **json_data)
            else:
                #Esto es para probar sin header - no debería pasar - sacarlo en produccion
                logger.info("NO HEADER ORIGIN")
                raise exceptions.ValidationError(800, "No tiene permisos  para acceder a la API")
                #res = insert_tarea(**json_data)    
      
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert tarea",
                    "error_description": "No se pudo insertar la tarea"
                }
            res = schema.MsgErrorOut().dump(result)
        print("*"*50)
        print("Tarea insertada:", schema.TareaOut().dump(res))
        return schema.TareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)    

#################DELETE########################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Baja de Tarea', summary='Baja de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.delete('/tarea/<string:id>')
@rol.require_role()
def del_tarea(id: str):
    try:
        username=g.get('username')
        res = tarea_model.delete_tarea(username, id)
        if res is None:
           raise exceptions.DataNotFound("Tarea no encontrada")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)    
    
