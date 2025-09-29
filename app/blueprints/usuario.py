from apiflask import APIBlueprint
from flask import current_app, request
from db.alchemy_db import db
import schemas.schemas as schema
import models.usuario_model as usuario_model
import models.grupo_hierarchy as grupo_hierarchy
import common.error_handling as error_handling
import common.exceptions as exceptions
import decorators.role as rol
import decorators.verify as verify
import common.auth as auth_token
import traceback
import decorators.role as rol
from flask import g

usuario_b = APIBlueprint('usuario_blueprint', __name__)
#################Before requests ##################
@usuario_b.before_request
def before_request():
    if request.method == 'OPTIONS':
        return  # Skip custom logic for OPTIONS requests
    
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')

#################GET GRUPOS POR USUARIO####################    
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Listado de Grupos al que pertenece un Usuario', summary='Grupos por Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/grupo_usuario/<string:id_usuario>')
#@usuario_b.output(GroupsUsuarioOut(many=True))
@verify.check_fields()
@rol.require_role()
def get_grupos_by_usr(id_usuario: str):
    try:
        print('***************ingreso a get grupos by usr**************')
        res = usuario_model.get_grupos_by_usuario(id_usuario)
        data = {
                
                "data":  schema.GroupsUsuarioOut().dump(res, many=True)
        }
 
      
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 
    
#####################POST#########################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Alta de nuevo Usuario', summary='Alta de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.post('/usuario')
@usuario_b.input(schema.UsuarioIn)
@verify.check_fields()
@rol.require_role()
def post_usuario(json_data: dict):
    try:
        print('inserta usuario')
        user_actualizacion=g.username        
        res = usuario_model.insert_usuario(user_actualizacion, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert usuario",
                    "ErrorMsg":"No se pudo insertar el usuario"
                } 
            return result
        data = {
                
                "data": schema.UsuarioOut().dump(res)
        }

        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)
    
#################UPDATE####################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Update de Usuario', summary='Update de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.patch('/usuario/<string:id_usuario>')
@usuario_b.input(schema.UsuarioInPatch)
@verify.check_fields()
@rol.require_role()
def patch_usuario(id_usuario: str, json_data: dict):
    try:
        username=g.username
        print("Username usuario.py:",username)
        res = usuario_model.update_usuario(id_usuario, username, **json_data)
        if res is None:
            print("No hay datos que modificar")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario no encontrado",
                    "ErrorMsg":"No se encontró el usuario a modificar"
                } 
            return result
        
        data = {
                
                "data": schema.UsuarioOut().dump(res)
        }

        #return UsuarioOut().dump(res)    
        return data
        
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

###############GET BY ID####################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de usuario. Ejemplo de url: /usuario?id=id_usuario', summary='Consulta de usuario por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario/<string:id>')
@verify.check_fields()
@rol.require_role()
def get_usuario_id(id: str):
        res = usuario_model.get_usuario_by_id(id)
        if res is None or len(res)==0:
            print("Usuario no encontrado")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario no encontrado",
                    "ErrorMsg":"No se encontró el usuario"
                } 
            return result
        data = {
                
                "data":  schema.UsuarioIdOut().dump(res, many=True)
        }
        
        return data
        

