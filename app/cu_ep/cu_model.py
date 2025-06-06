from common.utils import *
from common.error_handling import ValidationError
from alchemy_db import db
from .alch_model import CU
import uuid
from datetime import datetime
##########################  TIPO NOTAS #############################################

def get_all_CU(page=1, per_page=10):
    
    todo = db.session.query(CU).all()
    total= len(todo)
    res = db.session.query(CU).order_by(CU.codigo).all()
    return res, total

def insert_CU(username, codigo='', descripcion='', id_user_actualizacion=''):
    if username is not None:
        id_user_actualizacion = get_username_id(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
           
    nuevoID=uuid.uuid4()

    nuevo_CU = CU(
        id=nuevoID,
        codigo=codigo,
        descripcion=descripcion,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_CU)
    db.session.commit()
    return nuevo_CU