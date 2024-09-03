from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from ..models.expediente_model import get_all_expedientes
from ..schemas.schemas import  ExpedienteOut
from ..common.error_handling import ValidationError

expediente_b = APIBlueprint('expediente_blueprint', __name__)

@expediente_b.doc(description='Listado de Expedientes', summary='Listado de Expedientes del organismo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@expediente_b.get('/expediente')
@expediente_b.output(ExpedienteOut(many=True))
def get_expedientes():
    try:
        res = get_all_expedientes()
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Expedientes no encontrados",
                    "ErrorMsg":"No se encontraron datos de expedientes"
                } 
            return result
        current_app.session.remove()    
        return res
    
    except Exception as err:
        raise ValidationError(err)  
      