from apiflask import APIBlueprint
import models.grupo_model as grupo_model
import schemas.schemas as schemas
import common.error_handling as error_handling
import common.exceptions as exceptions
import common.auth as auth_token
from flask import request, g

herarquia_b = APIBlueprint('herarquia_blueprint', __name__)

#################Before requests ##################
@herarquia_b.before_request
def before_request():
    if request.method == 'OPTIONS':
        return  # Skip custom logic for OPTIONS requests
    
    jsonHeader = auth_token.verify_header() or {}
    g.username = jsonHeader.get('user_name', '')
    g.type = jsonHeader.get('type', '')
    g.rol = jsonHeader.get('user_rol', '')
####################################################

@herarquia_b.doc(description='Listado de Grupos padres - Hijos', summary='Grupos padres - hijos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@herarquia_b.get('/herarquias')
#@herarquia_b.output(GroupHOut(many=True))
def get_gruposh():
    try:
        #res=get_grupos_herarquia()
        res=grupo_model.get_grupos_herarquia_labels()
        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result

        res = {
                "data": schemas.GroupHOut().dump(res, many=True)
            }
        
        
        return res
       
    
    except Exception as err:
        raise exceptions.ValidationError(err)   
    
@herarquia_b.doc(description='Listado de Grupos padres e hijos con niveles', summary='Grupos Padres - Hijos con Niveles', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})    
@herarquia_b.get('/niveles_grupos')
#@herarquia_b.output(HerarquiaOut(many=True))
def get_niveles():
    try:
        #res=get_grupos_herarquia()
        res=grupo_model.get_grupos_recursivo()
        print(res)
        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"No existen jerarquías de grupos",
                } 
            
            return result
        res = {
                "data": schemas.HerarquiaOut().dump(res, many=True)
            }
        
        return res 
 
    
    except Exception as err:
        raise exceptions.ValidationError(err)       


@herarquia_b.get('/herarquias_all')
@herarquia_b.input(schemas.HerarquiaGroupGroupInput, location='query')
#@herarquia_b.output(HerarquiaAllOut(many=True))
def herarquias_all_(query_data: dict):
    try:
        #res=get_grupos_herarquia()
        eliminado=None
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')

        res=grupo_model.get_grupos_all(eliminado)

        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"No existen jerarquías de grupos",
                } 
            return result
        res = {
                "data": schemas.HerarquiaAllOut().dump(res, many=True)
            }
        
        return res 
 
    
    except Exception as err:
        raise exceptions.ValidationError(err)       







