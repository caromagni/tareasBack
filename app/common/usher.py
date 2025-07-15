import requests
from models.alch_model import Usuario, RolExt, EP, UsuarioRol, UsuarioGrupo
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
    logger = logger_config.logger
    logger.info("get_usr_cu - Inicio")
    logger.info(f"get_usr_cu - username: {username}, rol_usuario: {rol_usuario}, cu: {casos}")

    if not casos:
        logger.error("No hay casos de uso")
        return False

    pusher_ok = True
    pull_roles = False
    tiempo_vencimiento = timedelta(minutes=2)
    id_dominio = '06737c52-5132-41bb-bf82-98af37a9ed80'
    id_grupo = 'cb08f738-7590-4331-871e-26f0f09ff4ca'  # Organismo por defecto

    try:
        usuario = db.session.query(Usuario).filter_by(email=username).first()
        if not usuario:
            logger.error("Usuario no encontrado")
            return False

        id_usuario = usuario.id
        email = usuario.email

        # Consulta roles actuales
        roles_local = db.session.query(RolExt).filter_by(email=email).all()
        roles_vencidos = []
        if roles_local:
            roles_vencidos = db.session.query(RolExt).filter(
                RolExt.email == email,
                RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()
            ).all()

        # Pido a P-USHER si no hay roles o hay vencidos
        if not roles_local or roles_vencidos:
            logger.info("Solicitando roles desde P-USHER")
            roles_pusher = get_roles(username)
            if 'lista_roles_cus' in roles_pusher:
                logger.info("Roles válidos obtenidos desde P-USHER")

                # Elimino roles vencidos
                db.session.query(RolExt).filter(
                    RolExt.email == email,
                    RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()
                ).delete()

                # Obtengo grupo activo
                grupo_usuario = db.session.query(UsuarioGrupo).filter_by(
                    id_usuario=id_usuario, eliminado=False
                ).first()
                if not grupo_usuario:
                    raise Exception("Usuario no pertenece a ningún grupo")

                # Inserto nuevos roles
                for r in roles_pusher['lista_roles_cus']:
                    print("rol:",r['descripcion_rol'])
                    for caso_uso in r['casos_de_uso']:
                        nuevo_id_rol = uuid.uuid4()
                        nuevo_rol = RolExt(
                            id=nuevo_id_rol,
                            email=email,
                            fecha_actualizacion=datetime.now(),
                            rol=r['descripcion_rol'],
                            id_rol_ext=r['id_usuario_sistema_rol'],
                            descripcion_ext=caso_uso['descripcion_corta_cu']
                        )
                        db.session.add(nuevo_rol)

                        nuevo_usuario_rol = UsuarioRol(
                            id=uuid.uuid4(),
                            id_usuario_grupo=grupo_usuario.id,
                            id_rol_ext=nuevo_id_rol,
                            fecha_actualizacion=datetime.now(),
                            id_user_actualizacion=utils.get_username_id(username),
                            eliminado=False,
                            id_dominio=id_dominio
                        )
                        db.session.add(nuevo_usuario_rol)

                db.session.commit()
                pull_roles = True
            else:
                logger.error("Error al obtener roles desde P-USHER")
                pusher_ok = False

        # Determinar los roles a consultar
        if rol_usuario:
            roles_consulta = [rol_usuario]
        else:
            query_roles = db.session.query(RolExt.rol).filter_by(email=email).distinct().all()
            if not query_roles:
                logger.error("El usuario no tiene roles asignados")
                return False
            roles_consulta = [r.rol for r in query_roles]
            print("ROLES CONSULTA:", roles_consulta)

        # Consultar permisos
        query = db.session.query(RolExt.descripcion_ext).filter(
            RolExt.email == email,
            RolExt.rol.in_(roles_consulta),
            RolExt.descripcion_ext.in_(casos)
        )

        if pusher_ok:
            query = query.filter(
                RolExt.fecha_actualizacion + tiempo_vencimiento >= datetime.now()
            )
        else:
            logger.warning("P-USHER no disponible, usando roles locales vencidos")

        permisos = query.all()
        if not permisos:
            logger.error("No tiene permisos")
            return False

        logger.info("Usuario tiene permisos")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error en get_roles desde P-USHER: {e}")
        return False
    except Exception as e:
        logger.error(f"Error en get_usr_cu: {e}")
        return False


