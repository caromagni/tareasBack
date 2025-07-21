import schemas.schemas as schema
import models.ep_model_json as ep_model_json
import common.error_handling as error_handling
import common.exceptions as exceptions
import decorators.role as rol
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app
import uuid
import os

ep_url = APIBlueprint('url_blueprint', __name__)


#################Before requests ##################
@ep_url.before_request
def before_request():
    print("ENTRANDO A BEFORE REQUEST")
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')
     
@ep_url.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}, {'UserRoleAuth':[]}], description='Returns a URL to see details of a given task ID', summary='Endpoints', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@ep_url.get('/tarea/url/<string:id_tarea>')
@ep_url.output(schema.URLTareaOut)
#@rol.require_role()
def ep_url_(id_tarea:str):
    try:
        print(type(id_tarea))
        #validate id_tarea is a valid uuid
        if not uuid.UUID(id_tarea):
            raise exceptions.ValidationError("Invalid task ID")
        #get URL from env variable
        url = os.getenv('BACKEND_URL_TASKS')
        #add rest of url parts /tareas_grupos/d272173d-2c4c-4300-a1e7-96a01e2dfc2f/show_task_detail
        url_full = f"{url}/tareas_grupos/{id_tarea}/show_task_detail"
        res = {'url': url_full}
        print(schema.URLTareaOut().dump(res))
        return schema.URLTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise exceptions.ValidationError(err)     
