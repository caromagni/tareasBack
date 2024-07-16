# coding: utf-8
import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime
from ..common.functions import controla_fecha

from flask import current_app

from .alch_model import Tarea, TipoTarea, Usuario, TareaAsignadaUsuario, Grupo


def insert_tarea(id_grupo=None, prioridad=0, id_actuacion='', titulo='', cuerpo='', id_expediente='', caratula_expediente='', id_tipo_tarea=None, eliminable=False, fecha_eliminacion=None, id_usuario_asignado=None, id_user_actualizacion=None, plazo=0):

    
    session: scoped_session = current_app.session
    #fecha_inicio = controla_fecha(fecha_inicio)
    #fecha_fin = controla_fecha(fecha_fin)   
    #print("fecha_inicio:",fecha_inicio)
    nuevoID=uuid.uuid4()
    print("nuevoID:",nuevoID)
    nueva_tarea = Tarea(
        id=nuevoID,
        id_grupo=id_grupo,
        prioridad=prioridad,
        id_actuacion=id_actuacion,
        titulo=titulo,
        cuerpo=cuerpo,
        id_expediente=id_expediente,
        caratula_expediente=caratula_expediente,
        id_tipo_tarea=id_tipo_tarea,
        eliminable=eliminable,
        id_usuario_asignado=id_usuario_asignado,
        id_user_actualizacion=id_user_actualizacion,
        fecha_eliminacion=fecha_eliminacion,
        fecha_actualizacion=datetime.now(),
        #fecha_inicio=fecha_inicio,
        #fecha_fin=fecha_fin,
        fecha_creacion=datetime.now(),
        plazo=plazo
    )

    session.add(nueva_tarea)
    session.commit()
    print("Tarea ingresada:",nueva_tarea)
    return nueva_tarea


def get_all_tipo_tareas():
    print("get_tipo_tareas")
    session: scoped_session = current_app.session
    return session.query(TipoTarea).all()


def insert_tipo_tarea(id='', codigo_humano='', nombre='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
        id_user_actualizacion=id_user_actualizacion,
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


