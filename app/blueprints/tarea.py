from datetime import date, timedelta
from ..schemas.schemas import TipoTareaIn, TipoTareaOut, TareaIn, TareaOut, TareaUsuarioOut, TareaIdOut, MsgErrorOut, PageIn
from ..models.tarea_model import get_all_tareas, get_all_tipo_tareas, get_tarea_by_id, insert_tipo_tarea, usuarios_tarea, insert_tarea, delete_tarea
from app.common.error_handling import ObjectNotFound, InvalidPayload, ValidationError
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request


tarea_b = APIBlueprint('tarea_blueprint', __name__)

@tarea_b.doc(description='Listado de Tipos de Tareas', summary='Tipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tareas')
#@tarea_b.output(TipoTareaOut(many=True))
@tarea_b.input(PageIn, location='query')
def get_tipoTareas(query_data: dict):
    try:
        first=1
        rows=10
        if(request.args.get('first') is not None):
            first=int(request.args.get('first'))
        if(request.args.get('rows') is not None):
            rows=int(request.args.get('rows'))

        res, cant = get_all_tipo_tareas(first,rows)
    
        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            res = MsgErrorOut().dump(result, )
            return res
        
        data = {
                "count": cant,
                "data": TipoTareaOut().dump(res, many=True)
            }
        
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
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert tipo_tarea",
                    "ErrorMsg":"No se pudo insertar el tipo de tarea"
                } 
            res = MsgErrorOut().dump(result)
            return res
        return TipoTareaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)  


@tarea_b.doc(description='Listado de Tareas', summary='Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tareas')
@tarea_b.input(PageIn, location='query')
def get_tareas(query_data: dict):
    try:
        first=1
        rows=10
        if(request.args.get('first') is not None):
            first=int(request.args.get('first'))
        if(request.args.get('rows') is not None):
            rows=int(request.args.get('rows'))

        res,cant = get_all_tareas(first,rows)    
        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            res = MsgErrorOut().dump(result)
            return res

        data = {
                "count": cant,
                "data": TareaOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Consulta de tarea por ID', summary='Tarea por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea/<string:id_tarea>')
def get_tarea(id_tarea:str):
    try:
        res = get_tarea_by_id(id_tarea)    
        if res is None or len(res) == 0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontraron datos de tareas"
                } 
            res = MsgErrorOut().dump(result)
            return res

        return TareaIdOut().dump(res, many=True)
    
    except Exception as err:
        raise ValidationError(err) 

@tarea_b.doc(description='Usuarios asignados', summary='Usuario asignado a una Tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tarea_usr/<string:tarea_id>')
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
            res = MsgErrorOut().dump(result)
            return res

        return TareaUsuarioOut().dump(res, many=True)

    
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
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tarea no encontrada",
                    "ErrorMsg":"No se encontró la tarea a eliminar"
                } 
            res = MsgErrorOut().dump(result)
            return res
        else:
            print("Tarea eliminada:", res)
            result={
                    "Msg":"Registro eliminado",
                    "Id tarea": id
                    #"tarea": res.titulo
                } 
        
        return result
    
    except Exception as err:
        raise ValidationError(err)    