import schemas.schemas as schema
import models.organismo_model as organismo_model
import common.exceptions as exceptions
import decorators.role as rol
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint



organismo_b = APIBlueprint('organismo_blueprint', __name__)


#################Before requests ##################
@organismo_b.before_request
def before_request():
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')

@organismo_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Listado de Organismos', summary='Organismos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@organismo_b.get('/organismo')
@organismo_b.output(schema.OrganismoCountOut)
#@rol.require_role()
def get_organismo():
    try:
      
        username=g.get('username')

        res, cant = organismo_model.get_organismo()
        data = {
                "count": cant,
                "data": schema.OrganismoOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)     