import requests
from models.alch_model import Usuario, RolExt, EP, UsuarioRol
from datetime import date, timedelta, datetime
import common.logger_config as logger_config
import uuid
from db.alchemy_db import db
from sqlalchemy import or_
import os
import json
import common.utils as utils
from common.cache import *

def migrar_cu(username):
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)
    else:
        raise Exception("Usuario no ingresado")

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)

    borra_ep = db.session.query(EP).delete()

    archivo_json="./json/ep_cu.json"
    with open(archivo_json, 'r', encoding='utf-8') as f:
        endpoints_data = json.load(f)

    for item in endpoints_data:
        print("url:", item['url'])
        print("metodo:", item['metodo'])
        nuevo_ep = EP(
            id=uuid.uuid4(),
            url=item['url'],
            metodo=item['metodo'],
            descripcion=item['descripcion'],
            caso_uso=item['caso_uso'],  # Esto va directo como jsonb
            fecha_actualizacion=datetime.now(),  # o datetime.now() si querés local
            id_user_actualizacion=id_user_actualizacion
        )
            
        db.session.add(nuevo_ep)

    # Finalmente, confirmamos los cambios
    db.session.commit()
    cu = db.session.query(EP).all()
    return cu



def get_roles(username=''):
    print("get_roles")
    try:
        url=os.environ.get('PUSHER_URL')+username
        print("url:", url)
        x_api_key=os.environ.get('PUSHER_API_KEY')
        x_api_system=os.environ.get('PUSHER_API_SYSTEM')
        
        r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
        resp=r.json()
        return resp
    #except requests.exceptions.RequestException as e:
    except Exception as err:
        logger_config.logger.error(f"Error al obtener roles desde P-USHER: {err}")
        raise Exception(f"Error al obtener roles desde P-USHER: {err}")
    
######################Casos de uso de cada url######################
############desde la base de datos############
#@cache.memoize(CACHE_TIMEOUT_LONG)
def get_api_cu_bd(metodo=None, url=None):
    cu=[]
    if url is not None:
        cu_query= db.session.query(EP.caso_uso).filter(EP.url == url, EP.metodo == metodo).first()

    if cu_query is None or len(cu_query) == 0:
        logger_config.logger.error("No hay casos de uso para la url: %s", url)
        return cu  
    else:
        print("casos de uso encontrados desde base de datos:", cu_query.caso_uso)

    for item in cu_query.caso_uso:
            print("cu encontrado desde base de datos:", item['codigo'])
            cu.append(item['codigo'])

    return cu

##########desde el archivo JSON##########
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
#@cache.memoize(CACHE_TIMEOUT_LONG)
def get_usr_cu(username=None, rol_usuario='', casos=None):
    logger_config.logger.info("get_usr_cu - Inicio")
    logger_config.logger.info("get_usr_cu - username: %s", username)
    logger_config.logger.info("get_usr_cu - rol_usuario: %s", rol_usuario)
    logger_config.logger.info("get_usr_cu - cu: %s", casos)
    if casos is None or len(casos) == 0:
        logger_config.logger.error("No hay casos de uso")
        return False
    else:
        logger_config.logger.info("Casos de uso encontrados: %s", casos)
        
    pull_roles = False
    pusher_ok = True
    #tiempo_vencimiento = timedelta(days=1)
    #tiempo_vencimiento = timedelta(hours=1)
    tiempo_vencimiento = timedelta(minutes=2)
    try:
        print("entro TRY usher")
        query_usr = db.session.query(Usuario).filter(Usuario.email == username).first()
        print("after QUERY USR")
        if query_usr is None:
            logger_config.logger.error("Usuario no encontrado")
            return False
        
        id_usuario = query_usr.id
        email = query_usr.email
        print("id_usuario:", id_usuario)
        print("email:", email)

        #Pregunto si el usuario tiene un rol
        query_rol = db.session.query(RolExt).filter(RolExt.email == email).all()
        print("after QUERY ROL")
        if len(query_rol)>0:
            #Pregunto si hay algún registro vencido
            logger_config.logger.info("Controla roles vencidos")
            query_vencido = db.session.query(RolExt).filter(RolExt.email == email, RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()).all()
        #Traigo los roles del usuario desde P-USHER
        if len(query_rol)==0 or len(query_vencido)>0:
       
            #controlar si P-USHER no falla
            logger_config.logger.info("REQUEST PUSHER")
            #agregar un try y except para controlar si da error de conexion
            roles = get_roles(username)
            #print("roles:", roles)
            if 'lista_roles_cus' in roles:
            #Borro todos los registros del usuario si existen roles nuevos desde P-USHER
                logger_config.logger.info("ROLES VENCIDOS")
                query_vencido = db.session.query(RolExt).filter(RolExt.email == email, RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()).delete()
                pull_roles = True
            else:
                logger_config.logger.error("Error al obtener roles desde P-USHER")
                pusher_ok = False

            print ("pull_roles:", pull_roles)

        #######Consultar CU Api P-USHER##########
        #pull_roles = True
        print("checking pull roles")
        if pull_roles:
            logger_config.logger.info("Get roles desde p-usher")
            #roles = get_roles(username)
            for r in roles['lista_roles_cus']:
                    ######ROL USHER##########
                    print("rol:",r['descripcion_rol'])
                    ######Casos de uso del rol##########
                    for caso_uso in r['casos_de_uso']:
                        nuevoIDRol=uuid.uuid4()
                        nuevo_rol = RolExt(
                            id=nuevoIDRol, 
                            email=email,
                            #id_usuario=id_usuario, 
                            fecha_actualizacion=datetime.now(),
                            rol=r['descripcion_rol'],
                            id_rol_ext=r['id_usuario_sistema_rol'],
                            descripcion_ext=caso_uso['descripcion_corta_cu']
                        )
                        nuevo_usuarioRol = UsuarioRol(
                            id=uuid.uuid4(),
                            id_usuario_grupo="01b9d255-4e46-402b-9285-ec0446809283",
                            id_rol_ext=nuevoIDRol,
                            fecha_actualizacion=datetime.now(),
                            id_user_actualizacion=utils.get_username_id(username),
                            eliminado=False,
                            id_dominio="06737c52-5132-41bb-bf82-98af37a9ed80"
                        )

                        db.session.add(nuevo_rol)
                        db.session.add(nuevo_usuarioRol)
                
            db.session.commit()
        
        #Controlo si el usuario con el rol elegido tiene permisos
        if not pusher_ok:
            logger_config.logger.error("P-USHER no está disponible, utilizando roles vencidos de la base de datos")
            query_permisos = db.session.query(RolExt.descripcion_ext
                    ).filter(
                        RolExt.email == email,
                        RolExt.rol == rol_usuario,
                        RolExt.descripcion_ext.in_(casos)
                    ).all()
        else:
            #pusher falló, entonces no tengo en cuenta la fecha de vencimiento
            query_permisos = db.session.query(RolExt.descripcion_ext
                ).filter(
                    RolExt.email == email,
                    RolExt.rol == rol_usuario,
                    RolExt.fecha_actualizacion + tiempo_vencimiento >= datetime.now(),
                    RolExt.descripcion_ext.in_(casos)
                ).all()    
       
        if len(query_permisos)==0:
            logger_config.logger.error("No tiene permisos")
            return False
        else:
            logger_config.logger.info("Usuario tiene permisos")
            return True
    except requests.exceptions.RequestException as e:
        logger_config.logger.error(f"Error en get_roles desde P-USHER: {e}")
        return False    
    """ except Exception as e:
        logger_config.logger.error(f"Error en get_usr_cu: {e}")
        return False  """   

    
