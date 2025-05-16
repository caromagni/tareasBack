from common.utils import *
from common.error_handling import ValidationError
from alchemy_db import db
from .alch_model import EP
import uuid
from datetime import datetime
##########################  TIPO NOTAS #############################################

def get_all_EP(page=1, per_page=10):
    
    todo = db.session.query(EP).all()
    total= len(todo)
    res = db.session.query(EP).order_by(EP.url).all()
    return res, total

def insert_EP(username, **kwargs):
    if username is not None:
        id_user_actualizacion = get_username_id(username)
    else:
        raise Exception("Usuario no ingresado")

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)

    url = kwargs.get('url', '')
    descripcion = kwargs.get('descripcion', '')

    #caso_uso = kwargs.get('caso_uso', [])  # <-- directamente guardamos la lista de dicts
    cu=[]
    if 'caso_uso' in kwargs:
        caso_uso = kwargs['caso_uso']
        for i in caso_uso:
            print(i)
            print("codigo:",i['codigo'])
            cu.append(i['codigo'])
            
    nuevoID = uuid.uuid4()
    nuevo_EP = EP(
        id=nuevoID,
        url=url,
        descripcion=descripcion,
        caso_uso=cu,  # <-- guardamos la estructura completa
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_EP)
    db.session.commit()
    return nuevo_EP
    