from apiflask import APIBlueprint, HTTPTokenAuth
from ..api_key import *
from flask import request, current_app
from ..models.grupo_model import get_all_grupos, get_all_grupos_detalle, update_grupo, insert_grupo, get_usuarios_by_grupo, get_grupo_by_id, delete_grupo, get_all_grupos_nivel, undelete_grupo
from ..common.error_handling import ValidationError, DataError, DataNotFound, UnauthorizedError
from typing import List
from ..schemas.schemas import GroupIn, GroupPatchIn, GroupOut, GroupCountOut, GroupCountAllOut, GroupGetIn, UsuariosGroupOut, GroupIdOut, GroupAllOut, MsgErrorOut
from datetime import datetime
from ..common.auth import verificar_header


auth = HTTPTokenAuth()
groups_b = APIBlueprint('groups_Blueprint', __name__)


#################Before requests ##################
@groups_b.before_request
def before_request():
    if not verificar_header():
        #raise UnauthorizedError("Token o api-key no validos")   
        print("Token o api key no validos")  
####################################################

@groups_b.doc(description='Update de un grupo', summary='Update de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupo/<string:id_grupo>')
@groups_b.input(GroupPatchIn) 
@groups_b.output(GroupOut)

def patch_grupo(id_grupo: str, json_data: dict):
    try:
        
        res = update_grupo(id_grupo, **json_data)
        if res is None:
            raise DataNotFound("Grupo no encontrado")
            
        return res
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)
    
 ###############CONSULTA SIMPLE DE GRUPOS###################   
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta simple de grupos.', summary='Consulta simple de grupos por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})                                           
@groups_b.get('/grupo')
@groups_b.input(GroupGetIn,  location='query')
@groups_b.output(GroupCountOut)
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
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')  
        

        res, cant=get_all_grupos_nivel(page,per_page, nombre, fecha_desde, fecha_hasta, path_name, eliminado, suspendido)
        data = {
                "count": cant,
                "data": GroupOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
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
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')  

        res, cant=get_all_grupos_detalle(page,per_page, nombre, fecha_desde, fecha_hasta)
        
        data = {
                "count": cant,
                "data": GroupAllOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
        raise ValidationError(err)  

@groups_b.doc(description='Consulta de grupos por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo/<string:id>')
@groups_b.output(GroupIdOut())
def get_grupo_id(id: str):
    try:
        print("id:",id)
        res = get_grupo_by_id(id)
        
        current_app.session.remove()
        return res
    except Exception as err:
        raise ValidationError(err)
        


@groups_b.doc(description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo/<string:id_grupo>')
#@groups_b.input(PageIn, location='query')
@groups_b.output(UsuariosGroupOut(many=True))
def get_usrsbygrupo(id_grupo: str):
    try:
        res = get_usuarios_by_grupo(id_grupo)
        
        current_app.session.remove()
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
#################POST####################
@groups_b.doc(description='Alta de un grupo', summary='Alta de un nuevo grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(GroupIn)
#@groups_b.output(GroupOut)
def post_grupo(json_data: dict):
    try:
        res = insert_grupo(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el grupo"
                } 
            res = MsgErrorOut().dump(result)
            return res
            
        return GroupOut().dump(res)
    
    except Exception as err:
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
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
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
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)