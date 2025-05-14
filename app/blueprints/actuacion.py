from apiflask import APIBlueprint
from flask import g
import decorators.role as rol
import schemas.schemas as schemas
import models.actuacion_model as actuacion_model
import common.error_handling as error_handling
import common.auth as auth_token


actuacion_b = APIBlueprint('actuacion_blueprint', __name__)

#################Before requests ##################
@actuacion_b.before_request
def before_request():
    print("************ingreso a before_request Usuarios************")
    print("Before request user.py")

    jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=None
            type_origin=None
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin
@actuacion_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Actuaciones', summary='Actuaciones', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@actuacion_b.get('/actuacion')
@actuacion_b.output(schemas.ActuacionOut(many=True))
@rol.require_role(["consultar-actuacion"])
def get_actuaciones():
    
    try:
        res = actuacion_model.get_all_actuaciones()
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
        raise error_handling.ValidationError(err)  
    
@actuacion_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Tipo de actuaciones', summary='Tipo de actuaciones', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@actuacion_b.get('/tipo_actuaciones')
@actuacion_b.output(schemas.TipoActuacionOut(many=True))
@rol.require_role(["consultar-actuacion"])
def get_tipoactuaciones():
    try:
        res = actuacion_model.get_all_tipoactuaciones()
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
        raise error_handling.ValidationError(err)      