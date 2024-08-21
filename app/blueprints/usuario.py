from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.alch_model import Grupo,Usuario
from ..models.usuario_model import get_all_usuarios, get_grupos_by_usuario, insert_usuario, update_usuario, get_usuario_by_id, delete_usuario
from ..schemas.schemas import  UsuarioIn, UsuarioInPatch, UsuarioGetIn, UsuarioCountOut, UsuarioOut, GruposUsuarioOut, UsuarioIdOut, UsuarioAllOut
from ..common.error_handling import ValidationError, DataError, DataNotFound
from datetime import datetime

usuario_b = APIBlueprint('usuario_blueprint', __name__)

#################GET GRUPOS POR USUARIO####################    
@usuario_b.doc(description='Listado de Grupos al que pertenece un Usuario', summary='Grupos por Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/grupos_usuario/<string:id_usuario>')
@usuario_b.output(GruposUsuarioOut(many=True))
def get_grupos_by_usr(id_usuario: str):
    try:
        res = get_grupos_by_usuario(id_usuario)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario sin grupos",
                    "ErrorMsg":"No se encontraron datos de usuarios"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err) 
    
#################POST####################
@usuario_b.doc(description='Alta de nuevo Usuario', summary='Alta de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.post('/usuario')
@usuario_b.input(UsuarioIn)
@usuario_b.output(UsuarioOut)
def post_usuario(json_data: dict):
    try:
        print('inserta usuario')
        res=""
        res = insert_usuario(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert usuario",
                    "ErrorMsg":"No se pudo insertar el usuario"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)
    
#################UPDATE####################
@usuario_b.doc(description='Update de Usuario', summary='Update de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.patch('/usuario/<string:usuario_id>')
@usuario_b.input(UsuarioInPatch)
@usuario_b.output(UsuarioOut)
def patch_usuario(usuario_id: str, json_data: dict):
    try:
        
        res = update_usuario(usuario_id, **json_data)
        if res is None:
            print("No hay datos que modificar")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontró el grupo a modificar"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)

###############GET BY ID####################
@usuario_b.doc(description='Consulta de usuario. Ejemplo de url: /usuario?id=id_usuario', summary='Consulta de usuario por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario/<string:id>')
@usuario_b.output(UsuarioIdOut(many=True))
def get_usuario(id: str):
        res = get_usuario_by_id(id)
        if res is None:
            print("Usuario no encontrado")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontró el grupo"
                } 
            return result

        return res

#############Consulta por varios campos################    
@usuario_b.doc(description='Consulta de usuario con filtros', summary='Consulta de usuario por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuarios_detalle')
@usuario_b.input(UsuarioGetIn, location='query')
@usuario_b.output(UsuarioCountOut)
def get_usuarios_nombre(query_data: dict):
    try:
        page=1
        per_page=10
        nombre=""
        apellido=""
        id_grupo=None
        cant=0
        
        print("query_data:",query_data)
        
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
        

        res, cant=get_all_usuarios(page, per_page, nombre, apellido, id_grupo)

        data = {
                "count": cant,
                "data": UsuarioAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        raise ValidationError(err)  
######################DELETE######################
@usuario_b.doc(description='Baja de un Usuario', summary='Baja de un Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.delete('/usuario/<string:id>')
#@groups_b.output(GrupoOut)
def del_usuario(id: str):
    try:
        res = delete_usuario(id)
        if res is None:
            raise DataNotFound("Usuario no encontrado")
            
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id usuario": id,
                    "usuario": res.nombre
                } 
        
        return result
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)