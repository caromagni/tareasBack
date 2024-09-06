from datetime import date, timedelta
from ..schemas.schemas import TipoTareaIn, TareaGetIn, TipoTareaOut, TareaIn, TareaOut, TareaCountOut, TareaUsuarioIn, TareaUsuarioOut, TareaIdOut, MsgErrorOut, PageIn, TipoTareaCountOut
from ..models.tarea_model import get_all_tarea, get_all_tipo_tarea, get_tarea_by_id, insert_tipo_tarea, usuarios_tarea, insert_tarea, delete_tarea, insert_usuario_tarea, delete_tipo_tarea
from app.common.error_handling import DataError, DataNotFound, ValidationError
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime

tarea_b = APIBlueprint('tarea_blueprint', __name__)
###############
@tarea_b.before_request
def before_request():
    
    print("Antes de la petición")
    print(request.headers)

####################TIPO DE TAREA######################
@tarea_b.doc(description='Consulta de Tipos de Tareas', summary='Tipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tarea')
@tarea_b.output(TipoTareaCountOut)
@tarea_b.input(PageIn, location='query')
def get_tipoTareas(query_data: dict):
    try:
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        print("query_data:",query_data)
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = get_all_tipo_tarea(page,per_page)
    
        
        data = {
                "count": cant,
                "data": TipoTareaOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
   
    except Exception as err:
        raise ValidationError(err)    
 

@tarea_b.doc(description='Alta de un nuevo Tipos de Tareas', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(TipoTareaIn)
def post_tipo_tarea(json_data: dict):
    try:
    
        res = insert_tipo_tarea(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el tipo de tarea"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return TipoTareaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)  

@tarea_b.doc(description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        res = delete_tipo_tarea(id)
        if res is None:
            raise DataNotFound("Tipo de tarea no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)
    
################################TAREAS################################
@tarea_b.doc(description='Consulta de tarea', summary='Consulta de tareas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea')
@tarea_b.input(TareaGetIn, location='query')
@tarea_b.output(TareaCountOut)
def get_tareas(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant=0
        titulo=""
        id_expediente=None
        id_tipo_tarea=None
        id_usuario_asignado=None
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_usuario_asignado') is not None):
            id_usuario_asignado=request.args.get('id_usuario_asignado')    
        if(request.args.get('titulo') is not None):
            titulo=request.args.get('titulo')
        if(request.args.get('id_tipo_tarea') is not None):
            id_tipo_tarea=request.args.get('id_tipo_tarea') 
        if(request.args.get('id_expediente') is not None):
            id_expediente=request.args.get('id_expediente')     
        if(request.args.get('fecha_desde') is not None):
            fecha_desde=request.args.get('fecha_desde')
        if(request.args.get('fecha_hasta') is not None):
            fecha_hasta=request.args.get('fecha_hasta') 
        res,cant = get_all_tarea(page,per_page, titulo, id_expediente, id_tipo_tarea, id_usuario_asignado, fecha_desde, fecha_hasta)    

        data = {
                "count": cant,
                "data": TareaOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea/<string:id_tarea>')
@tarea_b.output(TareaIdOut(many=True))
def get_tarea(id_tarea:str):
    try:
        res = get_tarea_by_id(id_tarea) 
        if res is None or len(res) == 0:
            raise DataNotFound("Tarea no encontrada")

        current_app.session.remove()
        return res
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_usr/<string:tarea_id>')
@tarea_b.output(TareaUsuarioOut(many=True))
def get_usuarios_asignados(tarea_id:str):
    try:    
        print("Usuarios asignados a tarea:", tarea_id)
        res = usuarios_tarea(tarea_id)

        current_app.session.remove()
        return res

    except Exception as err:
        raise ValidationError(err)

@tarea_b.doc(description='Asignación de tarea a usuario', summary='Asignación a usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tarea_usr')
@tarea_b.input(TareaUsuarioIn)
#@tarea_b.output(TareaOut)
def post_usuario_tarea(json_data: dict):
    try:
    
        res, msg = insert_usuario_tarea(**json_data)
        if res is None:
            print("Tarea ya asignada")
            result={
                    "valido":"fail",
                    "code": 800,
                    "error_description":"Error en insert usuario_tarea",
                    "error":msg
                } 
            res = MsgErrorOut().dump(result)
            return res

        result={
                    "valido":"true",
                    "id_usuario": res.id_usuario,
                    "id_tarea": res.id_tarea,
                    "Msg":"Tarea asignada"
                } 
        current_app.session.remove()
        return result
    
    except Exception as err:
        raise ValidationError(err)    



@tarea_b.doc(description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tarea')
@tarea_b.input(TareaIn)
@tarea_b.output(TareaOut)
def post_tarea(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        res = insert_tarea(**json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert tarea",
                    "error_description": "No se pudo insertar la tarea"
                }
            res = MsgErrorOut().dump(result)

        return TareaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)    

#################DELETE########################
@tarea_b.doc(description='Baja de Tarea', summary='Baja de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tarea/<string:id>')
def del_tarea(id: str):
    try:
        res = delete_tarea(id)
        print("res:",res)
        if res is None:
           raise DataNotFound("Tarea no encontrada")
        else:
            print("Tarea eliminada:", res)
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)    