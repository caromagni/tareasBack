from apiflask import APIBlueprint
from flask import g
import decorators.role as rol
import schemas.schemas as schemas
import models.expediente_model as expediente_model
import common.error_handling as error_handling
import common.auth as auth_token 

expediente_b = APIBlueprint('expediente_blueprint', __name__)

#################Before requests ##################
@expediente_b.before_request
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


@expediente_b.get('/expediente')
@expediente_b.output(schemas.ExpedienteOut(many=True))
@expediente_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Listado de Expedientes', summary='Listado de Expedientes del organismo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Server error'})
@rol.require_role("Operador")
def get_expedientes():
    try:
        res = expediente_model.get_all_expedientes()
        if res is None:
            result = {
                "valido": "fail",
                "ErrorCode": 800,
                "ErrorDesc": "Expedientes no encontrados",
                "ErrorMsg": "No se encontraron datos de expedientes"
            }
            return result
            
        return res

    except Exception as err:
        raise error_handling.ValidationError(err)
