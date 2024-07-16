import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Usuario, UsuarioGrupo, Grupo


def get_usuario_by_id(id):
    session: scoped_session = current_app.session
    return session.query(Usuario).filter(Usuario.id == id).first()
    #return Usuario.query.filter(Usuario.id == id).first()

def get_all_usuarios():
    session: scoped_session = current_app.session
    return session.query(Usuario).all()

def get_grupos_by_usuario(id):
    session: scoped_session = current_app.session
    res = session.query(Usuario.id.label("id_usuario"),
                  Usuario.nombre.label("nombre"),
                  Usuario.apellido.label("apellido"),
                  Grupo.id.label("id_grupo"),
                  Grupo.nombre.label("nombre_grupo")
                  ).join(UsuarioGrupo, Usuario.id == UsuarioGrupo.id_usuario
                  ).join(Grupo, UsuarioGrupo.id_grupo == Grupo.id).filter(Usuario.id == id).all()                                    
    
    return res




def insert_usuario(id='', nombre='', apellido='', id_persona_ext=None, id_grupo=None, id_user_actualizacion=None):
    session: scoped_session = current_app.session
    nuevoID_usuario=uuid.uuid4()
    print("nuevo_usuario:",nuevoID_usuario)
    nuevo_usuario = Usuario(
        id=nuevoID_usuario,
        nombre=nombre,
        apellido=apellido,
        id_persona_ext=id_persona_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    print("nuevo_usuario:",nuevo_usuario)
    session.add(nuevo_usuario)
    
    if id_grupo is not '':        
        nuevoID=uuid.uuid4()
        nuevo_usuario_grupo = UsuarioGrupo(
            id=nuevoID,
            id_grupo=id_grupo,
            id_usuario=nuevoID_usuario,
            #id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )

        session.add(nuevo_usuario_grupo)
    
    session.commit()

    return nuevo_usuario


def update_usuario(id='', **kwargs):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
   
    if usuario is None:
        return None
    
    print("Usuario encontrado:",usuario)

    update_data = {}
    if 'nombre' in kwargs:
        usuario.nombre = kwargs['nombre']
    if 'apellido' in kwargs:
        usuario.apellido = kwargs['apellido']
    if 'id_persona_ext' in kwargs:
        usuario.id_persona_ext = kwargs['id_persona_ext']
    if 'id_user_actualizacion' in kwargs:
        usuario.id_user_actualizacion = kwargs['id_user_actualizacion']

    usuario.fecha_actualizacion = datetime.now()

    if 'id_grupo' in kwargs:      
        nuevoID=uuid.uuid4()
        usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.id_grupo==kwargs['id_grupo']).first()
        if usuario_grupo is None:
            nuevo_usuario_grupo = UsuarioGrupo(
                id=nuevoID,
                id_grupo=kwargs['id_grupo'],
                id_usuario=id,
                id_user_actualizacion= kwargs['id_user_actualizacion'],
                fecha_actualizacion=datetime.now()
            )
            session.add(nuevo_usuario_grupo)

    session.commit()
    return usuario

