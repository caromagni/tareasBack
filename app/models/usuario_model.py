import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Usuario, UsuarioGrupo


def get_usuario_by_id(id):
    session: scoped_session = current_app.session
    return session.query(Usuario).filter(Usuario.id == id).first()
    #return Usuario.query.filter(Usuario.id == id).first()

def get_all_usuarios():
    session: scoped_session = current_app.session
    return session.query(Usuario).all()

def insert_usuario(id='', nombre='', apellido='', id_persona_ext='', id_user_actualizacion='', id_grupo=''):
    session: scoped_session = current_app.session
    nuevoID_usuario=uuid.uuid4()
    print(nuevoID)
    nuevo_usuario = Usuario(
        id=nuevoID_usuario,
        nombre=nombre,
        apellido=apellido,
        id_persona_ext=id_persona_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    session.add(nuevo_usuario)
    
    if id_grupo is not '':        
        nuevoID=uuid.uuid4()
        nuevo_usuario_grupo = UsuarioGrupo(
            id=nuevoID,
            id_grupo=id_grupo,
            id_usuario=nuevoID_usuario,
            id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )

        session.add(nuevo_usuario_grupo)
    
    session.commit()

    return nuevo_usuario