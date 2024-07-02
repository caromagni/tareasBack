from apiflask import APIBlueprint
from ..models.grupo_model import get_all_herarquia, get_grupos_herarquia_labels
from ..common.error_handling import ValidationError
from typing import List
from ..schemas.schemas import GrupoHOut, HerarquiaGrupoGrupoOut


herarquia_b = APIBlueprint('herarquia_blueprint', __name__)

@herarquia_b.doc(description='Listado de Grupos padres - hijos', summary='Jerarquía de Grupos', responses={200: 'OK', 400: 'Invalid data provided', 500: 'Invalid data provided'})
@herarquia_b.get('/herarquias')
@herarquia_b.output(HerarquiaGrupoGrupoOut(many=True))
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
        raise ValidationError(err)  


@herarquia_b.get('/grupos_h')
@herarquia_b.output(GrupoHOut(many=True))
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

        return res 
 
    
    except Exception as err:
        raise ValidationError(err)   