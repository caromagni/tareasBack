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
            #id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )

        session.add(nuevo_usuario_grupo)
    
    session.commit()

    return nuevo_usuario


def update_usuario(id='', **kwargs):
#def update_usuario(id='', nombre='', apellido='', id_persona_ext='', id_grupo='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
   
    if usuario is None:
        return None
    
    print("Usuario encontrado:",usuario)

    update_data = {}
    if 'nombre' in kwargs:
        update_data[Usuario.nombre] = kwargs['nombre']
    if 'apellido' in kwargs:
        update_data[Usuario.apellido] = kwargs['apellido']
    if 'id_persona_ext' in kwargs:
        update_data[Usuario.id_persona_ext] = kwargs['id_persona_ext']
    if 'id_user_actualizacion' in kwargs:
        update_data[Usuario.id_user_actualizacion] = kwargs['id_user_actualizacion']
        id_user_actualizacion = kwargs['id_user_actualizacion']
    else:    
        id_user_actualizacion = ''

    # Siempre actualizar la fecha de actualización
    update_data[Usuario.fecha_actualizacion] = datetime.now()
    print("update_data:",update_data)
    
    """ if update_data:
        session.query(Usuario).filter(Usuario.id == id).update(update_data)
    if nombre != '':
        usuario.nombre = nombre
    if apellido != '':
        usuario.apellido = apellido
    if id_persona_ext != '':
        usuario.id_persona_ext = id_persona_ext
    else:
        usuario.id_persona_ext = None

    if id_user_actualizacion != '':
        usuario.id_user_actualizacion = id_user_actualizacion        
        print("nombre:",nombre)
    usuario.fecha_actualizacion = datetime.now() """

    session.query(Usuario).filter(Usuario.id == id).update(update_data)
    

    """ session.query(Usuario).filter(Usuario.id == id).update({Usuario.nombre: nombre,
        Usuario.apellido: apellido,
        Usuario.id_persona_ext: id_persona_ext,
        Usuario.id_user_actualizacion: id_user_actualizacion,
        Usuario.fecha_actualizacion: datetime.now()}) """
    

    #if id_grupo is not '': 
    print("##############################################")
    print("id_user_actualizacion:",id_user_actualizacion)
    print("##############################################")
    if 'id_grupo' in kwargs:      
        nuevoID=uuid.uuid4()
        usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.id_grupo==kwargs['id_grupo']).first()
        if usuario_grupo is None:
            nuevo_usuario_grupo = UsuarioGrupo(
                id=nuevoID,
                id_grupo=kwargs['id_grupo'],
                id_usuario=id,
                #id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )
            session.add(nuevo_usuario_grupo)

    session.commit()
    return usuario

