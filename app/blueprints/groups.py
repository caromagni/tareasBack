from apiflask import APIBlueprint, HTTPTokenAuth
from flask import request, current_app
from ..models.grupo_model import get_all_grupos, get_all_grupos_detalle, update_grupo, insert_grupo, get_usuarios_by_grupo, get_grupo_by_id, delete_grupo
from ..common.error_handling import ValidationError, DataError, DataNotFound
from typing import List
from ..schemas.schemas import GrupoIn, GrupoPatchIn, GrupoOut, GroupCountOut, GroupCountAllOut, GroupGetIn, UsuariosGrupoOut, GrupoIdOut, GrupoAllOut, MsgErrorOut
from datetime import datetime
import jwt
from ..common.keycloak import get_public_key
import os

auth = HTTPTokenAuth()
groups_b = APIBlueprint('groups_Blueprint', __name__)



@auth.verify_token
def verify_token():
    token_encabezado = request.headers.get('Authorization')
    jwt_pk=current_app.config['JWT_PUBLIC_KEY'] 
    jwt_alg=current_app.config['JWT_ALGORITHM']
    jwt_aud=current_app.config['JWT_DECODE_AUDIENCE']

    if token_encabezado:
        try:
            # Decodificar y verificar el token
            token = token_encabezado.split(' ')[1]
          
            payload = jwt.decode(jwt=token, key=jwt_pk, algorithms=jwt_alg, audience=jwt_aud)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValidationError( 'Token expirado. Inicie sesión nuevamente.')
        except jwt.InvalidTokenError as e:
            raise ValidationError( 'Token inválido. Inicie sesión nuevamente.')
        except Exception as e:
            raise ValidationError( 'Error al decodificar el token. Inicie sesión nuevamente.')
    else:
        raise ValidationError( 'No se encontró el token de autorización.' )
 
# parser=groups_b.parser()
# parser.add_argument('Authorization', type=str,
#                     location='headers',
#                     help='Bearer Access Token: "Bearer" token',
#                     required=True)



@groups_b.doc(description='Update de un grupo', summary='Update de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupo/<string:id_grupo>')
@groups_b.input(GrupoPatchIn) 
@groups_b.output(GrupoOut)

def patch_grupo(id_grupo: str, json_data: dict):
    try:
        #token_payload = verify_token()
        #print("token_payload:",token_payload)
        #nombre_usuario=token_payload['preferred_username']
        #print("nombre_usuario:",nombre_usuario)
        #print("json_data:",json_data)
        res = update_grupo(id_grupo, **json_data)
        if res is None:
            raise DataNotFound("Grupo no encontrado")
            
        return res
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)
    
 ###############CONSULTA SIMPLE DE GRUPOS###################   
@groups_b.doc(description='Consulta simple de grupos.', summary='Consulta simple de grupos por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})                                           
@groups_b.get('/grupo')
@groups_b.input(GroupGetIn, location='query')
@groups_b.output(GroupCountOut)
def get_grupo(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        print(type(per_page))
        nombre=""
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()
        print("query_data:",query_data)
        print("per_page:",per_page)
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

        res, cant=get_all_grupos(page,per_page, nombre, fecha_desde, fecha_hasta)
        
        
        data = {
                "count": cant,
                "data": GrupoOut().dump(res, many=True)
            }
        
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
        print("query_data:",query_data)
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
        
        print("res:",res)
       
        data = {
                "count": cant,
                "data": GrupoAllOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        raise ValidationError(err)  

@groups_b.doc(description='Consulta de grupos por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo/<string:id>')
@groups_b.output(GrupoIdOut())
def get_grupo_id(id: str):
    try:
        print("id:",id)
        res = get_grupo_by_id(id)
        
        return res
    except Exception as err:
        raise ValidationError(err)
        


@groups_b.doc(description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo/<string:id_grupo>')
#@groups_b.input(PageIn, location='query')
@groups_b.output(UsuariosGrupoOut(many=True))
def get_usrsbygrupo(id_grupo: str):
    try:
        res = get_usuarios_by_grupo(id_grupo)
        
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
#################POST####################
@groups_b.doc(description='Alta de un grupo', summary='Alta de un nuevo grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(GrupoIn)
#@groups_b.output(GrupoOut)
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
            
        return GrupoOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)  
     
##############DELETE####################
@groups_b.doc(description='Baja de un grupo', summary='Baja de un grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.delete('/grupo/<string:id>')
#@groups_b.output(GrupoOut)
def del_grupo(id: str):
    try:
        #eliminar el grupo con sus hijos
        todos=True
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