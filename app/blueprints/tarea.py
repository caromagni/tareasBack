from datetime import date, timedelta
from ..schemas.schemas import TipoTareaIn, TipoTareaOut, TareaIn, TareaOut, TareaUsuarioIn, TareaUsuarioOut, TareaIdOut, MsgErrorOut, PageIn, TipoTareaCountOut
from ..models.tarea_model import get_all_tareas, get_all_tipo_tareas, get_tarea_by_id, insert_tipo_tarea, usuarios_tarea, insert_tarea, delete_tarea, insert_usuario_tarea, delete_tipo_tarea
from app.common.error_handling import DataError, DataNotFound, ValidationError
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request


tarea_b = APIBlueprint('tarea_blueprint', __name__)
###############
@tarea_b.before_request
def before_request():
    
    print("Antes de la petición")
    print(request.headers)

####################TIPO DE TAREA######################
@tarea_b.doc(description='Listado de Tipos de Tareas', summary='Tipos de Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tipo_tareas')
@tarea_b.output(TipoTareaCountOut)
@tarea_b.input(PageIn, location='query')
def get_tipoTareas(query_data: dict):
    try:
        page=1
        per_page=10
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = get_all_tipo_tareas(page,per_page)
    
        
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

@tarea_b.doc(description='Baja de Tipo de Tarea', summary='Baja de tipo de tarea', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.delete('/tipo_tarea/<string:id>')
#@tarea_b.output(MsgErrorOut)
def del_tipo_tarea(id: str):
    try:
        res = delete_tipo_tarea(id)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Tipo de tarea no encontrado",
                    "ErrorMsg":"No se encontró el tipo de tarea"
                } 
            res = MsgErrorOut().dump(result)
            return res
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de tarea": id,
                    "Tipo de tarea": res.nombre
                } 
        
        return result
    
    except Exception as err:
        raise ValidationError(err)
    
################################TAREAS################################
@tarea_b.doc(description='Listado de Tareas', summary='Tareas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@tarea_b.get('/tareas')
@tarea_b.input(PageIn, location='query')
def get_tareas(query_data: dict):
    try:
        page=1
        per_page=10
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res,cant = get_all_tareas(page,per_page)    
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
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert usuario_tarea",
                    "ErrorMsg":msg
                } 
            res = MsgErrorOut().dump(result)
            return res

        result={
                    "valido":"true",
                    "id_usuario": res.id_usuario,
                    "id_tarea": res.id_tarea,
                    "Msg":"Tarea asignada"
                } 
        
        return result
    
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