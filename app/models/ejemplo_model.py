from db.alchemy_db import db
from models.alch_model import ActuacionExt, TipoActuacionExt

#ejemplo de lo que deberia tener el modelo, no hay que poner logica de negocios aca

def get_all_ejemplo():
    
    return db.session.query(ActuacionExt.id,
                         ActuacionExt.nombre, 
                         ActuacionExt.id_tipo_actuacion, 
                         ActuacionExt.fecha_actualizacion,
                         ActuacionExt.id_user_actualizacion,
                         TipoActuacionExt.nombre.label('tipo_actuacion')
                         ).join(TipoActuacionExt, TipoActuacionExt.id==ActuacionExt.id_tipo_actuacion).all()

def get_all_tipo_ejemplo():
    
    return db.session.query(TipoActuacionExt).all()