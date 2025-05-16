import schemas.schemas as schema
import models.cu_model as cu_model
import common.error_handling as error_handling
import decorators.role as rol
import common.usher as usher
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



cu_b = APIBlueprint('cu_blueprint', __name__)


#################Before requests ##################
@cu_b.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
       
    jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin
     
@cu_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Casos de Uso del Sistema', summary='Casos de Uso', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@cu_b.get('/cu')
@cu_b.output(schema.CUCountOut)
@rol.require_role(["consultar-alerta"])
def get_cu():
    try:
        cant=0
        username=g.get('username')
        res, cant = cu_model.get_all_CU(username)
        data = {
                "count": cant,
                "data": schema.CUOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)     



@cu_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Casos de Uso del Sistema ', summary='Casos de Uso', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@cu_b.post('/cu')
@cu_b.input(schema.CUInput)
@rol.require_role(["insertar-ep"])
def post_cu(json_data: dict):
    try:
        username=g.get('username')
        res = cu_model.insert_CU(username, **json_data)
        data = {
                "data": schema.CUOut().dump(res)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    