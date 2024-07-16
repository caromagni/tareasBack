from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.alch_model import Grupo,Usuario
from ..models.usuario_model import get_all_usuarios, get_grupos_by_usuario, insert_usuario, update_usuario
from ..schemas.schemas import  UsuarioIn, UsuarioOut, GruposUsuarioOut
from ..common.error_handling import ValidationError

usuario_b = APIBlueprint('usuario_blueprint', __name__)

@usuario_b.doc(description='Listado de Usuarios', summary='Usuarios', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/usuario')
@usuario_b.output(UsuarioOut(many=True))
def get_usuarios():
    try:
        res = get_all_usuarios()
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario no encontrado",
                    "ErrorMsg":"No se encontraron datos de usuarios"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
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
@usuario_b.input(UsuarioIn)
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

#################DELETE####################