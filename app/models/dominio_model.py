from db.alchemy_db import db
from models.alch_model import Dominio
from common.cache import *

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_dominio():
    
    # Get all dominio records
    dominios = db.session.query(Dominio).filter(Dominio.habilitado == True).all()
    
    # Convert to list of dictionaries for serialization
    results = []
    for dominio in dominios:
        result = {
            "id": dominio.id,
            "id_dominio_ext": dominio.id_dominio_ext,
            "descripcion": dominio.descripcion,
            "descripcion_corta": dominio.descripcion_corta,
            "prefijo": dominio.prefijo,
            "fecha_actualizacion": dominio.fecha_actualizacion,
            "habilitado": dominio.habilitado,
            "id_user_actualizacion": dominio.id_user_actualizacion
        }
        results.append(result)
    
    return results, len(results)