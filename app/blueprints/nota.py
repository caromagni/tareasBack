import schemas.schemas as schema
import models.nota_model as nota_model
import common.error_handling as error_handling
import common.auth as auth_token
import decorators.role as rol
import traceback
from apiflask import APIBlueprint
from flask import request, current_app
from datetime import datetime
from flask import g, request
from cache import cache

nota_b = APIBlueprint('nota_blueprint', __name__)
#################Before requests ##################
@nota_b.before_request
def before_request():
    
    jsonHeader = auth_token.verify_header()
    
    if jsonHeader is None:
            user_origin=''
            type_origin=''
    else:
            user_origin = jsonHeader['user_name']
            type_origin = jsonHeader['type']
    
    g.username = user_origin
    g.type = type_origin


####################TIPO DE NOTA######################
@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de Tipos de Notas', summary='Tipos de Notas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/tipo_nota')
@nota_b.output(schema.TipoNotaCountOut)
@nota_b.input(schema.PageIn, location='query')
@rol.require_role("Operador")
def get_tipoNotas(query_data: dict):
    try:
        cant=0
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])

        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))

        res, cant = nota_model.get_all_tipo_nota(page,per_page)
        
        data = {
                "count": cant,
                "data": schema.TipoNotaOut().dump(res, many=True)
            }
        
        
        return data
    
   
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    
 

@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de un nuevo Tipos de Notas', summary='Alta de Tipo de Nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.post('/tipo_nota')
@nota_b.input(schema.TipoNotaIn)
@rol.require_role("Operador")
def post_tipo_nota(json_data: dict):
    try:
        print('insertando nuevo tipo de notas')
        username = g.username
        res = nota_model.insert_tipo_nota(username, **json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "code": 800,
                    "error":"Error en insert grupo",
                    "error_description":"No se pudo insertar el tipo de nota"
                }
            res = schema.MsgErrorOut().dump(result)
            return res
        
        
        return schema.TipoNotaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)  

@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Tipo de Nota', summary='Baja de tipo de nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.delete('/tipo_nota/<string:id>')
#@nota_b.output(MsgErrorOut)
@rol.require_role("Operador")
def del_tipo_nota(id: str):
    try:
        username = g.username
        res = nota_model.delete_tipo_nota(username, id)
        if res is None:
            raise error_handling.DataNotFound("Tipo de nota no encontrado")
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id tipo de nota": id,
                    "Tipo de nota": res.nombre
                } 
        
        return result
    

    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)

################################ NOTAS ################################
@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de nota', summary='Consulta de notas por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/nota')
@nota_b.input(schema.NotaGetIn, location='query')
@nota_b.output(schema.NotaCountOut)
@rol.require_role("Operador")
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

        res, cant = nota_model.get_all_nota(page, per_page, titulo, id_tipo_nota, id_tarea, id_user_creacion, fecha_desde, fecha_hasta, eliminado)    

        data = {
            "count": cant,
            "data": schema.NotaAllOut().dump(res, many=True)
        }
        
        
        return data
    
    except error_handling.ValidationError as err:
        print(traceback.format_exc())
        return {"error": str(err)}, 400
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)


@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Consulta de nota por ID', summary='Nota por ID', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.get('/nota/<string:id>')
@nota_b.output(schema.NotaIdOut)
@rol.require_role("Operador")
def get_nota(id:str):
    print('nota.py')
    try:
        res = nota_model.get_nota_by_id(id)
        if res is None:
            raise error_handling.DataNotFound("Nota no encontrada")

        result = schema.NotaIdOut().dump(res)
        
        return result
    
    except error_handling.DataNotFound as err:
        print(traceback.format_exc())
        raise error_handling.DataError(800, err)
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err) 


@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Alta de Nota', summary='Alta y asignación de notas', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.post('/nota')
@nota_b.input(schema.NotaIn)
@nota_b.output(schema.NotaOut)
@rol.require_role("Operador")
def post_nota(json_data: dict):
    try:
        print("#"*50)
        print(json_data)
        print("#"*50)
        username = g.username
        res = nota_model.insert_nota(username, **json_data)
        if res is None:
            result = {
                    "valido":"fail",
                    "code": 800,
                    "error": "Error en insert nota",
                    "error_description": "No se pudo insertar la nota"
                }
            res = schema.MsgErrorOut().dump(result)
        
        return schema.NotaOut().dump(res)
    
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)    

#################DELETE########################
@nota_b.doc(security=[{'ApiKeyAuth': []}, {'ApiKeySystemAuth': []}, {'BearerAuth': []}], description='Baja de Nota', summary='Baja de Nota', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@nota_b.delete('/nota/<string:id>')
# @nota_b.output(NotaIdOut)
@rol.require_role("Operador")
def del_nota(id: str):
    try:
        username = g.username
        #username = 'simperiale@mail.jus.mendoza.gov.ar'
        res = nota_model.delete_nota(username,id)
        print("res:",res)
        if res is None:
           raise error_handling.DataNotFound("Nota no encontrada")
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

    
    except error_handling.DataNotFound as err:
        print(traceback.format_exc())
        raise error_handling.DataError(800, err)
    except Exception as err:
        print(traceback.format_exc())
        raise error_handling.ValidationError(err)
