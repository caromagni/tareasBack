import schemas.schemas as schema
import models.grupo_model as grupo_model
import common.error_handling as error_handling
import decorators.role as rol
import common.auth as auth_token
import traceback
from flask import g
from apiflask import APIBlueprint, HTTPTokenAuth
from flask import request, current_app

auth = HTTPTokenAuth()
groups_b = APIBlueprint('groups_Blueprint', __name__)

#################Before requests ##################

@groups_b.before_request
def before_request():
    print("************ingreso a before_request Usuarios************")
    jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=None
            type_origin=None
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin




@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Update de un grupo', summary='Update de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupo/<string:id_grupo>')
@groups_b.input(schema.GroupPatchIn) 
@groups_b.output(schema.GetGroupOut)
@rol.require_role(["modificar-grupo"])
def patch_grupo(id_grupo: str, json_data: dict):
    try:
        username=g.username
        res = grupo_model.update_grupo(username, id_grupo, **json_data)
        if res is None:
            raise error_handling.DataNotFound("Grupo no encontrado")
            
        return res

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
 ###############CONSULTA SIMPLE DE GRUPOS###################   
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta simple de grupos.', summary='Consulta simple de grupos por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})                                           
@groups_b.get('/grupo')
@groups_b.input(schema.GroupGetIn,  location='query')
@groups_b.output(schema.GetGroupCountOut)
@rol.require_role(["consultar-grupo"])
def get_grupo(query_data: dict):
    try:

        page = 1
        per_page = int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        eliminado = request.args.get('eliminado')
        suspendido = request.args.get('suspendido')
        path_name = request.args.get('path_name')
        if(request.args.get('page') is not None):
            page = int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page = int(request.args.get('per_page'))
        nombre = request.args.get('nombre')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        res, cant = grupo_model.get_all_grupos_nivel(page, per_page, nombre, fecha_desde, fecha_hasta, path_name, eliminado, suspendido)
        
        data = {
            "count": cant,
            "data": schema.GetGroupOut().dump(res, many=True)
        }
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
#############DETALLE DE GRUPOS###################    
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de grupos con usuarios y tareas ', summary='Consulta detallada de grupo por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo_detalle')
@groups_b.input(schema.GroupGetIn, location='query')
@groups_b.output(schema.GroupCountAllOut)
@rol.require_role(["consultar-grupo"])
def get_grupo_detalle(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        nombre=request.args.get('nombre')
        eliminado = request.args.get('eliminado')
        suspendido = request.args.get('suspendido')
        fecha_desde=request.args.get('fecha_desde')
        fecha_hasta=request.args.get('fecha_hasta')

        res, cant=grupo_model.get_all_grupos_detalle(page,per_page, nombre, eliminado, suspendido, fecha_desde, fecha_hasta)
        
        data = {
                "count": cant,
                "data": schema.GroupAllOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)  

@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de grupos por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo/<string:id>')
@groups_b.output(schema.GroupIdOut())
@rol.require_role(["consultar-grupo"])
def get_grupo_id(id: str):
    try:
        #can_pass=validar_rol(jwt,["leer-grupo"])

        print("id:",id)
        res = grupo_model.get_grupo_by_id(id)
        
       
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)

@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de todos los grupos del grupo base de un grupo determinado. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo del grupo base por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupos_grupobase')
@groups_b.input(schema.GroupsBaseIn, location='query')
@groups_b.output(schema.GroupsBaseOut(many=True))
@rol.require_role(["consultar-grupo"])
def get_all_grupobase(query_data: dict):
    try:
        id=None
        usuarios=False
        if(request.args.get('id_grupo') is not None):
            id=request.args.get('id_grupo')
        if(request.args.get('usuarios') is not None):
            usuarios=request.args.get('usuarios')
       
                    
        res = grupo_model.get_all_base(id, usuarios)
     
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)        

@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo')
@groups_b.input(schema.UsuariosGroupIn, location='query')
@groups_b.output(schema.UsuariosGroupOut(many=True))
@rol.require_role(["consultar-grupo"])
def get_usrsbygrupo(query_data: dict):
    try:
        grupos=None
        if(request.args.get('grupos') is not None):
            grupos = request.args.get('grupos')
            grupos = [grupo.strip() for grupo in grupos.split(",")]
        #res = get_usuarios_by_grupo(id_grupo)
        res = grupo_model.get_usuarios_by_grupo(grupos)
       
        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)  
    
#################POST####################
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un grupo', summary='Alta de un nuevo grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(schema.GroupIn)
@rol.require_role(["consultar-grupo"])
def post_grupo(json_data: dict):
    try:
        username=g.username
        res = grupo_model.insert_grupo(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el grupo"
                } 
            res = schema.MsgErrorOut().dump(result)
            return res
            
        return schema.GetGroupOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)  
     
##############DELETE####################
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de un grupo', summary='Baja de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.delete('/grupo/<string:id>')
@groups_b.output(schema.GroupOut)
@rol.require_role(["eliminar-grupo"])
def del_grupo(id: str):
    try:
        username=g.username
        #eliminar el grupo con sus hijos
        todos=False
        #elimina solo el grupo
        # todos=False
        res = grupo_model.delete_grupo(username, id, todos)
        if res is None:
            raise error_handling.DataNotFound("Grupo no encontrado")
  
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
##################UNDELETE####################
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Recuperar un grupo', summary='Recuperar un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'}) 
@groups_b.patch('/grupo_undelete/<string:id>')
@rol.require_role(["modificar-grupo"])
def restaura_grupo(id: str):
    try:
        username=g.username
        todos=False
        res = grupo_model.undelete_grupo(username, id)
        if res is None:
            raise error_handling.DataNotFound("Grupo no encontrado")

        result={
                    "Msg":"Registro restaurado",
                    "Id grupo": id,
                    "grupo": res.nombre
                }    
        return result

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
  
@groups_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de todos los grupos del grupo base por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.input(schema.GroupsBaseIn, location='query')
@groups_b.output(schema.GroupsBaseOut)
@groups_b.get('/grupo_base/<string:id>')
@rol.require_role(["consultar-grupo"])
def getGrupoBase(id: str):
    try:
        id_grupo=None
        usuarios =False
        if(request.args.get('id_grupo') is not None):
            id=request.args.get('id_grupo')
        if(request.args.get('usuarios') is not None):
            usuarios=request.args.get('usuarios')    
        res = grupo_model.get_all_base(id, usuarios)
        
        return res
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