#############GET CON PARAMETROS######################## 
# CONSULTA SIMPLE
#######################################################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de usuarios', summary='Consulta simple de usuarios por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario')
@usuario_b.input(schema.UsuarioGetIn, location='query')
@usuario_b.output(schema.UsuarioCountOut)
@verify.check_fields()
@rol.require_role()
def get_usuario(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        
        print("query_data:",query_data)
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        id_grupo=request.args.get('id_grupo')    
        nombre=request.args.get('nombre')
        apellido=request.args.get('apellido')  
        dni=request.args.get('dni') 
        username=request.args.get('username')           
        eliminado=request.args.get('eliminado')
        suspendido=request.args.get('suspendido')    

        res, cant=usuario_model.get_all_usuarios(page, per_page, nombre, apellido, id_grupo, dni, username, eliminado, suspendido)

        data = {
                "count": cant,
                "data": schema.UsuarioOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err) 
    
#####################DETALLE DE USUARIOS#######################   
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de usuarios con sus grupos y tareas', summary='Consulta detallada de usuarios por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario_detalle')
@usuario_b.input(schema.UsuarioGetIn, location='query')
@usuario_b.output(schema.UsuarioCountAllOut)
#@rol.require_role()
@verify.check_fields()
def get_usuarios_detalle(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        id_grupo=request.args.get('id_grupo')    
        nombre=request.args.get('nombre')
        apellido=request.args.get('apellido')    
        dni=request.args.get('dni')
        username=request.args.get('username')
        eliminado=request.args.get('eliminado')
        suspendido=request.args.get('suspendido')                

        res, cant=usuario_model.get_all_usuarios_detalle(page, per_page, nombre, apellido, id_grupo, dni, username, eliminado, suspendido)

        data = {
                "count": cant,
                "data": schema.UsuarioAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)  
    
######################DELETE######################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Baja de un Usuario', summary='Baja de un Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.delete('/usuario/<string:id>')
@verify.check_fields()
@rol.require_role()
def del_usuario(id: str):
    try:
        username=g.username
        print("Username usuario.py:",username)
        res = usuario_model.delete_usuario(username, id)
        if res is None:
            raise exceptions.DataNotFound("Usuario no encontrado")
            
        else:
            data={
                    "Msg":"Registro eliminado",
                    "Id usuario": id,
                    "usuario": res.nombre
                } 
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)

##########Prueba Roles################
@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta del rol de un usuario', summary='Consulta de Rol de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/usuario_rol')
@usuario_b.output(schema.UsuarioDominiosCountOut)
@rol.require_role()
@verify.check_fields()
def get_rol_usr():
    username=g.username
    res=usuario_model.get_rol_usuario(username)

    if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert de tipo de tarea",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
    
    data = {
                "count": len(res),
                "data": schema.UsuarioDominiosOut().dump(res, many=True)
            }
        
        
    return data

@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Listado de Grupos al que pertenece un Usuario con grupo padre', summary='Grupos por Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/groups_with_base')
@usuario_b.input(schema.UsuarioGetIn, location='query')
#@rol.require_role()
@verify.check_fields()
def get_groups_base_by_usr(query_data: dict):
    try:
        print('***************ingreso a get grupos by usr**************')
        print("query_data:",query_data)
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nombre=""
        apellido=""
        id_grupo=None
        dni=""
        username=""
        cant=0
        eliminado= None
        suspendido=None
        
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_grupo') is not None):
            id_grupo=request.args.get('id_grupo')    
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('apellido') is not None):
            apellido=request.args.get('apellido')    
        if(request.args.get('dni') is not None):
            dni=request.args.get('dni')
        if(request.args.get('username') is not None):
            username=request.args.get('username')
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')
        if(request.args.get('suspendido') is not None):
            suspendido=request.args.get('suspendido')                

        res, cant=usuario_model.get_all_usuarios_detalle(page, per_page, nombre, apellido, id_grupo, dni, username, eliminado, suspendido)

        # Add check for empty results
        if not res or len(res) == 0:
            # Return empty result or appropriate response
            return {"data": [], "count": 0}

        if res is not None or len(res)>0:
        
            for r in res[0]['grupo']:
                id_padre=grupo_hierarchy.find_parent_id_recursive(db.session, r['id_grupo'])
                r['id_padre']=id_padre
                print("r con id padre:",r)

        return res
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)  


@usuario_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Consulta de los dominios de un usuario|', summary='Consulta de Dominio de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/usuario_dominio')
@usuario_b.output(schema.UsuarioCountDominioOut)
#@rol.require_role()
@verify.check_fields()
def get_dominio_usr():
    username=g.username
    res=usuario_model.get_dominio_usuario(username)

    if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert de tipo de tarea",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
    
    data = {
                "count": len(res),
                "data": schema.UsuarioDominioOut().dump(res, many=True)
            }
        
    return data
    