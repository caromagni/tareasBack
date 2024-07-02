from apiflask import Schema, abort, APIBlueprint
from flask import request
from apiflask.fields import Integer, String, List, Nested
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify
from sqlalchemy.orm import scoped_session
from ..models.alch_model import Grupo,Tarea,Usuario, TareaAsignadaUsuario
from ..models.grupo_model import get_all_grupos, update_grupo, insert_grupo
from ..common.error_handling import ValidationError
from sqlalchemy.sql import text
from typing import List
from ..schemas.schemas import GrupoIn, GrupoOut
import logging

# from apiflask import Schema, abort, APIBlueprint, input, output
# from apiflask.fields import Integer, String
# from apiflask.validators import Length, OneOf
# from flask import current_app, jsonify
# from sqlalchemy.orm import scoped_session, Session
# from ..alch_model import Grupo, Tarea, Usuario, TareaAsignadaUsuario
# from sqlalchemy.sql import text
# from typing import List


groups_b = APIBlueprint('groups_b', __name__)

@groups_b.patch('/grupos/<string:grupo_id>')
@groups_b.input(GrupoIn(partial=True))  # -> json_data
@groups_b.output(GrupoOut)
def update_gr(grupo_id: str, json_data: dict):
    try:
        session: scoped_session = current_app.session
        print("Json data:",json_data)
        res = update_grupo(grupo_id, **json_data)
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

@groups_b.get('/grupo')
#@groups_b.output(GroupCountOut(many=True))
def get_grupos():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    try:
        
        res, cant=get_all_grupos(page,page_size)
       
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

# @groups_b.get('/grupos')
# #@groups_b.output()
# def get_grupos():
#     page = request.args.get('page', default=1, type=int)
#     page_size = request.args.get('page_size', default=10, type=int)
        
#     try:
#         logging.info("Fetching grupos...")
#         res,total_count=get_all_grupos(page,page_size)
#         print("does this have something?")
#         print(len(res))
#         data = {
#                 "count": total_count,
#                 "data": GrupoOut().dump(res, many=True)
#             }
#         if res is None or len(res) == 0:
            
#             result={
#                     "valido":"fail",
#                     "ErrorCode": 800,
#                     "ErrorDesc":"Grupo no encontrado",
#                     "ErrorMsg":"No se encontraron datos de grupos"
#                 } 
#             return result

#         return {"data": res, "total_count": total_count} 
    
#     except Exception as err:
#         logging.error(f"Error fetching grupos: {err}")
#         raise ValidationError(err)                                           


@groups_b.get('/tareas/<string:tarea_id>/usuarios_asignados')
def get_usuarios_asignados(tarea_id:str):
    try:    
        session: scoped_session = current_app.session
        
        usuarios = session.query(Usuario)\
                        .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                        .filter(TareaAsignadaUsuario.id_tarea == tarea_id)\
                        .all()
        
        return jsonify([{
            'id': str(usuario.id),
            'fecha_actualizacion': usuario.fecha_actualizacion,
            'id_user_actualizacion': str(usuario.id_user_actualizacion),
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'id_persona_ext': str(usuario.id_persona_ext)
        } for usuario in usuarios])
    
    except Exception as err:
        raise ValidationError(err)
    
#################POST####################
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