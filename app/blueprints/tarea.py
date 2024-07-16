from datetime import date, timedelta
from ..schemas.schemas import TipoTareaIn, TipoTareaOut, TareaIn, TareaOut, TareaUsuarioOut
from ..models.tarea_model import get_all_tareas, get_all_tipo_tareas, insert_tipo_tarea, usuarios_tarea, insert_tarea
from app.common.error_handling import ObjectNotFound, InvalidPayload, ValidationError
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint


tarea_b = APIBlueprint('tarea_blueprint', __name__)

@tarea_b.doc(description='Listado de Tipos de Tareas', summary='Tipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tareas')
@tarea_b.output(TipoTareaOut(many=True))
def get_tipoTareas():
    
    try:
        res = get_all_tipo_tareas()
    
        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err)    

@tarea_b.doc(description='Alta de un nuevo Tipos de Tareas', summary='Alta de Tipo de Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tipo_tarea')
@tarea_b.input(TipoTareaIn)
@tarea_b.output(TipoTareaOut)
def post_tipo_tarea(json_data: dict):
    try:
    
        res = insert_tipo_tarea(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert tipo_tarea",
                    "ErrorMsg":"No se pudo insertar el tipo de tarea"
                } 
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err)  
     
@tarea_b.doc(description='Listado de Tareas', summary='Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tareas')
@tarea_b.output(TareaOut(many=True))
def get_tareas():
    try:
        res = get_all_tareas()    
        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tareas/<string:tarea_id>/usuarios_asignados')
@tarea_b.output(TareaUsuarioOut(many=True))
def get_usuarios_asignados(tarea_id:str):
    try:    
        print("Usuarios asignados a tarea:", tarea_id)
        res = usuarios_tarea(tarea_id)

        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            return result

        return res

    
    except Exception as err:
        raise ValidationError(err)
    
@tarea_b.doc(description='Alta de Tarea', summary='Alta y asignación de tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.post('/tarea')
@tarea_b.input(TareaIn)
@tarea_b.output(TareaOut)
def post_tarea(json_data: dict):
    try:
    
        res = insert_tarea(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert tarea",
                    "ErrorMsg":"No se pudo insertar la tarea"
                } 
            return result
        return res
    
    except Exception as err:
        raise ValidationError(err)        