from models.alch_model import Usuario, UsuarioGrupo, Grupo
from db.alchemy_db import db
import common.logger_config as logger_config
import unicodedata

def normalize_spanish_text(text):
    """
    Remove Spanish special characters and replace them with their closest plain equivalents.
    
    Args:
        text (str): Input string that may contain Spanish special characters
        
    Returns:
        str: Plain UTF-8 string with special characters replaced
        
    Examples:
        normalize_spanish_text("Martín Cr") -> "Martin Cr"
        normalize_spanish_text("Silvia Susana...... Imperiale Horber") -> "Silvia Susana...... Imperiale Horber"
        normalize_spanish_text("Calas Nadín") -> "Calas Nadin"
    """
    if not text or not isinstance(text, str):
        return text
    
    # Define character mappings for Spanish special characters
    spanish_char_map = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a', 'å': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A', 'Ã': 'A', 'Å': 'A',
        'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
        'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
        'Ñ': 'N'
    }
    
    # Replace Spanish special characters
    normalized_text = text
    for special_char, plain_char in spanish_char_map.items():
        normalized_text = normalized_text.replace(special_char, plain_char)
    
    # Additional normalization using unicodedata for any remaining special characters
    normalized_text = unicodedata.normalize('NFD', normalized_text)
    normalized_text = ''.join(c for c in normalized_text if not unicodedata.combining(c))
    
    return normalized_text


def get_username_id(username):
    
    #username = username.upper()
    usuario = db.session.query(Usuario).filter(Usuario.username == username, Usuario.eliminado==False).first()
    if usuario is None:
        logger_config.logger.error("Usuario no encontrado: "+ username)
        raise Exception("Usuario no encontrado: "+ username)
    else:
        return usuario.id
    

def verifica_usr_id(id):
    print("Verifica id usuario - ID:",id)
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            logger_config.logger.error("Usuario de actualizacion no encontrado")
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    return usuario.id
    
def verifica_grupo_id(id):
    
    id_grupo=None
    id_user_asignacion=None
    usr_grupo=[]
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
            logger_config.logger.error("Usuario de actualizacion no encontrado")
            raise Exception("Usuario de actualizacion no encontrado: "+ id)
    else:
        usuario_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.eliminado==False).all()
        if usuario_grupo is not None:
            for row in usuario_grupo:
                existe_grupo = db.session.query(Grupo).filter(Grupo.id == usuario_grupo.id_grupo, Grupo.eliminado==False, Grupo.suspendido==False).first()
                if existe_grupo is not None:
                    usr_grupo.append(row.id_grupo, row.id_user_asignado_default)

    return usr_grupo
