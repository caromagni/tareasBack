import schemas.schemas as schema
import models.tarea_model as tarea_model
import common.error_handling as error_handling
import decorators.role as rol
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



tarea_b = APIBlueprint('tarea_blueprint', __name__)


#################Before requests ##################
@tarea_b.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
       
    jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin
     


    
####################TIPO DE TAREA######################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de Tipos de Tarea', summary='Tipos de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tarea')
@tarea_b.output(schema.TipoTareaCountOut)
@tarea_b.input(schema.PageIn, location='query')
@rol.require_role("Operador")
def get_tipoTareas(query_data: dict):
    try:
        user_name = g.username
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = tarea_model.get_all_tipo_tarea(page,per_page)
    
        
        data = {
                "count": cant,
                "data": schema.TipoTareaOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Tipos de Tarea', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(schema.TipoTareaIn)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err)  
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Modificación de un Tipos de Tarea', summary='Modificación de un Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/tipo_tarea/<string:tipo_tarea_id>')
@tarea_b.input(schema.TipoTareaPatchIn)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err)  
    
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
@rol.require_role("Operador")
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        username=g.username
        res = tarea_model.delete_tipo_tarea(username, id)
        if res is None:
            raise error_handling.DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
###############################SUBTIPO_TAREA################################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de Subtipos de Tareas', summary='Subtipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/subtipo_tarea')
@tarea_b.output(schema.SubtipoTareaCountOut)
@tarea_b.input(schema.SubtipoTareaGetIn, location='query')
@rol.require_role("Operador")
def get_subtipoTarea(query_data: dict):
    try:
        cant=0
        page=1
        id_tipo_tarea=None
        eliminado=None
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea')
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')

        #print("id_tipo_tarea:",id_tipo_tarea)

        res, cant = tarea_model.get_all_subtipo_tarea(page,per_page,id_tipo_tarea, eliminado)
        
        data = {
                "count": cant,
                "data": schema.SubtipoTareaOut().dump(res, many=True)
            }
        
        
        return data
    
   
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Subtipos de Tarea', summary='Alta de Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/subtipo_tarea')
@tarea_b.input(schema.SubtipoTareaIn)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err)  

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Modificación de un Subtipos de Tarea', summary='Modificación de un Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/subtipo_tarea/<string:subtipo_id>')
@tarea_b.input(schema.SubtipoTareaPatchIn)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Subtipo de Tarea', summary='Baja de subtipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/subtipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
@rol.require_role("Operador")
def del_subtipo_tarea(id: str):
    try:
        username=g.username
        res = tarea_model.delete_subtipo_tarea(username, id)
        if res is None:
            raise error_handling.DataNotFound("Subtipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id subtipo de tarea": id,
                    "Subtipo de tarea": res.nombre
                } 
        
        return result
 
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
        
################################TAREAS################################
#@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea con notas', summary='Consulta de tareas con notas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/tarea_notas')
@tarea_b.input(schema.TareaNotasGetIn, location='query')
@tarea_b.output(schema.TareaCountOut)
@rol.require_role("Operador")
def get_tareas(query_data: dict):
    try:
        ########## ROLES - REVEER ####################
        #token='eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJsTVhjMjlEdmFtdEZhZ2tiUWoxQ2Fib1pqSk9OY1lxTE5teE1CWERIZmx3In0.eyJleHAiOjE3MjcyNjMzOTEsImlhdCI6MTcyNTk2OTA1OCwiYXV0aF90aW1lIjoxNzI1OTY3MzkxLCJqdGkiOiJhZDU5MzlhNS03NjkwLTQwNmUtYmZiMi1hNWM1OTMzZTg1MzciLCJpc3MiOiJodHRwczovL2Rldi1hdXRoLnBqbS5nb2IuYXIvYXV0aC9yZWFsbXMvZGV2b3BzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5MWFiOTA5LTMzNzQtNDU2YS04Y2U5LTdiZDJkZjExOWQwYSIsInR5cCI6IkJlYXJlciIsImF6cCI6InVzaGVyIiwibm9uY2UiOiI2MGE5ZGRlZS01ZGY3LTQxNjYtYjk3Ny0zMTBhZDk1MWI3NmIiLCJzZXNzaW9uX3N0YXRlIjoiYTFiMDA2NWQtMzhiOC00YTFmLTk2YzAtMTg0NmU0MzliY2VjIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ1c2hlciI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImExYjAwNjVkLTM4YjgtNGExZi05NmMwLTE4NDZlNDM5YmNlYyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlNpbHZpYSBTLiBJbXBlcmlhbGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzaW1wZXJpYWxlIiwiZ2l2ZW5fbmFtZSI6IlNpbHZpYSBTLiIsImZhbWlseV9uYW1lIjoiSW1wZXJpYWxlIiwiZW1haWwiOiJzaW1wZXJpYWxlQG1haWwuanVzLm1lbmRvemEuZ292LmFyIn0.OnfYhSdrZfz7bL6r1sy3-6DCTeFH8G7VesMbGWh4XGCiFM2IuqpXldrjlhKWI8ahRTKAJEdvXlBn8ht5JtGY1y-ee8RbeVrxtmjmmBHJt-nejXNflhsoXcF_20r3rMyfvM210vtFaUy26YZi7ttIBS6mQaql4Y_DPgL_wAMVoa431ThaDw3Kijcl7nJQ40fBeti0YgiwS3KKvEamf8E-CbX1gCUNoZX_pyP4dWSh9kduNh_K0QU4uqyvVzwyt8_jikcPxWmHQ9SHh31M5_31b6uEgSXx7QqKECs-VzH4GnkdZB3TwRb7fnj0D4jSuSvuUp5Wk_lPcrdNMDX4RxA84w'
        #nombre_usuario='simperiale@mail.jus.mendoza.gov.ar'
        #url_api='get/tarea'
        #rol='administrador'
        #accede = control_rol_usuario(token, nombre_usuario, rol, url_api)
        #accede = True
        #if accede is False:
        #    raise DataError(800, "No tiene permisos para acceder a la API")
        #############################################################
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
        raise error_handling.ValidationError(err) 


