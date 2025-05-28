import schemas.schemas as schema
import models.label_model as label_model
import common.error_handling as error_handling
import common.auth as auth_token
import decorators.role as rol
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from flask import request
from flask import g
import traceback

label_b = APIBlueprint('label_blueprint', __name__)

# ###############
@label_b.before_request
def before_request():
    
    """ jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
        #if not verificar_header():
            #raise UnauthorizedError("Token o api-key no validos")   
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
# ####################################################

################################ ETIQUETAS ################################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label', summary='Consulta de labels por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label')
@label_b.input(schema.LabelGetIn, location='query')
@label_b.output(schema.LabelCountOut)
@rol.require_role("Operador")
def get_labels(query_data: dict):
    try:
        username = g.username

        page = 1
        per_page = int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant = 0
        nombre = ""
        eliminado = None
        label_color = ""
        id_user_creacion = None
        id_tarea = None
        id_grupo_base = None
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()

        if request.args.get('page') is not None:
            page = int(request.args.get('page'))
        if request.args.get('per_page') is not None:
            per_page = int(request.args.get('per_page'))
        if request.args.get('id_user_creacion') is not None:
            id_user_creacion = request.args.get('id_user_creacion')       
        if request.args.get('nombre') is not None:
            nombre = request.args.get('nombre')
        if request.args.get('id_tarea') is not None:
            id_tarea = request.args.get('id_tarea') 
        if request.args.get('eliminado') is not None:
            eliminado = request.args.get('eliminado')           
        if request.args.get('fecha_desde') is not None:
            fecha_desde = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta') is not None:
            fecha_hasta = request.args.get('fecha_hasta')
        if request.args.get('label_color') is not None:
            label_color = request.args.get('label_color')  

        res, cant = label_model.get_all_label(username, page, per_page, nombre, id_grupo_base, id_tarea, id_user_creacion, fecha_desde, fecha_hasta, eliminado, label_color)    
        data = {
            "count": cant,
            "data": schema.LabelAllOut().dump(res, many=True)
        }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 


@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label por ID', summary='Label por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label/<string:id>')
@label_b.output(schema.LabelIdOut)
@rol.require_role("Operador")
def get_label(id:str):
    print('label.py')
    try:
        res = label_model.get_label_by_id(id)
        if res is None:
            raise error_handling.DataNotFound("Label no encontrada")

        result = schema.LabelIdOut().dump(res)
        
        return result
 
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 


@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Label', summary='Alta de label', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.post('/label')
@label_b.input(schema.LabelIn)
@rol.require_role("Operador")
def post_label(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        res = label_model.insert_label(username, **json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert label",
                    "error_description": "No se pudo insertar la label"
                }
            res = schema.MsgErrorOut().dump(result)
        
        labels = []
        """ for label in res:
            print("label:", label)
            print("label:", label.id_label)
            if label != []: 
                labels.append(LabelXTareaIdOut().dump(label)) """

        data = {
                "data": schema.LabelXTareaIdOut().dump(res, many=True)
            }
        
        
        return data

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    

#################DELETE########################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Label', summary='Baja de Label', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.delete('/label/<string:id>')
@rol.require_role("Operador")
def del_label(id: str):
    try:
        username = g.username
        res = label_model.delete_label(username, id)
        print("res:",res)
        print(type(res))
        if res is None:
           raise error_handling.DataNotFound("Label no encontrada")
        else:
            if (res['status'] == 'error'):
                result = {
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc": "Error en eliminar label",
                    "ErrorMsg": res['message']
                }
                res = schema.MsgErrorOut().dump(result)
            else:
                print("Label eliminada:", res)
                result= res
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
    
################################ LABELS X TAREAS ################################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label por tarea', summary='Consulta de labels por tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label_tarea/<string:id_tarea>')
@label_b.output(schema.LabelXTareaIdCountAllOut)
@rol.require_role("Operador")
def get_label_tarea(id_tarea:str):
    try:
        res, cant = label_model.get_label_by_tarea(id_tarea)
        if res is None:
            raise error_handling.DataNotFound("Label no encontrada")

        data = {
            "count": cant,            
            "data": schema.LabelXTareaIdOut().dump(res, many=True)

        }
        return data
      
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 
         

@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Asignacion de Label a tarea', summary='Asignación de labels', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.put('/label_tarea')
@label_b.input(schema.LabelXTareaIn)
@rol.require_role("Operador")
def put_label_tarea(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        res = label_model.insert_label_tarea(username, **json_data)
        print("res:",res)   
        if res is None:
            result = {
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc": "Error en insert label",
                    "ErrorMsg": "No se pudo insertar la label"
                }
     
            res = schema.MsgErrorOut().dump(result)

        labels = []
        for label in res:
            if label != []: 
                labels.append(schema.LabelXTareaIdOut().dump(label))

        

        # Prepare the response data
        data = {
                "data": labels
            }

        return data
        
        # return LabelXTareaPrueba().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    
    
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.doc(description='Elimina Label de tarea', summary='Eliminación de labels', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.delete('/label_tarea/<string:id>')
@rol.require_role("Operador")
def delete_label_tarea(id: str):

    try:
        username = g.username
        res = label_model.delete_label_tarea_model(username, id) 
        if res is None:
            raise error_handling.DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id label x tarea": id,
                    } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    


@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Busca todas las etiquetas que existen activas para un grupo base', summary='Búsqueda de labels activas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label_grupo/<string:ids_grupos_base>')
@rol.require_role("Operador")
def get_active_labels_grupo(ids_grupos_base: str):
    try:
        # Fetch active labels and count
        res, cant = label_model.get_active_labels(ids_grupos_base)

        if res is None:
            result = {
                "valido": "fail",
                "code": 800,
                "error": "Error en obtener etiquetas",
                "error_description": "No se encontraron etiquetas activas"
            }
            return schema.MsgErrorOut().dump(result)

        # Serialize each label and append to the list
        labels = []
        for label in res:
            if label != []: 
                labels.append(schema.LabelAllOut().dump(label, many=True))

        # Prepare the response data
        data = {
            "count": str(cant),
            "data": labels
        }

        return data

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)