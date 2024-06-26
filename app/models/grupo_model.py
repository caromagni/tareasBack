import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Grupo, HerarquiaGrupoGrupo


def get_all_grupos():
    session: scoped_session = current_app.session
    return session.query(Grupo).all()


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