@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tareas', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/tarea')
@tarea_b.input(schema.TareaGetIn, location='query')
@tarea_b.output(schema.TareaCountAllOut)
@rol.require_role("Operador")
def get_tareas_detalle(query_data: dict):
    try:
        print("ENTRANDO A GET TAREAS")
        usuario = g.get('username')
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
        id_actuacion=request.args.get('id_actuacion')
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
        print("right before the get_all_tarea_detalle call")
        res,cant = tarea_model.get_all_tarea_detalle(page,per_page, titulo, label, labels, id_expediente, id_actuacion, id_tipo_tarea, id_usuario_asignado, grupos, id_tarea, fecha_desde, fecha_hasta, fecha_fin_desde, fecha_fin_hasta, prioridad, estado, eliminado, tiene_notas)    

        data = {
                "count": cant,
                "data": schema.TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_detalle/<string:id_tarea>')
@tarea_b.output(schema.TareaIdOut(many=True))
@rol.require_role("Operador")
def get_tarea(id_tarea:str):
    try:
        res = tarea_model.get_tarea_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise error_handling.DataNotFound("Tarea no encontrada")

        
        return res

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}],description='Consulta de usuarios x tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_historia_usr/<string:id_tarea>')
@tarea_b.output(schema.TareaHIstoriaUserIdOut(many=True))
@rol.require_role("Operador")
def get_tarea_historia_usr(id_tarea:str):
    try:
        res = tarea_model.get_tarea_historia_usr_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise error_handling.DataNotFound("Tarea no encontrada")

        
        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea por ID de grupo', summary='Tarea por Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_grupo')
@tarea_b.output(schema.TareaCountAllOut)
@rol.require_role("Operador")
def get_tareas_grupo():    
    try:
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
        raise error_handling.ValidationError(err)     

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/usuario_tarea/<string:tarea_id>')
@tarea_b.output(schema.TareaUsuarioOut(many=True))
@rol.require_role("Operador")
def get_usuarios_asignados(tarea_id:str):
    try:    
        res = tarea_model.usuarios_tarea(tarea_id)

        return res

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)

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
        raise error_handling.ValidationError(err)    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Tarea', summary='Update de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/tarea/<string:tarea_id>')
@tarea_b.input(schema.TareaPatchIn)
@rol.require_role("Operador")
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
        return schema.TareaAllOut().dump(res)    
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas')
@tarea_b.input(schema.TareaPatchLoteIn)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err)

################V2 LOTE TAREAS####################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas_v2')
@tarea_b.input(schema.TareaPatchLoteV2In)
@rol.require_role("Operador")
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
        raise error_handling.ValidationError(err)
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.post('/tarea')
@tarea_b.input(schema.TareaIn)
@tarea_b.output(schema.TareaOut)
@rol.require_role("Operador")
def post_tarea(json_data: dict):
    try:
        print("#"*50)
        print("Inserta tarea")
        print(json_data)
        #Modificado para el Migue - Agregar token
        print("**** G OBJECT *****")
        username = g.get('username')
        type_header = g.get('type')
        
        #if username type is api_key then we must use the username that comes inside the body, with the key "username"
        
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
                raise error_handling.ValidationError(800, "No tiene permisos para acceder a la API")
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
        raise error_handling.ValidationError(err)    

#################DELETE########################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tarea', summary='Baja de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.delete('/tarea/<string:id>')
@rol.require_role("Operador")
def del_tarea(id: str):
    try:
        username=g.get('username')
        res = tarea_model.delete_tarea(username, id)
        if res is None:
           raise error_handling.DataNotFound("Tarea no encontrada")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    
    
