from apiflask import APIBlueprint
from models.grupo_model import get_all_herarquia, get_grupos_herarquia_labels, get_grupos_recursivo,get_grupos_all
from typing import List
from schemas.schemas import GroupHOut, HerarquiaGroupGroupOut, HerarquiaGroupGroupInput, HerarquiaOut,HerarquiaAllOut
from common.error_handling import ValidationError
from common.auth import verificar_header
from flask import current_app, request

herarquia_b = APIBlueprint('herarquia_blueprint', __name__)

#################Before requests ##################
@herarquia_b.before_request
def before_request():
    if not verificar_header():
        #raise UnauthorizedError("Token o api-key no validos")   
        print("Token o api key no validos")  
####################################################

@herarquia_b.doc(description='Listado de Grupos padres - Hijos', summary='Grupos padres - hijos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@herarquia_b.get('/herarquias')
#@herarquia_b.output(GroupHOut(many=True))
def get_gruposh():
    try:
        #res=get_grupos_herarquia()
        res=get_grupos_herarquia_labels()
        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result

        res = {
                "data": GroupHOut().dump(res, many=True)
            }
        
        
        return res
       
    
    except Exception as err:
        raise ValidationError(err)   
    
@herarquia_b.doc(description='Listado de Grupos padres e hijos con niveles', summary='Grupos Padres - Hijos con Niveles', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})    
@herarquia_b.get('/niveles_grupos')
#@herarquia_b.output(HerarquiaOut(many=True))
def get_niveles():
    try:
        #res=get_grupos_herarquia()
        res=get_grupos_recursivo()
        print(res)
        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"No existen jerarquías de grupos",
                } 
            
            return result
        res = {
                "data": HerarquiaOut().dump(res, many=True)
            }
        
        return res 
 
    
    except Exception as err:
        raise ValidationError(err)       


@herarquia_b.get('/herarquias_all')
@herarquia_b.input(HerarquiaGroupGroupInput, location='query')
#@herarquia_b.output(HerarquiaAllOut(many=True))
def herarquias_all_(query_data: dict):
    try:
        #res=get_grupos_herarquia()
        eliminado=None
        if(request.args.get('eliminado') is not None):
            eliminado=request.args.get('eliminado')

        res=get_grupos_all(eliminado)

        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"No existen jerarquías de grupos",
                } 
            return result
        res = {
                "data": HerarquiaAllOut().dump(res, many=True)
            }
        
        return res 
 
    
    except Exception as err:
        raise ValidationError(err)       







