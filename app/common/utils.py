from models.alch_model import Usuario, UsuarioGrupo, Grupo
from sqlalchemy.orm import scoped_session
from flask import current_app
from alchemy_db import db
from common.logger_config import logger


def get_username_id(username):
    
    #username = username.upper()
    usuario = db.session.query(Usuario).filter(Usuario.username == username, Usuario.eliminado==False).first()
    if usuario is None:
        logger.error("Usuario no encontrado: "+ username)
        raise Exception("Usuario no encontrado: "+ username)
    else:
        return usuario.id
    

def verifica_usr_id(id):
    print("Verifica id usuario - ID:",id)
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            logger.error("Usuario de actualizacion no encontrado")
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    return usuario.id
    
def verifica_grupo_id(id):
    
    id_grupo=None
    id_user_asignacion=None
    usr_grupo=[]
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            logger.error("Usuario de actualizacion no encontrado")
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    else:
        usuario_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.eliminado==False).all()
        if usuario_grupo is not None:
            for row in usuario_grupo:
                existe_grupo = db.session.query(Grupo).filter(Grupo.id == usuario_grupo.id_grupo, Grupo.eliminado==False, Grupo.suspendido==False).first()
                if existe_grupo is not None:
                    usr_grupo.append(row.id_grupo, row.id_user_asignado_default)

    return usr_grupo
