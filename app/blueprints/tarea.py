from datetime import date, timedelta
from schemas.schemas import TipoTareaIn, TareaGetIn, TipoTareaOut, TareaIn, TareaOut, TareaCountOut, TareaUsuarioIn, TareaUsuarioOut, TareaIdOut, MsgErrorOut, PageIn, TipoTareaCountOut, TareaCountAllOut, TareaAllOut, TareaPatchIn
from schemas.schemas import SubtipoTareaIn, SubtipoTareaOut, SubtipoTareaCountOut, SubtipoTareaGetIn, SubtipoTareaPatchIn, TipoTareaPatchIn, TareaxGrupoIdOut, TareaHIstoriaUserIdOut, TareaPatchLoteIn, TareaPatchLoteOut, TareaPatchLoteV2Out, TareaPatchLoteV2In, TareaAlertaIn
from models.tarea_model import get_all_tarea, get_all_tarea_detalle, get_all_tipo_tarea, get_tarea_by_id, insert_tipo_tarea, usuarios_tarea, insert_tarea, delete_tarea, insert_usuario_tarea, delete_tipo_tarea, update_tarea, get_tarea_historia_usr_by_id
from models.tarea_model import update_tipo_tarea, update_subtipo_tarea, get_all_subtipo_tarea, insert_subtipo_tarea, delete_subtipo_tarea, update_lote_tareas, get_tarea_grupo, update_lote_tareas_v2, tareas_a_vencer
from common.error_handling import DataError, DataNotFound, ValidationError, UnauthorizedError
from models.alch_model import Usuario, Rol
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from sqlalchemy.orm import scoped_session
from common.usher import get_roles
from common.auth import verify_header
from common.logger_config import logger
import traceback
import uuid
import json
from flask import g
from alchemy_db import db


tarea_b = APIBlueprint('tarea_blueprint', __name__)


#################Before requests ##################
@tarea_b.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
    jsonHeader = verify_header()
    
    if jsonHeader is None:
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin
     

######################Control de acceso######################
def control_rol_usuario(token='', nombre_usuario=None, rol='', url_api=''):
    #session: scoped_session = current_app.session



# .d8888. d888888b db      db    db d888888b  .d8b. 
# 88'  YP   `88'   88      88    88   `88'   d8' `8b
# `8bo.      88    88      Y8    8P    88    88ooo88
#   `Y8b.    88    88      `8b  d8'    88    88~~~88
# db   8D   .88.   88booo.  `8bd8'    .88.   88   88
# `8888Y' Y888888P Y88888P    YP    Y888888P YP   YP

#review the possibility of running two or more queries at once. for example session.query(Usuario).filter(Usuario.email == nombre_usuario).first() and session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now()).all() in a SINGLE JOIN?
#this is to save time and compensate for network latency
    #tiempo_vencimiento = timedelta(minutes=30)
    tiempo_vencimiento = timedelta(days=360)
    query_usr = db.session.query(Usuario).filter(Usuario.email == nombre_usuario).first()
    if query_usr is None:
        logger.error("Usuario no encontrado")
        return False
    else:
        id_usuario = query_usr.id
        email = query_usr.email
        query_rol = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now()).all()
        if len(query_rol)==0:
            #######Consultar CU Api Usher##########
            roles = get_roles(token)
            for r in roles['lista_roles_cus']:
                for cu in r['casos_de_uso']:
                    match cu['descripcion_corta_cu']:
                        case 'crear-tarea':
                            urlCU='post/tarea'
                        case 'borrar-tarea':
                            urlCU='delete/tarea'
                        case 'consulta-tarea':
                            urlCU='get/tarea'
                        case 'asignar-tarea':
                            urlCU='post/tarea'
                        case 'crear-grupo':
                            urlCU='post/grupo'
                        case 'crear-usuario':
                            urlCU='post/usuario'
                        case 'modificar-usuario':
                            urlCU='patch/usuario'
                        case 'eliminar-tipo-tarea':
                            urlCU='delete/tipo_tarea'
                        case 'consulta_usuarios_tarea':
                            urlCU='get/usuario_tarea'
                        case 'consulta_tarea_id':
                            urlCU='get/tarea'
                        case 'consulta_tareas_usuario':
                            urlCU='get/tarea'
                        case 'consulta_tareas_grupo':
                            urlCU='get/tarea'
                        case 'consulta_tareas_expediente':
                            urlCU='get/tarea'
                        case 'consulta_tareas_tipo':
                            urlCU='get/tipo_tarea'
                        case 'eliminar-datos':
                            urlCU='delete/tarea'
                        case 'modificar-datos':
                            urlCU='patch/tarea'  

                    nuevoIDRol=uuid.uuid4()
                    nuevo_rol = Rol(
                        id=nuevoIDRol, 
                        email=email,
                        id_usuario=id_usuario, 
                        fecha_actualizacion=datetime.now(),
                        rol=r['descripcion_rol'],
                        id_rol_ext=r['id_usuario_sistema_rol'],
                        descripcion_ext=cu['descripcion_corta_cu'],
                        url_api=urlCU
                    )
                    db.session.add(nuevo_rol)
                    db.session.commit()
                    print("Nuevo Rol Guardado:",nuevo_rol.id)
                
            db.session.commit()
            
        query_permisos = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), Rol.url_api.like(f"%{url_api}%")).all()
        
        if len(query_permisos)==0:
            logger.error("No tiene permisos")
            return False
        else:
            #print("#"*50)
            #print("Roles de tareas:")
            #for permiso in query_rol:
            #    print(f" Email: {permiso.email}, URL API: {permiso.url_api}")
            
            #print("#"*50)
            return True
            
    

    
