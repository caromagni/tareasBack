import schemas.schemas as schema
import models.ep_model as ep_model
import common.error_handling as error_handling
import decorators.role as rol
import common.auth as auth_token
import common.usher as usher
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



ep_b = APIBlueprint('ep_blueprint', __name__)


#################Before requests ##################
@ep_b.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
       
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')
     
@ep_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Listado EP', summary='Endpoints', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_b.get('/ep')
@ep_b.output(schema.EPCountOut)
@rol.require_role()
def get_ep():
    try:
        cant=0
        username=g.get('username')
        res, cant = ep_model.get_all_EP(username)
        data = {
                "count": cant,
                "data": schema.EPOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)     
    
@ep_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Endpoints', summary='Endpoints', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_b.post('/ep')
@ep_b.input(schema.EPInput)
@rol.require_role()
def post_ep(json_data: dict):
    try:
        print("ENTRANDO A POST EP-", json_data)
        cant=0
        username=g.get('username')
        res = ep_model.insert_EP(username, **json_data)
        return schema.EPOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)  

@ep_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Migrar cu a la base', summary='Migrar cu', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_b.post('/migra_ep')
@ep_b.output(schema.EPCountOut)
def post_migraep():
    try:
        print("ENTRANDO A MIGRACION EP")
        cant=0
        username=g.get('username')
        res = usher.migrar_cu(username)
        data = {
                "count": len(res),
                "data": schema.EPOut().dump(res, many=True)
            }
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)            