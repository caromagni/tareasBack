from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify, request
from sqlalchemy.orm import scoped_session
from models.alch_model import Grupo,Usuario
from models.usuario_model import get_all_usuarios, get_all_usuarios_detalle, get_grupos_by_usuario, insert_usuario, update_usuario, get_usuario_by_id, delete_usuario
from schemas.schemas import  UsuarioIn, UsuarioInPatch, UsuarioGetIn, UsuarioCountOut,UsuarioCountAllOut, UsuarioOut, GroupsUsuarioOut, UsuarioIdOut, UsuarioAllOut
from common.error_handling import ValidationError, DataError, DataNotFound
from common.auth import verificar_header
from datetime import datetime
import requests

usuario_b = APIBlueprint('usuario_blueprint', __name__)
#################Before requests ##################
@usuario_b.before_request
def before_request():
    if not verificar_header():
        #raise UnauthorizedError("Token o api-key no validos")   
        print("Token o api key no validos")

#################GET GRUPOS POR USUARIO####################    
@usuario_b.doc(description='Listado de Grupos al que pertenece un Usuario', summary='Grupos por Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.get('/grupo_usuario/<string:id_usuario>')
#@usuario_b.output(GroupsUsuarioOut(many=True))
def get_grupos_by_usr(id_usuario: str):
    try:
        res = get_grupos_by_usuario(id_usuario)
        print("res:",res)
        if res is None or len(res)==0:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario sin grupos",
                    "ErrorMsg":"No se encontraron datos de usuarios"
                } 
            return result
        
        current_app.session.remove()    
        #return res
        return GroupsUsuarioOut().dump(res, many=True)
    
    except Exception as err:
        raise ValidationError(err) 
    
