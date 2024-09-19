from datetime import date, timedelta
from ..schemas.schemas import TipoTareaIn, TareaGetIn, TipoTareaOut, TareaIn, TareaOut, TareaCountOut, TareaUsuarioIn, TareaUsuarioOut, TareaIdOut, MsgErrorOut, PageIn, TipoTareaCountOut
from ..models.tarea_model import get_all_tarea, get_all_tipo_tarea, get_tarea_by_id, insert_tipo_tarea, usuarios_tarea, insert_tarea, delete_tarea, insert_usuario_tarea, delete_tipo_tarea
from app.common.error_handling import DataError, DataNotFound, ValidationError
from ..models.alch_model import Usuario, Rol
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from sqlalchemy.orm import scoped_session
from ..common.usher import get_roles
import uuid
import json

tarea_b = APIBlueprint('tarea_blueprint', __name__)
###############
@tarea_b.before_request
def before_request():
    print("Antes de la petición")
    print(request.headers)

######################Control de acceso######################
def control_rol_usuario(token='', nombre_usuario='', rol='', url_api=''):
    session: scoped_session = current_app.session

    tiempo_vencimiento = timedelta(minutes=30)
    query_usr = session.query(Usuario).filter(Usuario.email == nombre_usuario).first()
    if query_usr is None:
        print("Usuario no encontrado")
        return False
    else:
        id_usuario = query_usr.id
        email = query_usr.email
        query_rol = session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now()).all()
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
                        case 'consulta_usuario_tarea':
                            urlCU='get/tarea_usr'
                        case 'alta_usuario_tarea':
                            urlCU='post/tarea_usr'
                        case 'consulta_usuarios_tarea':
                            urlCU='get/tarea_usr'
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
                    session.add(nuevo_rol)
                    session.commit()
                    print("Nuevo Rol Guardado:",nuevo_rol.id)
                
            session.commit()
            
        query_permisos = session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), Rol.url_api.like(f"%{url_api}%")).all()
        
        if len(query_permisos)==0:
            print("No tiene permisos")
            return False
        else:
            print("Roles de tareas:",query_rol)
            return True
            
    

    
