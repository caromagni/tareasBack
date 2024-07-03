# coding: utf-8
import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Tarea, TipoTarea, Usuario, TareaAsignadaUsuario, Grupo


def get_all_tipo_tareas():
    print("get_tipo_tareas")
    session: scoped_session = current_app.session
    return session.query(TipoTarea).all()


def insert_tipo_tarea(id='', codigo_humano='', nombre='', id_usuario_actualizacion=''):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
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

def usuarios_tarea(tarea_id=""):
    session: scoped_session = current_app.session
    print("Usuarios por tarea:", tarea_id)    
    usuarios = session.query(Usuario.nombre.label('nombre'),
                        Usuario.apellido.label('apellido'),
                        Usuario.id.label('id'),
                        Usuario.id_persona_ext.label('id_persona_ext'),
                        Usuario.id_user_actualizacion.label('id_user_actualizacion'),
                        Usuario.fecha_actualizacion.label('fecha_actualizacion'),
                        Tarea.id_grupo.label('id_grupo'),\
                        Grupo.nombre.label('grupo'))\
                        .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                        .join(Tarea, TareaAsignadaUsuario.id_tarea == Tarea.id)\
                        .join(Grupo, Tarea.id_grupo == Grupo.id)\
                        .filter(TareaAsignadaUsuario.id_tarea == tarea_id)\
                        .all()
    
    return usuarios


