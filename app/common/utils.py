from models.alch_model import Usuario, UsuarioGrupo, Grupo
from sqlalchemy.orm import scoped_session
from flask import current_app

def verifica_username(username):
    session: scoped_session = current_app.session
    username = username.upper()
    usuario = session.query(Usuario).filter(Usuario.username == username, Usuario.eliminado==False).first()
    if usuario is None:
        raise Exception("Usuario no encontrado: "+ username)
    else:
        return usuario.id
    

def verifica_usr_id(id):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    return usuario.id
    
def verifica_grupo_id(id):
    session: scoped_session = current_app.session
    id_grupo=None
    id_user_asignacion=None
    usuario = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    else:
        usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.eliminado==False).first()
        if usuario_grupo is not None:
            existe_grupo = session.query(Grupo).filter(Grupo.id == usuario_grupo.id_grupo, Grupo.eliminado==False, Grupo.suspendido==False).first()
            if existe_grupo is not None:
                id_grupo=existe_grupo.id
                id_user_asignacion=existe_grupo.id_user_asignado_default
            if id_user_asignacion is None:
                id_user_asignacion = id
        else:
            id_user_asignacion = id       

    return id_grupo, id_user_asignacion        