####################TIPO DE TAREA######################
@tarea_b.doc(description='Consulta de Tipos de Tareas', summary='Tipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
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
        
        current_app.session.remove()
        return data
    
   
    except Exception as err:
        raise ValidationError(err)    
 

@tarea_b.doc(description='Alta de un nuevo Tipos de Tareas', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(TipoTareaIn)
def post_tipo_tarea(json_data: dict):
    try:
    
        res = insert_tipo_tarea(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return TipoTareaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)  

@tarea_b.doc(description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        res = delete_tipo_tarea(id)
        if res is None:
            raise DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)
    
################################TAREAS################################
@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea')
@tarea_b.input(TareaGetIn, location='query')
@tarea_b.output(TareaCountOut)
def get_tareas(query_data: dict):
    try:
        ##########Variables de control de acceso####################
        token='eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJsTVhjMjlEdmFtdEZhZ2tiUWoxQ2Fib1pqSk9OY1lxTE5teE1CWERIZmx3In0.eyJleHAiOjE3MjcyNjMzOTEsImlhdCI6MTcyNTk2OTA1OCwiYXV0aF90aW1lIjoxNzI1OTY3MzkxLCJqdGkiOiJhZDU5MzlhNS03NjkwLTQwNmUtYmZiMi1hNWM1OTMzZTg1MzciLCJpc3MiOiJodHRwczovL2Rldi1hdXRoLnBqbS5nb2IuYXIvYXV0aC9yZWFsbXMvZGV2b3BzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5MWFiOTA5LTMzNzQtNDU2YS04Y2U5LTdiZDJkZjExOWQwYSIsInR5cCI6IkJlYXJlciIsImF6cCI6InVzaGVyIiwibm9uY2UiOiI2MGE5ZGRlZS01ZGY3LTQxNjYtYjk3Ny0zMTBhZDk1MWI3NmIiLCJzZXNzaW9uX3N0YXRlIjoiYTFiMDA2NWQtMzhiOC00YTFmLTk2YzAtMTg0NmU0MzliY2VjIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ1c2hlciI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImExYjAwNjVkLTM4YjgtNGExZi05NmMwLTE4NDZlNDM5YmNlYyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlNpbHZpYSBTLiBJbXBlcmlhbGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzaW1wZXJpYWxlIiwiZ2l2ZW5fbmFtZSI6IlNpbHZpYSBTLiIsImZhbWlseV9uYW1lIjoiSW1wZXJpYWxlIiwiZW1haWwiOiJzaW1wZXJpYWxlQG1haWwuanVzLm1lbmRvemEuZ292LmFyIn0.OnfYhSdrZfz7bL6r1sy3-6DCTeFH8G7VesMbGWh4XGCiFM2IuqpXldrjlhKWI8ahRTKAJEdvXlBn8ht5JtGY1y-ee8RbeVrxtmjmmBHJt-nejXNflhsoXcF_20r3rMyfvM210vtFaUy26YZi7ttIBS6mQaql4Y_DPgL_wAMVoa431ThaDw3Kijcl7nJQ40fBeti0YgiwS3KKvEamf8E-CbX1gCUNoZX_pyP4dWSh9kduNh_K0QU4uqyvVzwyt8_jikcPxWmHQ9SHh31M5_31b6uEgSXx7QqKECs-VzH4GnkdZB3TwRb7fnj0D4jSuSvuUp5Wk_lPcrdNMDX4RxA84w'
        nombre_usuario='simperiale@mail.jus.mendoza.gov.ar'
        url_api='get/tarea'
        rol='administrador'
        #accede = control_rol_usuario(token, nombre_usuario, rol, url_api)
        accede = True
        if accede is False:
            raise DataError(800, "No tiene permisos para acceder a la API")
        #############################################################
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        titulo=""
        id_expediente=None
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
            id_usuario_asignado=request.args.get('id_grupo')      
        if(request.args.get('titulo') is not None):
            titulo=request.args.get('titulo')
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea') 
        if(request.args.get('id_expediente') is not None):
            id_expediente=request.args.get('id_expediente')     
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta') 
        res,cant = get_all_tarea(page,per_page, titulo, id_expediente, id_tipo_tarea, id_usuario_asignado, id_grupo, fecha_desde, fecha_hasta)    

        data = {
                "count": cant,
                "data": TareaOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea/<string:id_tarea>')
@tarea_b.output(TareaIdOut(many=True))
def get_tarea(id_tarea:str):
    try:
        res = get_tarea_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise DataNotFound("Tarea no encontrada")

        current_app.session.remove()
        return res
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_usr/<string:tarea_id>')
@tarea_b.output(TareaUsuarioOut(many=True))
def get_usuarios_asignados(tarea_id:str):
    try:    
        print("Usuarios asignados a tarea:", tarea_id)
        res = usuarios_tarea(tarea_id)

        current_app.session.remove()
        return res

    except Exception as err:
        raise ValidationError(err)

@tarea_b.doc(description='Asignación de tarea a usuario', summary='Asignación a usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tarea_usr')
@tarea_b.input(TareaUsuarioIn)
#@tarea_b.output(TareaOut)
def post_usuario_tarea(json_data: dict):
    try:
    
        res, msg = insert_usuario_tarea(**json_data)
        if res is None:
            print("Tarea ya asignada")
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
        current_app.session.remove()
        return result
    
    except Exception as err:
        raise ValidationError(err)    



@tarea_b.doc(description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tarea')
@tarea_b.input(TareaIn)
@tarea_b.output(TareaOut)
def post_tarea(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        res = insert_tarea(**json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert tarea",
                    "error_description": "No se pudo insertar la tarea"
                }
            res = MsgErrorOut().dump(result)
        
        return TareaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)    

#################DELETE########################
@tarea_b.doc(description='Baja de Tarea', summary='Baja de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tarea/<string:id>')
def del_tarea(id: str):
    try:
        res = delete_tarea(id)
        print("res:",res)
        if res is None:
           raise DataNotFound("Tarea no encontrada")
        else:
            print("Tarea eliminada:", res)
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)    