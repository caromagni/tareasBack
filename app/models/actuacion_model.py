from db.alchemy_db import db
from models.alch_model import ActuacionExt, TipoActuacionExt
from common.cache import cache

@cache.memoize(timeout=3600)
def get_all_actuaciones():
    
    return db.session.query(ActuacionExt.id,
                         ActuacionExt.nombre, 
                         ActuacionExt.id_tipo_actuacion, 
                         ActuacionExt.fecha_actualizacion,
                         ActuacionExt.id_user_actualizacion,
                         TipoActuacionExt.nombre.label('tipo_actuacion')
                         ).join(TipoActuacionExt, TipoActuacionExt.id==ActuacionExt.id_tipo_actuacion).all()

def get_all_tipoactuaciones():
    
    return db.session.query(TipoActuacionExt).all()