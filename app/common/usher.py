import requests
from models.alch_model import Usuario, Rol
from datetime import date, timedelta, datetime
import common.logger_config as logger_config
import uuid
from db.alchemy_db import db
from sqlalchemy import or_
import os
import json
from common.cache import cache

def get_roles(username=''):
    print("get_roles")
    url=os.environ.get('PUSHER_URL')+username
    
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    
    r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
    resp=r.json()
    return resp

######################Casos de uso de la api######################
@cache.memoize(timeout=500)

def get_api_cu(metodo=None, url=None):
    archivo_json="./json/ep_cu.json"
    logger_config.logger.info("get_api_cu - url: %s", url)
    cu = []
    if metodo is None or url is None:
        return cu

    if not os.path.exists(archivo_json):
        raise FileNotFoundError(f"El archivo {archivo_json} no existe.")

    with open(archivo_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ep in data:
        if ep.get("metodo") == metodo and ep.get("url") == url:
            cu = [item["codigo"] for item in ep.get("caso_uso", [])]
            break

    return cu

######################Control de acceso######################
@cache.memoize(timeout=500)
def get_usr_cu(username=None, rol_usuario='', cu=None):
    #logger_config.logger.info("get_usr_cu - username: %s", username)
    #logger_config.logger.info("get_usr_cu - rol_usuario: %s", rol_usuario)
    #logger_config.logger.info("get_usr_cu - cu: %s", cu)
    if cu is None or len(cu) == 0:
        logger_config.logger.error("No hay casos de uso")
        return False
    
    pull_roles = True
    #tiempo_vencimiento = timedelta(days=1)
    tiempo_vencimiento = timedelta(minutes=3)
    try:
        query_usr = db.session.query(Usuario).filter(Usuario.email == username).first()
        if query_usr is None:
            logger_config.logger.error("Usuario no encontrado")
            return False
        
        id_usuario = query_usr.id
        email = query_usr.email
        #Pregunto si el usuario tiene un rol
        query_rol = db.session.query(Rol).filter(Rol.email == email).all()
        if len(query_rol)>0:
            pull_roles = False
            #Pregunto si hay algún registro vencido
            logger_config.logger.info("Controla roles vencidos")
            query_vencido = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento < datetime.now()).all()
            if len(query_vencido)>0:
                #controlar si P-USHER no falla
                logger_config.logger.info("REQUEST PUSHER")
                roles = get_roles(username)
                print("roles:", roles)
                if 'lista_roles_cus' in roles:
                #Borro todos los registros del usuario si existen roles nuevos desde P-USHER
                    logger_config.logger.info("ROLES VENCIDOS")
                    print("Borrando roles vencidos")
                    query_vencido = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento < datetime.now()).delete()
                    pull_roles = True    

        #######Consultar CU Api P-USHER##########
        #pull_roles = True
        if pull_roles:
            logger_config.logger.info("Get roles desde p-usher")
            #roles = get_roles(username)
            for r in roles['lista_roles_cus']:
                    ######ROL USHER##########
                    print("rol:",r['descripcion_rol'])
                    ######Casos de uso del rol##########
                    for caso_uso in r['casos_de_uso']:
                        nuevoIDRol=uuid.uuid4()
                        nuevo_rol = Rol(
                            id=nuevoIDRol, 
                            email=email,
                            id_usuario=id_usuario, 
                            fecha_actualizacion=datetime.now(),
                            rol=r['descripcion_rol'],
                            id_rol_ext=r['id_usuario_sistema_rol'],
                            descripcion_ext=caso_uso['descripcion_corta_cu']
                        )
                        db.session.add(nuevo_rol)
                
            db.session.commit()
        
        #Controlo si el usuario con el rol elegido tiene permisos
        query_permisos = db.session.query(Rol).filter(Rol.email == email, Rol.rol == rol_usuario, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), or_(*[Rol.descripcion_ext.like(f"%{perm}%") for perm in cu])).all()
        if len(query_permisos)==0:
            logger_config.logger.error("No tiene permisos")
            return False
        else:
            logger_config.logger.info("Usuario tiene permisos")
            return True
    except requests.exceptions.RequestException as e:
        logger_config.logger.error(f"Error en get_roles desde P-USHER: {e}")
        return False    
    except Exception as e:
        logger_config.logger.error(f"Error en get_usr_cu: {e}")
        return False    

    
