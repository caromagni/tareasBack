# coding: utf-8
import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Tarea, TipoTarea


def get_all_tipo_tareas():
    print("get_tipo_tareas")
    session: scoped_session = current_app.session
    return session.query(TipoTarea).all()


def insert_tipo_tarea(id='', codigo_humano='', descripcion='', id_usuario_actualizacion=''):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        descripcion=descripcion,
        id_usuario_actualizacion=id_usuario_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    session.add(nuevo_tipo_tarea)
    session.commit()
    return nuevo_tipo_tarea


def get_all_tareas():
    session: scoped_session = current_app.session
    tareas = session.query(Tarea).all()
    print("Tareas:", tareas)
    return tareas



