from apiflask import APIBlueprint, HTTPTokenAuth
from common.api_key import *
from flask import request, current_app
from models.grupo_model import get_all_grupos, get_all_base, get_all_grupos_detalle, update_grupo, insert_grupo, get_usuarios_by_grupo, get_grupo_by_id, delete_grupo, get_all_grupos_nivel, undelete_grupo
from common.error_handling import ValidationError, DataError, DataNotFound, UnauthorizedError
from typing import List
from schemas.schemas import GroupIn, GroupPatchIn, GroupOut, GetGroupOut, GetGroupCountOut, GroupCountOut, GroupCountAllOut, GroupGetIn, UsuariosGroupOut, GroupIdOut, GroupAllOut, MsgErrorOut, GroupsBaseOut, GroupsBaseIn
from datetime import datetime
from common.auth import verify_header
from common.logger_config   import logger
#from app.common.rabbitmq_utils import *
from flask import g
from alchemy_db import db
import traceback
import logging
from cache import cache
auth = HTTPTokenAuth()
groups_b = APIBlueprint('groups_Blueprint', __name__)


#################Before requests ##################
@groups_b.before_request
def before_request():
    jsonHeader = verify_header()
    
    if jsonHeader is None:
        #if not verificar_header():
            #raise UnauthorizedError("Token o api-key no validos")   
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin

####################################################

@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de un grupo', summary='Update de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupo/<string:id_grupo>')
@groups_b.input(GroupPatchIn) 
@groups_b.output(GetGroupOut)

def patch_grupo(id_grupo: str, json_data: dict):
    try:
        username=g.username
        res = update_grupo(username, id_grupo, **json_data)
        if res is None:
            raise DataNotFound("Grupo no encontrado")
            
        return res

    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    
 ###############CONSULTA SIMPLE DE GRUPOS###################   
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta simple de grupos.', summary='Consulta simple de grupos por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})                                           
@groups_b.get('/grupo')

@groups_b.input(GroupGetIn,  location='query')
@groups_b.output(GetGroupCountOut)
#@cache.cached(timeout=500, key_prefix=lambda: request.full_path)
def get_grupo(query_data: dict):
    
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nombre=""
        eliminado=False
        suspendido=False
        path_name=False
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()
        
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')
        if(request.args.get('suspendido') is not None):
            suspendido=request.args.get('suspendido')
        if(request.args.get('path_name') is not None):
            path_name=request.args.get('path_name')    
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
            fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')
            fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)  

        res, cant=get_all_grupos_nivel(page,per_page, nombre, fecha_desde, fecha_hasta, path_name, eliminado, suspendido)
        data = {
                "count": cant,
                "data": GetGroupOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  
    
#############DETALLE DE GRUPOS###################    
@groups_b.doc(description='Consulta de grupos con usuarios y tareas ', summary='Consulta detallada de grupo por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo_detalle')
@groups_b.input(GroupGetIn, location='query')
@groups_b.output(GroupCountAllOut)
def get_grupo_detalle(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nombre=""
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
            fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')
            fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)  
 

        res, cant=get_all_grupos_detalle(page,per_page, nombre, fecha_desde, fecha_hasta)
        
        data = {
                "count": cant,
                "data": GroupAllOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  

@groups_b.doc(description='Consulta de grupos por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo/<string:id>')
@groups_b.output(GroupIdOut())
def get_grupo_id(id: str):
    try:
        print("id:",id)
        res = get_grupo_by_id(id)
        
       
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)

@groups_b.doc(description='Consulta de todos los grupos del grupo base de un grupo determinado. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo del grupo base por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupos_grupobase')
@groups_b.input(GroupsBaseIn, location='query')
@groups_b.output(GroupsBaseOut(many=True))
def get_all_grupobase(query_data: dict):
    try:
        id=None
        usuarios=False
        if(request.args.get('id_grupo') is not None):
            id=request.args.get('id_grupo')
        if(request.args.get('usuarios') is not None):
            usuarios=request.args.get('usuarios')
       
                    
        res = get_all_base(id, usuarios)
     
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)        

@groups_b.doc(description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo/<string:id_grupo>')
#@groups_b.input(PageIn, location='query')
@groups_b.output(UsuariosGroupOut(many=True))
def get_usrsbygrupo(id_grupo: str):
    try:
        
        logger.info("id_grupo: "+id_grupo)
        res = get_usuarios_by_grupo(id_grupo)
        
       
        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  
    
#################POST####################
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un grupo', summary='Alta de un nuevo grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(GroupIn)
#@groups_b.output(GroupOut)
def post_grupo(json_data: dict):
    try:
        username=g.username
        res = insert_grupo(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el grupo"
                } 
            res = MsgErrorOut().dump(result)
            return res
            
        return GetGroupOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)  
     
##############DELETE####################
@groups_b.doc(description='Baja de un grupo', summary='Baja de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.delete('/grupo/<string:id>')
#@groups_b.output(GroupOut)
def del_grupo(id: str):
    try:
        #eliminar el grupo con sus hijos
        todos=False
        #elimina solo el grupo
        # todos=False
        res = delete_grupo(id, todos)
        if res is None:
            raise DataNotFound("Grupo no encontrado")
            
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id grupo": id,
                    "grupo": res.nombre
                } 
        
        return result
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    
##################UNDELETE####################
@groups_b.doc(description='Recuperar un grupo', summary='Recuperar un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'}) 
@groups_b.patch('/grupo_undelete/<string:id>')
def restaura_grupo(id: str):
    try:
        todos=False
        res = undelete_grupo(id)
        if res is None:
            raise DataNotFound("Grupo no encontrado")

        result={
                    "Msg":"Registro restaurado",
                    "Id grupo": id,
                    "grupo": res.nombre
                }    
        return result

    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    
  
@groups_b.doc(description='Consulta de todos los grupos del grupo base por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.input(GroupsBaseIn, location='query')
@groups_b.output(GroupsBaseOut)
@groups_b.get('/grupo_base/<string:id>')
def getGrupoBase(id: str):
    try:
        id_grupo=None
        usuarios =False
        if(request.args.get('id_grupo') is not None):
            id=request.args.get('id_grupo')
        if(request.args.get('usuarios') is not None):
            usuarios=request.args.get('usuarios')    
        res = get_all_base(id, usuarios)
        
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)     
