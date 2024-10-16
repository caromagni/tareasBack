from ..models.alch_model import Usuario, UsuarioGrupo
from sqlalchemy.orm import scoped_session
from flask import current_app

def verifica_username(username):
    session: scoped_session = current_app.session
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
    
def verifica_grupo_id(id):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    else:
        usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.eliminado==False).first()
        if usuario_grupo is not None:
            return usuario_grupo.id_grupo
        else:   
            return None 