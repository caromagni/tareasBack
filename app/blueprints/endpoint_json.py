import schemas.schemas as schema
import models.ep_model_json as ep_model_json
import common.error_handling as error_handling
import decorators.role as rol
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



ep_bj = APIBlueprint('ep_json_blueprint', __name__)


#################Before requests ##################
@ep_bj.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
       
    """ jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin """
    
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
     
@ep_bj.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Listado EP', summary='Endpoints', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_bj.get('/epj')
@ep_bj.output(schema.EPCountOut)
@rol.require_role("Operador")
def get_epj():
    try:
        cant=0
        username=g.get('username')
        res, cant = ep_model_json.get_all_EP(username)
        data = {
                "count": cant,
                "data": schema.EPOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)     
    
@ep_bj.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Guardo los casos de uso para cada enpoint en un archivo json', summary='Escribo los endpoints en un archivo json ', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_bj.post('/epj')
@ep_bj.input(schema.EPInput)
@rol.require_role("Operador")
def post_epj(json_data: dict):
    try:
        print("ENTRANDO A POST EP-", json_data)
        cant=0
        username=g.get('username')
        res = ep_model_json.insert_EP(username, **json_data)
        return schema.EPOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    

""" @ep_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Export Endpoints to json file', summary='Export Endpoints to json file', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_b.get('/ep/export')
@ep_b.output(schema.EPCountOut)
def exportar_eps():
    try:
        res, cant= ep_model.exportar_eps_a_json()
        data = {
                "count": cant,
                "data": schema.EPOut().dump(res, many=True)
            }
        
        
        return data
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)        """  