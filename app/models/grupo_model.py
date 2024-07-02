import uuid
from sqlalchemy.orm import scoped_session, aliased
from datetime import datetime

from flask import current_app

from .alch_model import Grupo, HerarquiaGrupoGrupo


""" def get_all_grupos():
    session: scoped_session = current_app.session
    res =session.query(Grupo).offset(0).limit(3).all()
    cant=session.query(Grupo).count()
    return res, cant """

def get_all_grupos(first=1, rows=10): #if no arguments are passed, the default values are used
    session: scoped_session = current_app.session
    total= session.query(Grupo).count()
    result= session.query(Grupo).offset((first-1)*rows).limit(rows).all()
    return result, total

def get_all_herarquia():
    session: scoped_session = current_app.session
    res =session.query(HerarquiaGrupoGrupo).all()
    return res

def get_grupos_herarquia():
    session: scoped_session = current_app.session
    res=session.query(Grupo.id, Grupo.descripcion, HerarquiaGrupoGrupo.id_hijo, HerarquiaGrupoGrupo.id_padre)\
        .join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre)\
        .all()
    print(len(res))
    return res

def get_grupos_herarquia_labels():
    GrupoPadre = aliased(Grupo)
    GrupoHijo = aliased(Grupo)
    session: scoped_session = current_app.session
    
    # Realizar la consulta con los joins necesarios
    res = session.query(
            Grupo.id.label("id"),
            Grupo.id_user_actualizacion.label("user_actualizacion"),
            Grupo.fecha_actualizacion.label("fecha_actualizacion"),
            Grupo.descripcion.label("descripcion"),
            HerarquiaGrupoGrupo.id.label("herarquia_grupo_grupo_id"),
            HerarquiaGrupoGrupo.id_padre.label("id_padre"),
            GrupoPadre.descripcion.label("padre_descripcion"),
            HerarquiaGrupoGrupo.id_hijo.label("id_hijo"),
            GrupoHijo.descripcion.label("hijo_descripcion"),
            HerarquiaGrupoGrupo.id_usuario_actualizacion.label("tareas_herarquia_grupo_grupo_id_usuario_actualizacion"),
            HerarquiaGrupoGrupo.fecha_actualizacion.label("tareas_herarquia_grupo_grupo_fecha_actualizacion")
        ).join(
            HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre
        ).join(
        GrupoPadre, HerarquiaGrupoGrupo.id_padre == GrupoPadre.id
    ).join(
        GrupoHijo, HerarquiaGrupoGrupo.id_hijo == GrupoHijo.id
    ).all()
    
    return res                                                                 

def update_grupo(id='', descripcion='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    grupos = session.query(Grupo).filter(Grupo.id == id).first()
   
    if grupos is None:
        return None
    
    print("Grupo encontrado:",grupos)
    session.query(Grupo).filter(Grupo.id == id).update({Grupo.descripcion: descripcion,
        Grupo.id_user_actualizacion: id_user_actualizacion,
        Grupo.fecha_actualizacion: datetime.now()})
   
    session.commit()
    return grupos

def insert_grupo(id='', descripcion='', id_user_actualizacion='', id_padre=''):
    session: scoped_session = current_app.session
    nuevoID_grupo=uuid.uuid4()
    nuevoID=uuid.uuid4()
    print(nuevoID)
    nuevo_grupo = Grupo(
        id=nuevoID_grupo,
        descripcion=descripcion,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    session.add(nuevo_grupo)

    if id_padre is not '':        
        nueva_herarquia = HerarquiaGrupoGrupo(
            id=nuevoID,
            id_padre=id_padre,
            id_hijo=nuevoID_grupo,
            id_usuario_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )
        session.add(nueva_herarquia)
    
    session.commit()
    
    return nuevo_grupo

