from datetime import date, timedelta
from schemas.schemas import TipoNotaIn, NotaGetIn, TipoNotaOut, NotaIn, NotaOut, NotaCountOut, NotaIdOut, MsgErrorOut, PageIn, TipoNotaCountOut, NotaCountAllOut, NotaAllOut, NotaPatchIn, NotaIdOut
from models.nota_model import get_all_nota, get_all_tipo_nota, get_nota_by_id, insert_nota, delete_nota, delete_tipo_nota, update_nota, insert_tipo_nota
from common.error_handling import DataError, DataNotFound, ValidationError
from models.alch_model import Usuario, Rol, Nota
#from flask_jwt_extended import jwt_required
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from sqlalchemy.orm import scoped_session
from common.usher import get_roles
from common.auth import verify_header
import uuid
import json
from flask import g

nota_b = APIBlueprint('nota_blueprint', __name__)
#################Before requests ##################
# @nota_b.before_request
# def before_request():
#     if not verificar_header():
#         #raise UnauthorizedError("Token o api-key no validos")   
#         print("Token o api key no validos") 

@nota_b.before_request
def before_request():
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


####################TIPO DE NOTA######################
@nota_b.doc(description='Consulta de Tipos de Notas', summary='Tipos de Notas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/tipo_nota')
@nota_b.output(TipoNotaCountOut)
@nota_b.input(PageIn, location='query')
def get_tipoNotas(query_data: dict):
    try:
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = get_all_tipo_nota(page,per_page)
        
        data = {
                "count": cant,
                "data": TipoNotaOut().dump(res, many=True)
            }
        
        
        return data
    
   
    except Exception as err:
        raise ValidationError(err)    
 

@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Tipos de Notas', summary='Alta de Tipo de Nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.post('/tipo_nota')
@nota_b.input(TipoNotaIn)
def post_tipo_nota(json_data: dict):
    try:
        print('insertando nuevo tipo de notas')
        username = g.username
        res = insert_tipo_nota(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el tipo de nota"
                }
            res = MsgErrorOut().dump(result)
            return res
        
        
        return TipoNotaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)  

@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tipo de Nota', summary='Baja de tipo de nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.delete('/tipo_nota/<string:id>')
#@nota_b.output(MsgErrorOut)
def del_tipo_nota(id: str):
    try:
        username = g.username
        res = delete_tipo_nota(username, id)
        if res is None:
            raise DataNotFound("Tipo de nota no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de nota": id,
                    "Tipo de nota": res.nombre
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)

################################ NOTAS ################################
@nota_b.doc(description='Consulta de nota', summary='Consulta de notas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/nota')
@nota_b.input(NotaGetIn, location='query')
@nota_b.output(NotaCountOut)
def get_notas(query_data: dict):
    try:
        page = 1
        per_page = int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        cant = 0
        titulo = ""
        eliminado = None
        id_tipo_nota = None
        id_user_creacion = None
        id_tarea = None
        fecha_desde=datetime.strptime("01/01/1900","%d/%m/%Y").replace(hour=0, minute=0, second=0)
        fecha_hasta=datetime.now()

        if request.args.get('page') is not None:
            print("page:",request.args.get('page'))
            page = int(request.args.get('page'))
        if request.args.get('per_page') is not None:
            per_page = int(request.args.get('per_page'))
        if request.args.get('id_user_creacion') is not None:
            id_user_creacion = request.args.get('id_user_creacion')       
        if request.args.get('titulo') is not None:
            titulo = request.args.get('titulo')
        if request.args.get('id_tipo_nota') is not None:
            id_tipo_nota = request.args.get('id_tipo_nota') 
        if request.args.get('id_tarea') is not None:
            id_tarea = request.args.get('id_tarea') 
        if request.args.get('eliminado') is not None:
            eliminado = request.args.get('eliminado')           
        if request.args.get('fecha_desde') is not None:
            fecha_desde = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta') is not None:
            fecha_hasta = request.args.get('fecha_hasta') 

        res, cant = get_all_nota(page, per_page, titulo, id_tipo_nota, id_tarea, id_user_creacion, fecha_desde, fecha_hasta, eliminado)    

        data = {
            "count": cant,
            "data": NotaAllOut().dump(res, many=True)
        }
        
        
        return data
    
    except ValidationError as err:
        print(f"Validation error: {err}")
        return {"error": str(err)}, 400
    except Exception as err:
        print(f"Unexpected error: {err}")
        raise ValidationError(err)


@nota_b.doc(description='Consulta de nota por ID', summary='Nota por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/nota/<string:id>')
@nota_b.output(NotaIdOut)
def get_nota(id:str):
    print('nota.py')
    try:
        res = get_nota_by_id(id)
        if res is None:
            raise DataNotFound("Nota no encontrada")

        result = NotaIdOut().dump(res)
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err) 


@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Nota', summary='Alta y asignación de notas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.post('/nota')
@nota_b.input(NotaIn)
@nota_b.output(NotaOut)
def post_nota(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        print("Username:",username)
        res = insert_nota(username, **json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert nota",
                    "error_description": "No se pudo insertar la nota"
                }
            res = MsgErrorOut().dump(result)
        
        return NotaOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)    

#################DELETE########################
@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Nota', summary='Baja de Nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.delete('/nota/<string:id>')
# @nota_b.output(NotaIdOut)
def del_nota(id: str):
    try:
        username = g.username
        #username = 'simperiale@mail.jus.mendoza.gov.ar'
        res = delete_nota(username,id)
        print("res:",res)
        if res is None:
           raise DataNotFound("Nota no encontrada")
        else:
            if (type(res) != str):
                result={
                        "Msg": "Registro eliminado",
                        "Id nota": id
                    }
            else:
                result={
                        "Msg":"Registro no eliminado, usuario no autorizado",
                        "Id nota": id
                    }
            return result 

    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)
    except Exception as e:
        current_app.session.rollback()