####################TIPO DE TAREA######################
@tarea_b.doc(description='Consulta de Tipos de Tarea', summary='Tipos de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tarea')
@tarea_b.output(TipoTareaCountOut)
@tarea_b.input(PageIn, location='query')
def get_tipoTareas(query_data: dict):
    try:
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = get_all_tipo_tarea(page,per_page)
    
        
        data = {
                "count": cant,
                "data": TipoTareaOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Tipos de Tarea', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(TipoTareaIn)
def post_tipo_tarea(json_data: dict):
    try:
        username = g.username
        res = insert_tipo_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert de tipo de tarea",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return TipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Modificación de un Tipos de Tarea', summary='Modificación de un Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/tipo_tarea/<string:tipo_tarea_id>')
@tarea_b.input(TipoTareaPatchIn)
def update_tipotarea(tipo_tarea_id:str,json_data: dict):
    try:
        username=g.username
        res = update_tipo_tarea(username, tipo_tarea_id,**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en modificación de tipo de tarea",
                    "error_description":"No se pudo modificar el tipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return TipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  
    
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        username=g.username
        res = delete_tipo_tarea(username, id)
        if res is None:
            raise DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    

    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    
###############################SUBTIPO_TAREA################################
@tarea_b.doc(description='Consulta de Subtipos de Tareas', summary='Subtipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/subtipo_tarea')
@tarea_b.output(SubtipoTareaCountOut)
@tarea_b.input(SubtipoTareaGetIn, location='query')
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

        res, cant = get_all_subtipo_tarea(page,per_page,id_tipo_tarea, eliminado)
        
        data = {
                "count": cant,
                "data": SubtipoTareaOut().dump(res, many=True)
            }
        
        
        return data
    
   
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    
 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Subtipos de Tarea', summary='Alta de Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/subtipo_tarea')
@tarea_b.input(SubtipoTareaIn)
def post_subtipo_tarea(json_data: dict):
    try:
        username=g.username
        res = insert_subtipo_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert subtipo de tarea",
                    "error_description":"No se pudo insertar el subtipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return SubtipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Modificación de un Subtipos de Tarea', summary='Modificación de un Subtipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.patch('/subtipo_tarea/<string:subtipo_id>')
@tarea_b.input(SubtipoTareaPatchIn)
def update_subtipotarea(subtipo_id:str,json_data: dict):
    try:
        username = g.username
        res = update_subtipo_tarea(username, subtipo_id,**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en modificar subtipo de tarea",
                    "error_description":"No se pudo modificar el subtipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        return SubtipoTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Subtipo de Tarea', summary='Baja de subtipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/subtipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
def del_subtipo_tarea(id: str):
    try:
        username=g.username
        res = delete_subtipo_tarea(username, id)
        if res is None:
            raise DataNotFound("Subtipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id subtipo de tarea": id,
                    "Subtipo de tarea": res.nombre
                } 
        
        return result
 
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
        
################################TAREAS################################
#@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea con notas', summary='Consulta de tareas con notas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/tarea_notas')
@tarea_b.input(TareaGetIn, location='query')
@tarea_b.output(TareaCountOut)
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
        cant=0
        titulo=""
        id_expediente=None
        id_actuacion=None
        prioridad=0
        estado = 0
        eliminado=None
        tiene_notas=None
        id_tarea=None
        id_tipo_tarea=None
        id_usuario_asignado=None
        id_grupo=None
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_usuario_asignado') is not None):
            id_usuario_asignado=request.args.get('id_usuario_asignado')   
        if(request.args.get('id_grupo') is not None):
            id_grupo=request.args.get('id_grupo')      
        if(request.args.get('titulo') is not None):
            titulo=request.args.get('titulo')
        if(request.args.get('id_tarea') is not None):
            id_tarea=request.args.get('id_tarea')     
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea') 
        if(request.args.get('id_expediente') is not None):
            id_expediente=request.args.get('id_expediente')
        if(request.args.get('id_actuacion') is not None):
            id_actuacion=request.args.get('id_actuacion')    
        if(request.args.get('prioridad') is not None):
            prioridad=int(request.args.get('prioridad'))  
        if(request.args.get('estado') is not None):
            estado=int(request.args.get('estado'))    
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado') 
        if(request.args.get('tiene_notas') is not None):
            tiene_notas=request.args.get('tiene_notas')               
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
            fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')
            fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)  
 
        res,cant = get_all_tarea(page,per_page, titulo, id_expediente, id_actuacion, id_tipo_tarea, id_tarea, id_usuario_asignado, id_grupo, fecha_desde, fecha_hasta, prioridad, estado, eliminado, tiene_notas)    

        data = {
                "count": cant,
                "data": TareaOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 


@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tareas', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
#@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea')
@tarea_b.input(TareaGetIn, location='query')
@tarea_b.output(TareaCountAllOut)
def get_tareas_detalle(query_data: dict):
    try:
        print("ENTRANDO A GET TAREAS")
        ##########ROLES - REVEER ####################
        #token='eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJsTVhjMjlEdmFtdEZhZ2tiUWoxQ2Fib1pqSk9OY1lxTE5teE1CWERIZmx3In0.eyJleHAiOjE3MjcyNjMzOTEsImlhdCI6MTcyNTk2OTA1OCwiYXV0aF90aW1lIjoxNzI1OTY3MzkxLCJqdGkiOiJhZDU5MzlhNS03NjkwLTQwNmUtYmZiMi1hNWM1OTMzZTg1MzciLCJpc3MiOiJodHRwczovL2Rldi1hdXRoLnBqbS5nb2IuYXIvYXV0aC9yZWFsbXMvZGV2b3BzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5MWFiOTA5LTMzNzQtNDU2YS04Y2U5LTdiZDJkZjExOWQwYSIsInR5cCI6IkJlYXJlciIsImF6cCI6InVzaGVyIiwibm9uY2UiOiI2MGE5ZGRlZS01ZGY3LTQxNjYtYjk3Ny0zMTBhZDk1MWI3NmIiLCJzZXNzaW9uX3N0YXRlIjoiYTFiMDA2NWQtMzhiOC00YTFmLTk2YzAtMTg0NmU0MzliY2VjIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ1c2hlciI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImExYjAwNjVkLTM4YjgtNGExZi05NmMwLTE4NDZlNDM5YmNlYyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlNpbHZpYSBTLiBJbXBlcmlhbGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzaW1wZXJpYWxlIiwiZ2l2ZW5fbmFtZSI6IlNpbHZpYSBTLiIsImZhbWlseV9uYW1lIjoiSW1wZXJpYWxlIiwiZW1haWwiOiJzaW1wZXJpYWxlQG1haWwuanVzLm1lbmRvemEuZ292LmFyIn0.OnfYhSdrZfz7bL6r1sy3-6DCTeFH8G7VesMbGWh4XGCiFM2IuqpXldrjlhKWI8ahRTKAJEdvXlBn8ht5JtGY1y-ee8RbeVrxtmjmmBHJt-nejXNflhsoXcF_20r3rMyfvM210vtFaUy26YZi7ttIBS6mQaql4Y_DPgL_wAMVoa431ThaDw3Kijcl7nJQ40fBeti0YgiwS3KKvEamf8E-CbX1gCUNoZX_pyP4dWSh9kduNh_K0QU4uqyvVzwyt8_jikcPxWmHQ9SHh31M5_31b6uEgSXx7QqKECs-VzH4GnkdZB3TwRb7fnj0D4jSuSvuUp5Wk_lPcrdNMDX4RxA84w'
        #nombre_usuario='simperiale@mail.jus.mendoza.gov.ar'
        #url_api='get/tarea'
        #rol='administrador'
        #accede = control_rol_usuario(token, nombre_usuario, rol, url_api)
        #accede = True
        #if accede is False:
        #   raise DataError(800, "No tiene permisos para acceder a la API")
        #############################################################
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        titulo=""
        label=""
        id_expediente=None
        id_actuacion=None
        prioridad=0
        estado = 0
        eliminado=None
        tiene_notas=None
        id_tipo_tarea=None
        id_usuario_asignado=None
        id_grupo=None
        grupos=None
        id_tarea=None
        fecha_desde=datetime.strptime("30/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()
        fecha_fin_desde=None
        fecha_fin_hasta=None
        labels=None
        grupos = None

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_tarea') is not None):
            id_tarea=request.args.get('id_tarea')    
        if(request.args.get('id_usuario_asignado') is not None):
            id_usuario_asignado=request.args.get('id_usuario_asignado')   
        if(request.args.get('id_grupo') is not None):
            id_grupo=request.args.get('id_grupo')      
        if(request.args.get('titulo') is not ''):
            titulo=request.args.get('titulo')
        if(request.args.get('label') is not ''):
            label=request.args.get('label')
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea') 
        if(request.args.get('id_expediente') is not None):
            id_expediente=request.args.get('id_expediente')
        if(request.args.get('id_actuacion') is not None):
            id_actuacion=request.args.get('id_actuacion')    
        if(request.args.get('prioridad') is not None):
            prioridad=int(request.args.get('prioridad')) 
        if(request.args.get('estado') is not None):
            estado=int(request.args.get('estado'))    
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')   
        if(request.args.get('tiene_notas') is not None):
            tiene_notas=request.args.get('tiene_notas')            
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
            fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')
            fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)  
        if(request.args.get('fecha_fin_desde') is not None):
            fecha_fin_desde=request.args.get('fecha_fin_desde')
            fecha_fin_desde = datetime.strptime(fecha_fin_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        if(request.args.get('fecha_fin_hasta') is not None):
            fecha_fin_hasta=request.args.get('fecha_fin_hasta')
            fecha_fin_hasta = datetime.strptime(fecha_fin_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)  
        if(request.args.get('labels') is not None):
            labels=request.args.get('labels')
            labels = labels.split(",")
            print("Labels:",labels)
        if(request.args.get('grupos') is not None):
            grupos=request.args.get('grupos')
            grupos = grupos.split(",")
            print("Grupo:",grupos)    
        print("right before the get_all_tarea_detalle call")
        res,cant = get_all_tarea_detalle(page,per_page, titulo, label, labels, id_expediente, id_actuacion, id_tipo_tarea, id_usuario_asignado, id_grupo, grupos, id_tarea, fecha_desde, fecha_hasta, fecha_fin_desde, fecha_fin_hasta, prioridad, estado, eliminado, tiene_notas)    

        data = {
                "count": cant,
                "data": TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_detalle/<string:id_tarea>')
@tarea_b.output(TareaIdOut(many=True))
def get_tarea(id_tarea:str):
    try:
        res = get_tarea_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise DataNotFound("Tarea no encontrada")

        
        return res

    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 

@tarea_b.doc(description='Consulta de usuarios x tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_historia_usr/<string:id_tarea>')
@tarea_b.output(TareaHIstoriaUserIdOut(many=True))
def get_tarea_historia_usr(id_tarea:str):
    try:
        res = get_tarea_historia_usr_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise DataNotFound("Tarea no encontrada")

        
        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de tarea por ID de grupo', summary='Tarea por Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
#@tarea_b.get('/tarea_grupo/<string:id_grupo>')
@tarea_b.get('/tarea_grupo')
@tarea_b.output(TareaCountAllOut)
#def get_tarea_grupo(id_grupo:str):
def get_tareas_grupo():    
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        username = g.get('username')
        #username ='simperiale@ju.mendoza.gov.ar'
        #res, cant = get_tarea_grupo_by_id(username, page, per_page) 
        res, cant = get_tarea_grupo(username, page, per_page)
        
        data = {
                "count": cant,
                "data": TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)     

@tarea_b.doc(description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/usuario_tarea/<string:tarea_id>')
@tarea_b.output(TareaUsuarioOut(many=True))
def get_usuarios_asignados(tarea_id:str):
    try:    
        res = usuarios_tarea(tarea_id)

        return res

    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)

#@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Asignación de tarea a usuario', summary='Asignación a usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
#@tarea_b.post('/tarea_usr')
#@tarea_b.input(TareaUsuarioIn)
#@tarea_b.output(TareaOut)
def post_usuario_tarea(json_data: dict):
    try:
        username = g.get('username')
        res, msg = insert_usuario_tarea(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error_description":"Error en insert usuario_tarea",
                    "error":msg
                } 
            res = MsgErrorOut().dump(result)
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
        raise ValidationError(err)    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Tarea', summary='Update de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/tarea/<string:tarea_id>')
@tarea_b.input(TareaPatchIn)
#@usuario_b.output(UsuarioOut)
def patch_tarea(tarea_id: str, json_data: dict):
    try:
        username = g.get('username')

        res = update_tarea(tarea_id, username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        return TareaAllOut().dump(res)    
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas')
@tarea_b.input(TareaPatchLoteIn)
def patch_lote_tareas(json_data: dict):
    try:
        username = g.get('username')
   
        res = update_lote_tareas(username, **json_data)
        
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        
        return TareaPatchLoteOut().dump(res)    
        
     
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)

################V2 LOTE TAREAS####################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de Lote de Tareas', summary='Update de Lote de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.patch('/lote_tareas_v2')
@tarea_b.input(TareaPatchLoteV2In)
def patch_lote_tareasv2(json_data: dict):
    try:
        username = g.get('username')

        res = update_lote_tareas_v2(username, **json_data)
        
        
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a modificar"
                } 
            return result
        
        return TareaPatchLoteV2Out().dump(res)    
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    

@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.post('/tarea')
@tarea_b.input(TareaIn)
@tarea_b.output(TareaOut)
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
            res = insert_tarea(**json_data)
        else:    
            if type_header == 'JWT':
                logger.info("JWT ORIGIN")
                res = insert_tarea(username, **json_data)
            else:
                #Esto es para probar sin header - no debería pasar - sacarlo en produccion
                logger.info("NO HEADER ORIGIN")
                raise ValidationError(800, "No tiene permisos para acceder a la API")
                #res = insert_tarea(**json_data)    
      
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert tarea",
                    "error_description": "No se pudo insertar la tarea"
                }
            res = MsgErrorOut().dump(result)
        print("*"*50)
        print("Tarea insertada:", TareaOut().dump(res))
        return TareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    

#################DELETE########################
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tarea', summary='Baja de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.delete('/tarea/<string:id>')
def del_tarea(id: str):
    try:
        username=g.get('username')
        res = delete_tarea(username, id)
        if res is None:
           raise DataNotFound("Tarea no encontrada")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    
    
    
@tarea_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Listado de Tareas a vencer', summary='Tareas a vencer', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@tarea_b.get('/alertas')
@tarea_b.input(TareaAlertaIn, location='query')
@tarea_b.output(TareaCountAllOut)
def get_alerta_tarea(query_data: dict):
    try:
        dias_aviso=15
        cant=0
        username=g.get('username')
        if(request.args.get('dias_aviso') is not None):
            dias_aviso=int(request.args.get('dias_aviso'))
        logger.info("Tareas a vencer")
        res, cant = tareas_a_vencer(username, dias_aviso)
        data = {
                "count": cant,
                "data": TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)        
