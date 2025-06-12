import common.utils as utils
import common.logger_config as logger_config
from db.alchemy_db import db
from models.alch_model import EP
import uuid
from datetime import datetime
##########################  TIPO NOTAS #############################################

def get_all_EP(username=None):
    logger_config.logger.info("get_all_EP")
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)
    else:
        raise Exception("Usuario no ingresado")
    
    res = db.session.query(EP).order_by(EP.url).all()
    total= len(res)
    
    return res, total

def insert_EP(username, **kwargs):
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)
    else:
        raise Exception("Usuario no ingresado")

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)

    url = kwargs.get('url', '')
    descripcion = kwargs.get('descripcion', '')
    metodo = kwargs.get('metodo', '')
    existe = db.session.query(EP).filter(EP.url == url, metodo == metodo).first()
    if existe is not None:
        raise Exception(f"Ya existe un endpoint con la URL {url} y el método {metodo}")
    #caso_uso = kwargs.get('caso_uso', [])  # <-- directamente guardamos la lista de dicts
    cu=[]
    if 'caso_uso' in kwargs:
        caso_uso = kwargs['caso_uso']
        for i in caso_uso:
            print(i)
            print("codigo:",i['codigo'])
            cu.append({
                'codigo': i['codigo']
            })
            
    nuevoID = uuid.uuid4()
    nuevo_EP = EP(
        id=nuevoID,
        url=url,
        descripcion=descripcion,
        caso_uso=cu,  # <-- guardamos la estructura completa
        metodo=metodo,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_EP)
    db.session.commit()
    return nuevo_EP
    