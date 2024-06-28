from apiflask import APIBlueprint 
from ..models.alch_model import Grupo,Tarea,Usuario, TareaAsignadaUsuario, HerarquiaGrupoGrupo
from ..models.grupo_model import get_all_grupos, update_grupo, insert_grupo
from ..common.error_handling import ValidationError
from ..schemas.schemas import GrupoIn, GrupoOut, GroupCountOut, PageIn
from flask import request

groups_b = APIBlueprint('groups_blueprint', __name__)

@groups_b.doc(description='Update de un Grupo', summary='Update de un Grupo', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@groups_b.patch('/grupos/<string:grupo_id>')
@groups_b.input(GrupoIn(partial=True))  # -> json_data
@groups_b.output(GrupoOut)
def update_gr(grupo_id: str, json_data: dict):
    try:
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
    
@groups_b.doc(description='Listado de Grupos existentes', summary='Listado de Grupos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})                                           
@groups_b.get('/grupos')
@groups_b.output(GroupCountOut)
def get_grupos():
    try:
        page=int(request.args.get('page'))
        page_size=int(request.args.get('page_size'))
        print("page_size:",page_size)
        print("page:",page)
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