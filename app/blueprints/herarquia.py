from apiflask import APIBlueprint
from ..models.grupo_model import get_all_herarquia, get_grupos_herarquia_labels, get_grupos_recursivo,get_grupos_all
from typing import List
from ..schemas.schemas import GroupHOut, HerarquiaGroupGroupOut, HerarquiaOut,HerarquiaAllOut
from ..common.error_handling import ValidationError
from flask import current_app

herarquia_b = APIBlueprint('herarquia_blueprint', __name__)

""" @herarquia_b.doc(description='Listado de Grupos padres - hijos', summary='Jerarquía de Grupos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@herarquia_b.get('/herarquias')
@herarquia_b.output(HerarquiaGroupGroupOut(many=True))
def get_herarquias():
    try:
        
        res=get_all_herarquia()
        
        if res is None or len(res) == 0:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"Grupo no encontrado",
                    "ErrorMsg":"No se encontraron datos de grupos"
                } 
            return result

        return res
    
    except Exception as err:
        raise ValidationError(err)   """

@herarquia_b.doc(description='Listado de Grupos padres - Hijos', summary='Grupos padres - hijos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@herarquia_b.get('/herarquias')
@herarquia_b.output(GroupHOut(many=True))
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

        current_app.session.remove()
        return res 
    
    except Exception as err:
        raise ValidationError(err)   
    
@herarquia_b.doc(description='Listado de Grupos padres e hijos con niveles', summary='Grupos Padres - Hijos con Niveles', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})    
@herarquia_b.get('/niveles_grupos')
@herarquia_b.output(HerarquiaOut(many=True))
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

        current_app.session.remove()
        return res 
 
    
    except Exception as err:
        raise ValidationError(err)       


@herarquia_b.get('/herarquias_all')
@herarquia_b.output(HerarquiaAllOut(many=True))
def herarquias_all_():
    try:
        #res=get_grupos_herarquia()
        res=get_grupos_all()
        if res is None:
            
            result={
                    "valido":"fail",
                    "ErrorCode": 800,
                    "ErrorDesc":"No existen jerarquías de grupos",
                } 
            return result
        
        current_app.session.remove()
        return res 
 
    
    except Exception as err:
        raise ValidationError(err)       







