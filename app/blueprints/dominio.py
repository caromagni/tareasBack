import schemas.schemas as schema
import models.dominio_model as dominio_model
import common.error_handling as error_handling
import common.exceptions as exceptions
import decorators.role as rol
import common.usher as usher
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



dominio_b = APIBlueprint('dominio_blueprint', __name__)


#################Before requests ##################
@dominio_b.before_request
def before_request():
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')
     
@dominio_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Listado de Dominios', summary='Dominios', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@dominio_b.get('/dominio')
@dominio_b.output(schema.DominioCountOut)
@rol.require_role()
def get_dominio():
    try:
      
        username=g.get('username')
      
        res, cant = dominio_model.get_dominio()
        data = {
                "count": cant,
                "data": schema.DominioOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)     