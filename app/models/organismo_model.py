from models.alch_model import Organismo
from db.alchemy_db import db
from common.cache import *

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_organismo():
    #session: scoped_session = current_app.session
    query = db.session.query(Organismo).order_by(Organismo.descripcion).all()
    results = []
    for organismo in query:
        result = {
            "id": organismo.id,
            "id_organismo_ext": organismo.id_organismo_ext,
            "circunscripcion_judicial": organismo.circunscripcion_judicial,
            "descripcion": organismo.descripcion,
            "id_fuero": organismo.id_fuero,
            "descripcion_corta": organismo.descripcion_corta,
            "eliminado": organismo.eliminado,
            "id_tarea_grupo_base": organismo.id_tarea_grupo_base,
            "instancia": organismo.instancia,
            "fecha_actualizacion": organismo.fecha_actualizacion,
            "id_user_actualizacion": organismo.id_user_actualizacion
        }
        results.append(result)
    
    return results, len(results)