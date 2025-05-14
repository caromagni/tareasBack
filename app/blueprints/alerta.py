import schemas.schemas as schema
import models.tarea_model as tarea_model
import common.error_handling as error_handling
import decorators.role as rol
import common.usher as usher
import common.auth as auth_token
import traceback
from common.logger_config import logger
from flask import g
from apiflask import APIBlueprint
from flask import request, current_app



alerta_b = APIBlueprint('alerta_blueprint', __name__)


#################Before requests ##################
@alerta_b.before_request
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
     
@alerta_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Listado de Tareas a vencer', summary='Tareas a vencer', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided', 800: '{"code": 800,"error": "DataNotFound", "error_description": "Datos no encontrados"}'})
@alerta_b.get('/alertas')
@alerta_b.input(schema.TareaAlertaIn, location='query')
@alerta_b.output(schema.TareaCountAllOut)
@rol.require_role(["consultar-alerta"])
def get_alerta_tarea(query_data: dict):
    try:
        dias_aviso=15
        cant=0
        username=g.get('username')
        dias_aviso=int(request.args.get('dias_aviso'))
        grupos_usr=request.args.get('grupos_usr')
        logger.info("Tareas a vencer")
        res, cant = tarea_model.tareas_a_vencer(username, dias_aviso, grupos_usr)
        data = {
                "count": cant,
                "data": schema.TareaAllOut().dump(res, many=True)
            }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)     