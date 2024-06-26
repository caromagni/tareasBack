from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.alch_model import Grupo,Usuario
from ..models.usuario_model import get_all_usuarios, get_usuario_by_id, insert_usuario
from ..schemas.schemas import  UsuarioIn, UsuarioOut
from ..common.error_handling import ValidationError

usuario_b = APIBlueprint('usuario_b', __name__)

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
    

#################POST####################
@usuario_b.post('/usuario')
@usuario_b.input(UsuarioIn)
@usuario_b.output(UsuarioOut)
def post_usuario(json_data: dict):
    try:
        
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