#####################POST#########################
@usuario_b.doc(description='Alta de nuevo Usuario', summary='Alta de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.post('/usuario')
@usuario_b.input(UsuarioIn)
#@usuario_b.output(UsuarioOut)
def post_usuario(json_data: dict):
    try:
        print('inserta usuario')
        res=""
        res = insert_usuario(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert usuario",
                    "ErrorMsg":"No se pudo insertar el usuario"
                } 
            return result
            
        return UsuarioOut().dump(res)
    
    except Exception as err:
        raise ValidationError(err)
    
#################UPDATE####################
@usuario_b.doc(description='Update de Usuario', summary='Update de Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.patch('/usuario/<string:usuario_id>')
@usuario_b.input(UsuarioInPatch)
#@usuario_b.output(UsuarioOut)
def patch_usuario(usuario_id: str, json_data: dict):
    try:
        
        res = update_usuario(usuario_id, **json_data)
        if res is None:
            print("No hay datos que modificar")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario no encontrado",
                    "ErrorMsg":"No se encontró el usuario a modificar"
                } 
            return result
        return UsuarioOut().dump(res)    
        
    
    except Exception as err:
        raise ValidationError(err)

###############GET BY ID####################
@usuario_b.doc(description='Consulta de usuario. Ejemplo de url: /usuario?id=id_usuario', summary='Consulta de usuario por id', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario/<string:id>')
#@usuario_b.output(UsuarioIdOut(many=True))
def get_usuario_id(id: str):
        res = get_usuario_by_id(id)
        if res is None or len(res)==0:
            print("Usuario no encontrado")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Usuario no encontrado",
                    "ErrorMsg":"No se encontró el usuario"
                } 
            return result
        current_app.session.remove()
        return UsuarioIdOut().dump(res, many=True)
        

#############GET CON PARAMETROS######################## 
# CONSULTA SIMPLE
#######################################################
@usuario_b.doc(description='Consulta de usuarios', summary='Consulta simple de usuarios por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario')
@usuario_b.input(UsuarioGetIn, location='query')
@usuario_b.output(UsuarioCountOut)
def get_usuario(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nombre=""
        apellido=""
        dni=""
        username=""
        id_grupo=None
        eliminado= None
        suspendido=None
        cant=0
        
        print("query_data:",query_data)
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_grupo') is not None):
            id_grupo=request.args.get('id_grupo')    
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('apellido') is not None):
            apellido=request.args.get('apellido')  
        if(request.args.get('dni') is not None):
            dni=request.args.get('dni') 
        if(request.args.get('username') is not None):
            username=request.args.get('username')           
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')
        if(request.args.get('suspendido') is not None):
            suspendido=request.args.get('suspendido')    

        res, cant=get_all_usuarios(page, per_page, nombre, apellido, id_grupo, dni, username, eliminado, suspendido)

        data = {
                "count": cant,
                "data": UsuarioOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
        raise ValidationError(err) 
    
#####################DETALLE DE USUARIOS#######################   
@usuario_b.doc(description='Consulta de usuarios con sus grupos y tareas', summary='Consulta detallada de usuarios por parámetros', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@usuario_b.get('/usuario_detalle')
@usuario_b.input(UsuarioGetIn, location='query')
@usuario_b.output(UsuarioCountAllOut)
def get_usuarios_detalle(query_data: dict):
    try:
        page=1
        per_page=int(current_app.config['MAX_ITEMS_PER_RESPONSE'])
        nombre=""
        apellido=""
        id_grupo=None
        dni=""
        username=""
        cant=0
        eliminado= None
        suspendido=None
        
        print("query_data:",query_data)
        
        if(request.args.get('page') is not None):
            page=int(request.args.get('page'))
        if(request.args.get('per_page') is not None):
            per_page=int(request.args.get('per_page'))
        if(request.args.get('id_grupo') is not None):
            id_grupo=request.args.get('id_grupo')    
        if(request.args.get('nombre') is not None):
            nombre=request.args.get('nombre')
        if(request.args.get('apellido') is not None):
            apellido=request.args.get('apellido')    
        if(request.args.get('dni') is not None):
            dni=request.args.get('dni')
        if(request.args.get('username') is not None):
            username=request.args.get('username')
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')
        if(request.args.get('suspendido') is not None):
            suspendido=request.args.get('suspendido')                

        res, cant=get_all_usuarios_detalle(page, per_page, nombre, apellido, id_grupo, dni, username, eliminado, suspendido)

        data = {
                "count": cant,
                "data": UsuarioAllOut().dump(res, many=True)
            }
        
        current_app.session.remove()
        return data
    
    except Exception as err:
        raise ValidationError(err)  
######################DELETE######################
@usuario_b.doc(description='Baja de un Usuario', summary='Baja de un Usuario', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@usuario_b.delete('/usuario/<string:id>')
#@groups_b.output(GroupOut)
def del_usuario(id: str):
    try:
        res = delete_usuario(id)
        if res is None:
            raise DataNotFound("Usuario no encontrado")
            
        else:
            result={
                    "Msg":"Registro eliminado",
                    "Id usuario": id,
                    "usuario": res.nombre
                } 
        
        return result
    
    except DataNotFound as err:
        raise DataError(800, err)
    except Exception as err:
        raise ValidationError(err)

##########Prueba Roles################
@usuario_b.get('/usuario_rol/<string:token>')
#@usuario_b.output(UsuarioOut)
def get_rol_usr(token: str):
    token='eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJsTVhjMjlEdmFtdEZhZ2tiUWoxQ2Fib1pqSk9OY1lxTE5teE1CWERIZmx3In0.eyJleHAiOjE3MjcyNjMzOTEsImlhdCI6MTcyNTk2OTA1OCwiYXV0aF90aW1lIjoxNzI1OTY3MzkxLCJqdGkiOiJhZDU5MzlhNS03NjkwLTQwNmUtYmZiMi1hNWM1OTMzZTg1MzciLCJpc3MiOiJodHRwczovL2Rldi1hdXRoLnBqbS5nb2IuYXIvYXV0aC9yZWFsbXMvZGV2b3BzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5MWFiOTA5LTMzNzQtNDU2YS04Y2U5LTdiZDJkZjExOWQwYSIsInR5cCI6IkJlYXJlciIsImF6cCI6InVzaGVyIiwibm9uY2UiOiI2MGE5ZGRlZS01ZGY3LTQxNjYtYjk3Ny0zMTBhZDk1MWI3NmIiLCJzZXNzaW9uX3N0YXRlIjoiYTFiMDA2NWQtMzhiOC00YTFmLTk2YzAtMTg0NmU0MzliY2VjIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ1c2hlciI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImExYjAwNjVkLTM4YjgtNGExZi05NmMwLTE4NDZlNDM5YmNlYyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlNpbHZpYSBTLiBJbXBlcmlhbGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzaW1wZXJpYWxlIiwiZ2l2ZW5fbmFtZSI6IlNpbHZpYSBTLiIsImZhbWlseV9uYW1lIjoiSW1wZXJpYWxlIiwiZW1haWwiOiJzaW1wZXJpYWxlQG1haWwuanVzLm1lbmRvemEuZ292LmFyIn0.OnfYhSdrZfz7bL6r1sy3-6DCTeFH8G7VesMbGWh4XGCiFM2IuqpXldrjlhKWI8ahRTKAJEdvXlBn8ht5JtGY1y-ee8RbeVrxtmjmmBHJt-nejXNflhsoXcF_20r3rMyfvM210vtFaUy26YZi7ttIBS6mQaql4Y_DPgL_wAMVoa431ThaDw3Kijcl7nJQ40fBeti0YgiwS3KKvEamf8E-CbX1gCUNoZX_pyP4dWSh9kduNh_K0QU4uqyvVzwyt8_jikcPxWmHQ9SHh31M5_31b6uEgSXx7QqKECs-VzH4GnkdZB3TwRb7fnj0D4jSuSvuUp5Wk_lPcrdNMDX4RxA84w'
    url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas'
    r=requests.get(url,headers={'Authorization': 'Bearer '+token})
    resp=r.json()
    print("resp:",resp)
    return resp        