from apiflask import Schema, abort, APIBlueprint
from flask import request
from apiflask.fields import Integer, String, List, Nested
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify
from sqlalchemy.orm import scoped_session
from ..models.grupo_model import get_all_grupos, update_grupo, insert_grupo, get_usuarios_by_grupo
from ..common.error_handling import ValidationError
from sqlalchemy.sql import text
from typing import List
from ..schemas.schemas import GrupoIn, GrupoOut, GroupCountOut, PageIn, UsuariosGrupoOut
import logging


groups_b = APIBlueprint('groups_Blueprint', __name__)



@groups_b.doc(description='Update de un Grupo', summary='Update de un Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupo/<string:id>')
@groups_b.input(GrupoIn(partial=True))  # -> json_data
@groups_b.output(GrupoOut)
def patch_grupo(id: str, json_data: dict):
    try:
        res = update_grupo(id, **json_data)
        if res is None:
            print("No hay datos que modificar")  
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontró el grupo a modificar"
                } 
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err)
    
@groups_b.doc(description='Listado de Grupos existentes. Ejemplo de url: /grupo?first=1&rows=2', summary='Listado de Grupos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupo')
@groups_b.input(PageIn, location='query')
@groups_b.output(GroupCountOut)
def get_grupos(query_data: dict):
    try:
        #page=1
        first=1
        #page_size=10
        rows=10
        if(request.args.get('first') is not None):
            first=int(request.args.get('first'))
        if(request.args.get('rows') is not None):
            rows=int(request.args.get('rows'))

        print("page_size:",rows)
        print("page:",first)
        res, cant=get_all_grupos(first,rows)
        
        
        if res is None or len(res) == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result
       
        data = {
                "count": cant,
                "data": GrupoOut().dump(res, many=True)
            }
        
        return data
    
    except Exception as err:
        raise ValidationError(err)   
    
@groups_b.doc(description='Listado de Usuarios pertenecientes a un grupo', summary='Usuarios por Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/usuarios_grupo/<string:id_grupo>')
#@groups_b.input(PageIn, location='query')
@groups_b.output(UsuariosGrupoOut(many=True))
def get_usrsbygrupo(id_grupo: str):
    try:
        print("id_grupo:",id_grupo)
        res = get_usuarios_by_grupo(id_grupo)
        
        
        if res is None == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo sin usuarios",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result
        
        return res
    
    except Exception as err:
        raise ValidationError(err)  
    
#################POST####################
@groups_b.doc(description='Alta de un Grupo', summary='Alta de un nuevo Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.post('/grupo')
@groups_b.input(GrupoIn)
@groups_b.output(GrupoOut)
def post_grupo(json_data: dict):
    try:
        
        res = insert_grupo(**json_data)
        if res is None:
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Error en insert grupo",
                    "ErrorMsg":"No se pudo insertar el grupo"
                } 
            return result
            
        return res
    
    except Exception as err:
        raise ValidationError(err)    