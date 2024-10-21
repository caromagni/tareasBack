import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import ActuacionExt, TipoActuacionExt


def get_all_actuaciones():
    session: scoped_session = current_app.session
    return session.query(ActuacionExt.id,
                         ActuacionExt.nombre, 
                         ActuacionExt.id_tipo_actuacion, 
                         ActuacionExt.fecha_actualizacion,
                         ActuacionExt.id_user_actualizacion,
                         TipoActuacionExt.nombre.label('tipo_actuacion')
                         ).join(TipoActuacionExt, TipoActuacionExt.id==ActuacionExt.id_tipo_actuacion).all()

def get_all_tipoactuaciones():
    session: scoped_session = current_app.session
    return session.query(TipoActuacionExt).all()