def get_usr_cu_old(username=None, rol_usuario='', casos=None):
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
    id_grupo = 'cb08f738-7590-4331-871e-26f0f09ff4ca'  # Organismo por defecto
    id_dominio = '06737c52-5132-41bb-bf82-98af37a9ed80'  # Dominio por defecto
    #tiempo_vencimiento = timedelta(days=1)
    #tiempo_vencimiento = timedelta(hours=1)
    tiempo_vencimiento = timedelta(minutes=2)
    try:
        query_usr = db.session.query(Usuario).filter(Usuario.email == username).first()
        if query_usr is None:
            logger_config.logger.error("Usuario no encontrado")
            return False
        
        id_usuario = query_usr.id
        email = query_usr.email

        #Pregunto si el usuario tiene un rol
        query_rol = db.session.query(RolExt).filter(RolExt.email == email).all()
        if len(query_rol)>0:
            #Pregunto si hay algún registro vencido
            logger_config.logger.info("Controla roles vencidos")
            query_vencido = db.session.query(RolExt).filter(RolExt.email == email, RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()).all()
        #Traigo los roles del usuario desde P-USHER
        if len(query_rol)==0 or len(query_vencido)>0:
       
            #controlar si P-USHER no falla
            logger_config.logger.info("REQUEST PUSHER")
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
            print ("id de usuario:", id_usuario)
            ####HACER LA BUSQUEDA DE GRUPO PARA EL ORGANISMO ACTUAL######
            #grupo_usuario = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario==id_usuario, UsuarioGrupo.id_grupo==id_grupo, UsuarioGrupo.eliminado==False)
            grupo_usuario = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario==id_usuario, UsuarioGrupo.eliminado==False)
            if grupo_usuario is None or grupo_usuario.count() == 0:
                logger_config.logger.error("Usuario no pertenece a ningún grupo")
                raise Exception("Usuario no pertenece a ningún grupo")
            else:
                grupo_usuario = grupo_usuario.first()
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
                            fecha_actualizacion=datetime.now(),
                            rol=r['descripcion_rol'],
                            id_rol_ext=r['id_usuario_sistema_rol'],
                            descripcion_ext=caso_uso['descripcion_corta_cu']
                        )
                        db.session.add(nuevo_rol)

                        #for grupo in grupo_usuario:
                        nuevo_usuarioRol = UsuarioRol(
                                id=uuid.uuid4(),
                                id_usuario_grupo=grupo_usuario.id,
                                id_rol_ext=nuevoIDRol,
                                fecha_actualizacion=datetime.now(),
                                id_user_actualizacion=utils.get_username_id(username),
                                eliminado=False,
                                id_dominio=id_dominio
                            )
                        db.session.add(nuevo_usuarioRol)
                        
            db.session.commit()
        ##### EXPEDIENTES - Controlo si viene el rol en el encabezado ###########
        rol_usr = bool(rol_usuario)

        # Si no se recibió, obtengo todos los roles posibles del usuario
        if not rol_usr:
            query_roles = db.session.query(RolExt.rol).filter(
                RolExt.email == email
            ).distinct().all()

            if not query_roles:
                logger_config.logger.error("El usuario no tiene roles asignados")
                return False

            roles_usuario = [r.rol for r in query_roles]
        else:
            roles_usuario = [rol_usuario]

        # Construyo la base del query
        query = db.session.query(RolExt.descripcion_ext).filter(
            RolExt.email == email,
            RolExt.rol.in_(roles_usuario),
            RolExt.descripcion_ext.in_(casos)
        )

        # Si Pusher está disponible, agrego control de fecha
        if pusher_ok:
            query = query.filter(
                RolExt.fecha_actualizacion + tiempo_vencimiento >= datetime.now()
            )
        else:
            logger_config.logger.warning("P-USHER no está disponible, utilizando roles vencidos de la base de datos")

        # Ejecuto el query
        query_permisos = query.all()
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

    
