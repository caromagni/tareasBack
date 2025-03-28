from datetime import date, timedelta
from schemas.schemas import LabelGetIn, LabelIn, LabelOut, LabelCountOut, LabelXTareaPatchIn, LabelIdOut, MsgErrorOut, LabelXTareaIdOut, LabelXTareaOut, LabelXTareaIn, PageIn, LabelXTareaIdCountAllOut, LabelCountAllOut, LabelAllOut, LabelPatchIn, LabelIdOut
from models.label_model import get_all_label, get_label_by_id, delete_label_tarea_model, get_active_labels, insert_label_tarea,  insert_label, delete_label, update_label, get_label_by_tarea
from common.error_handling import DataError, DataNotFound, ValidationError
from models.alch_model import Usuario, Rol, Label
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from common.usher import get_roles
from common.auth import verify_header
import uuid
import json
from flask import jsonify, request
from flask import g
from alchemy_db import db
import traceback

label_b = APIBlueprint('label_blueprint', __name__)

# ###############
@label_b.before_request
def before_request():
    print("label.py - before_request -", request.method)
    print("encabezados:",request.headers)
    if request.method == 'OPTIONS':
        print('grupo.py')
        print("Solicitud OPTIONS recibida, permitiendo sin autenticación")
        return jsonify({"message": "CORS preflight handled"}), 200
    
    
    jsonHeader = verify_header()
    
    if jsonHeader is None:
        #if not verificar_header():
            #raise UnauthorizedError("Token o api-key no validos")   
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin
# ####################################################

################################ ETIQUETAS ################################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label', summary='Consulta de labels por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label')
@label_b.input(LabelGetIn, location='query')
@label_b.output(LabelCountOut)
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
        id_grupo_padre = None
        #fecha_desde = "01/01/1900"
        #fecha_hasta = datetime.now().strftime("%d/%m/%Y")
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

        res, cant = get_all_label(username, page, per_page, nombre, id_grupo_padre, id_tarea, id_user_creacion, fecha_desde, fecha_hasta, eliminado, label_color)    
        data = {
            "count": cant,
            "data": LabelAllOut().dump(res, many=True)
        }
        
        
        return data
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 


@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label por ID', summary='Label por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label/<string:id>')
@label_b.output(LabelIdOut)
def get_label(id:str):
    print('label.py')
    try:
        res = get_label_by_id(id)
        if res is None:
            raise DataNotFound("Label no encontrada")

        result = LabelIdOut().dump(res)
        
        return result
 
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 


@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Label', summary='Alta de label', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.post('/label')
@label_b.input(LabelIn)
@label_b.output(LabelOut)
def post_label(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        res = insert_label(username, **json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert label",
                    "error_description": "No se pudo insertar la label"
                }
            res = MsgErrorOut().dump(result)
        
        return LabelOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    

#################DELETE########################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Label', summary='Baja de Label', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.delete('/label/<string:id>')
def del_label(id: str):
    try:
        username = g.username
        res = delete_label(username, id)
        print("res:",res)
        if res is None:
           raise DataNotFound("Label no encontrada")
        else:
            print("Label eliminada:", res)
            result={
                    "Msg":"Registro eliminado",
                    "Id label": id,
                    "nombre": res.nombre
                } 
        
        return result
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)
    
################################ LABELS X TAREAS ################################
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de label por tarea', summary='Consulta de labels por tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label_tarea/<string:id_tarea>')
@label_b.output(LabelXTareaIdCountAllOut)
def get_label_tarea(id_tarea:str):
    try:
        res, cant = get_label_by_tarea(id_tarea)
        if res is None:
            raise DataNotFound("Label no encontrada")

        data = {
            "count": cant,            
            "data": LabelXTareaIdOut().dump(res, many=True)

        }
        print("result:",data) 
        
        return data
        #return jsonify({
        #'status': 'success',
        #'data': data
    #})      
 
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err) 
         

@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Asignacion de Label a tarea', summary='Asignación de labels', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.put('/label_tarea')
@label_b.input(LabelXTareaIn)
@label_b.output(LabelXTareaOut)
def put_label_tarea(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        res = insert_label_tarea(username, **json_data)
        print("res:",res)   
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert label",
                    "error_description": "No se pudo insertar la label"
                }
            res = MsgErrorOut().dump(result)
        
        return LabelXTareaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    
    
@label_b.doc(description='Elimina Label de tarea', summary='Eliminación de labels', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.put('/label_tarea_del/')
@label_b.input(LabelXTareaPatchIn)
@label_b.output(LabelXTareaIdOut)
def delete_label_tarea(json_data: dict):
    try:
        username = g.username
        print("##"*50)
        print(json_data)
        print("#"*50)
        res = delete_label_tarea_model(username, **json_data)
        print("res:",res)   
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en delete label",
                    "error_description": "No se pudo eliminar la etiqueta"
                }
            res = MsgErrorOut().dump(result)
        
        return LabelXTareaIdOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)    
    
@label_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Busca todas las etiquetas que existen activas para un grupo base', summary='Búsqueda de labels activas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@label_b.get('/label_grupo/<string:ids_grupos_base>')
# @label_b.input(LabelXTareaGetIn)
# @label_b.output(LabelCountAllOut)
def get_active_labels_grupo(ids_grupos_base:str):
    try:
        labels = []
        res, cant = get_active_labels(ids_grupos_base)
        for label in res:           
            # data = {
            #     'data': LabelAllOut().dump(label, many=True)
            # }
            labels.append(LabelAllOut().dump(label, many=True))
        print("array labels formateado:",labels)   
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en delete label",
                    "error_description": "No se pudo eliminar la etiqueta"
                }
            res = MsgErrorOut().dump(result)
        
            return LabelAllOut().dump(res)
    
        # data = {
        #         "count": str(cant),            
        #         "data": LabelAllOut().dump(res, many=True)

        #     }
        # print("result:",data) 
        print('saliendo del label_b.get /label_grupo/<string:ids_grupos_base>')
        return labels
    
    except Exception as err:
        print(traceback.format_exc())
        raise ValidationError(err)