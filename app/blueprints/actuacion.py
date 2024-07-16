from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.actuacion_model import get_all_actuaciones, get_all_tactuaciones
from ..schemas.schemas import  ActuacionOut, TipoActuacionOut
from ..common.error_handling import ValidationError

actuacion_b = APIBlueprint('actuacion_blueprint', __name__)

@actuacion_b.doc(description='Actuaciones', summary='Actuaciones', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@actuacion_b.get('/actuaciones')
@actuacion_b.output(ActuacionOut(many=True))
def get_actuaciones():
    try:
        res = get_all_actuaciones()
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Actuaciones no encontradas",
                    "ErrorMsg":"No se encontraron datos de actuaciones"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
@actuacion_b.doc(description='Tipo de actuaciones', summary='Tipo de actuaciones', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@actuacion_b.get('/tipo_actuaciones')
@actuacion_b.output(TipoActuacionOut(many=True))
def get_tactuaciones():
    try:
        res = get_all_tactuaciones()
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tipo de actuaciones no encontradas",
                    "ErrorMsg":"No se encontraron datos de tipos de actuaciones"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)      