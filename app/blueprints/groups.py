from apiflask import APIBlueprint, HTTPTokenAuth
from flask import request
from ..models.grupo_model import get_all_grupos, update_grupo, insert_grupo, get_usuarios_by_grupo, get_grupo_by_id, delete_grupo
from ..common.error_handling import ValidationError
from typing import List
from ..schemas.schemas import GrupoIn, GrupoPatchIn, GrupoOut, GroupCountOut, PageIn, GroupGetIn, UsuariosGrupoOut, GrupoIdOut
from datetime import datetime
import jwt

auth = HTTPTokenAuth()
groups_b = APIBlueprint('groups_Blueprint', __name__)

#@jwt_required
@auth.verify_token
def verify_token():
    token_encabezado = request.headers.get('Authorization')

    if token_encabezado:
        try:
            # Decodificar y verificar el token
            token = token_encabezado.split(' ')[1]
            payload = jwt.decode(token, verify=False)
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValidationError( 'Token expirado. Inicie sesión nuevamente.')
        except jwt.InvalidTokenError:
            raise ValidationError( 'Token inválido. Inicie sesión nuevamente.')
    else:
        raise ValidationError( 'No se encontró el token de autorización.' )
 
# parser=groups_b.parser()
# parser.add_argument('Authorization', type=str,
#                     location='headers',
#                     help='Bearer Access Token: "Bearer" token',
#                     required=True)



@groups_b.doc(description='Update de un Grupo', summary='Update de un Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
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
        print("res:",res)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err)
    
@groups_b.doc(description='Listado de Grupos existentes. Ejemplo de url: /grupo?first=1&rows=2', summary='Listado de Grupos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupos')
@groups_b.input(PageIn, location='query')
@groups_b.output(GroupCountOut)
def get_grupos(query_data: dict):
    try:
        #page=1
        first=1
        #page_size=10
        rows=10
        if(request.args.get('first') is not None):
            first=int(request.args.get('first'))
        if(request.args.get('rows') is not None):
            rows=int(request.args.get('rows'))

        res, cant=get_all_grupos(first,rows)
        
        
        if res is None or len(res) == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result
       
        data = {
                "count": cant,
                "data": GrupoOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        raise ValidationError(err)  
    
#############Consulta por varios campos################    
@groups_b.doc(description='Consulta de grupos por fecha y descripción. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por fechas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo')
@groups_b.input(GroupGetIn, location='query')
@groups_b.output(GroupCountOut)
def get_grupos_fechas(query_data: dict):
    try:
        first=1
        rows=10
        nombre=""
        fecha_desde="01/01/1900"
        fecha_hasta=datetime.now().strftime("%d/%m/%Y")
        print("query_data:",query_data)
        if(request.args.get('first') is not None):
            first=int(request.args.get('first'))
        if(request.args.get('rows') is not None):
            rows=int(request.args.get('rows'))
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta')  

        res, cant=get_all_grupos(first,rows, nombre, fecha_desde, fecha_hasta)
        
        
        if res is None or len(res) == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result
       
        data = {
                "count": cant,
                "data": GrupoOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        raise ValidationError(err)  

@groups_b.doc(description='Consulta de grupos por id. Ejemplo de url: /grupo?id=id_grupo', summary='Consulta de grupo por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo/<string:id>')
@groups_b.output(GrupoIdOut(many=True))
def get_grupo(id: str):
        res = get_grupo_by_id(id)
        if res is None:
            print("Grupo no encontrado")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontró el grupo"
                } 
            return result

        return res


@groups_b.doc(description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo/<string:id_grupo>')
#@groups_b.input(PageIn, location='query')
@groups_b.output(UsuariosGrupoOut(many=True))
def get_usrsbygrupo(id_grupo: str):
    try:
        print("id_grupo:",id_grupo)
        res = get_usuarios_by_grupo(id_grupo)
        
        
        if res is None == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo sin usuarios",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result
        
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
#################POST####################
@groups_b.doc(description='Alta de un Grupo', summary='Alta de un nuevo Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(GrupoIn)
@groups_b.output(GrupoOut)
def post_grupo(json_data: dict):
    try:
        
        res = insert_grupo(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert grupo",
                    "ErrorMsg":"No se pudo insertar el grupo"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)    
##############DELETE####################
@groups_b.doc(description='Baja de un Grupo', summary='Baja de un Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.delete('/grupo/<string:id>')
#@groups_b.output(GrupoOut)
def del_grupo(id: str):
    try:
        todos=True
        print("id_grupo:",id)
        res = delete_grupo(id, todos)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontró el grupo a eliminar"
                } 
            return result
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id grupo": id,
                    "grupo": res.nombre
                } 
        
        return result
    
    except Exception as err:
        raise ValidationError(err)