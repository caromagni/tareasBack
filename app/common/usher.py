import requests
from models.alch_model import Usuario, RolExt, EP, UsuarioRol, UsuarioGrupo, Organismo, Dominio,Grupo
from datetime import date, timedelta, datetime
import common.logger_config as logger_config
import uuid
from db.alchemy_db import db
from sqlalchemy import or_
import os
import json
import common.utils as utils
from common.cache import *
import traceback

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
        logger_config.logger.info("url: %s", str(url))
        x_api_key=os.environ.get('PUSHER_API_KEY')
        x_api_system=os.environ.get('PUSHER_API_SYSTEM')
        logger_config.logger.info("getting roles from pusher")
        logger_config.logger.info("url: %s", str(url))
        logger_config.logger.info("USER TO RETRIEVE ROLES: %s", str(username))  
        starting_time = datetime.now()
        r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
        resp=r.json()
        ending_time = datetime.now()
        logger_config.logger.info("time taken to get roles from pusher: %s", ending_time - starting_time)
        if 'lista_roles_cus' in resp:
            logger_config.logger.info("user roles count from P-USHER: %s", str(len(resp['lista_roles_cus'])))
        else:
            logger_config.logger.error("Error de conexión con P-USHER ")
            #raise Exception(f"No se encontraron roles para el usuario {username}")
        return resp
    #except requests.exceptions.RequestException as e:
    except Exception as err:
        logger_config.logger.error(traceback.format_exc())
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
            print("cu encontrado desde base de datos:", str(item))
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
    id_grupo = ''  
    id_dominio = '' 
    
    #tiempo_vencimiento = timedelta(days=1)
    #tiempo_vencimiento = timedelta(hours=1)
    roles_expiry_time = os.environ.get('ROLES_EXPIRY_TIME', 30)
    #convert to float as required by timedelta

    tiempo_vencimiento = timedelta(minutes=float(roles_expiry_time))
    try:
        query_usr = db.session.query(Usuario).filter(Usuario.email == username).first()
        if query_usr is None:
            logger_config.logger.error("Usuario no encontrado")
            return False
        
        id_usuario = query_usr.id
        email = query_usr.email
        pull_roles = False
        #Pregunto si el usuario tiene un rol
        current_user_roles = db.session.query(RolExt).filter(RolExt.email == email).all()
        print("current_user_roles:", len(current_user_roles))
        print("**"*20)
        
        #Pregunto si hay algún registro vencido
        logger_config.logger.info("Controla roles vencidos")
        current_user_expired_roles = db.session.query(RolExt).filter(RolExt.email == email, RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()).all()
        print("current_user_expired_roles:", len(current_user_expired_roles))
        print("**"*20)
        
        #Traigo los roles del usuario desde P-USHER
        if len(current_user_roles)==0 or len(current_user_expired_roles)>0:
       
            #controlar si P-USHER no falla
            logger_config.logger.info("REQUEST PUSHER")
            roles = get_roles(username)
            #print("roles:", roles)
            if 'lista_roles_cus' in roles:
            #Borro todos los registros del usuario si existen roles nuevos desde P-USHER
                logger_config.logger.info("ROLES VENCIDOS")
               
                logger_config.logger.info("before delete expired roles")
                #needs to delete first the entry in usuario_rol as it has a foreign key to rol_ext
               
                logger_config.logger.info(f"proceeding to erase {len(current_user_expired_roles)} roles")
                for role in current_user_expired_roles:
                    db.session.query(UsuarioRol).filter(UsuarioRol.id_rol_ext == role.id).delete()
                logger_config.logger.info("after delete expired roles")
                current_user_expired_roles = db.session.query(RolExt).filter(RolExt.email == email, RolExt.fecha_actualizacion + tiempo_vencimiento < datetime.now()).delete()
                pull_roles = True
            else:
                logger_config.logger.error("Error al obtener roles desde P-USHER")
                pusher_ok = False
                pull_roles = False

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
            
            # Prepare bulk insert lists
            nuevos_roles = []
            nuevos_usuarios_roles = []
            current_time = datetime.now()
            id_user_actualizacion = utils.get_username_id(username)
            
            #roles = get_roles(username)
            for r in roles['lista_roles_cus']:
                ######ROL USHER##########
                print("rol:",r['descripcion_rol'])
                ########Obtengo id_dominio e id_grupo del organismo desde PUSHER##########
                print("#"*20)
                print("id_organismo:", r['id_organismo'])
                print("#"*20)
                id_organismo = r['id_organismo']
                query_organismo = db.session.query(Organismo).filter(Organismo.id_organismo_ext == id_organismo).first()
                if query_organismo is not None:
                    query_grupo=db.session.query(Grupo).filter(Grupo.id_organismo_ext == id_organismo).first()
                    id_grupo = query_grupo.id
                    #id_grupo = query_organismo.id_organismo_ext
                    query_dominio = db.session.query(Dominio).filter(Dominio.id_dominio_ext == query_organismo.id_dominio_ext).first()
                    if query_dominio is not None:
                        id_dominio = query_dominio.id_dominio_ext 
                        print("#"*20)
                        print("id_dominio:", id_dominio)
                        print("#"*20)

                print("id_organismo:", id_organismo)
                email = username
                print("email:", email)
                ######Casos de uso del rol##########
                for caso_uso in r['casos_de_uso']:
                    print("caso de uso:", caso_uso['descripcion_corta_cu']) 
                    nuevoIDRol = uuid.uuid4()
                    
                    # Create RolExt object (don't add to session yet)
                    nuevo_rol = RolExt(
                        id=nuevoIDRol, 
                        email=email,
                        fecha_actualizacion=current_time,
                        rol=r['descripcion_rol'],
                        id_rol_ext=r['id_usuario_sistema_rol_organismo'],
                        descripcion_ext=caso_uso['descripcion_corta_cu']
                    )
                    nuevos_roles.append(nuevo_rol)
                    #print("nuevo_rol:", nuevo_rol)

                    # Create UsuarioRol object (don't add to session yet)
                    nuevo_usuarioRol = UsuarioRol(
                        id=uuid.uuid4(),
                        id_usuario_grupo=grupo_usuario.id,
                        id_rol_ext=nuevoIDRol,
                        fecha_actualizacion=current_time,
                        id_user_actualizacion=id_user_actualizacion,
                        eliminado=False,
                        id_dominio_ext=id_dominio,
                        id_grupo=id_grupo
                    )
                    nuevos_usuarios_roles.append(nuevo_usuarioRol)
                    #print("nuevo_usuarioRol:", nuevo_usuarioRol)
            # Bulk insert all RolExt objects at once
            if nuevos_roles:
                db.session.bulk_save_objects(nuevos_roles)
                logger_config.logger.info(f"Bulk inserted {len(nuevos_roles)} RolExt records")
            
            # Bulk insert all UsuarioRol objects at once
            if nuevos_usuarios_roles:
                db.session.bulk_save_objects(nuevos_usuarios_roles)
                logger_config.logger.info(f"Bulk inserted {len(nuevos_usuarios_roles)} UsuarioRol records")
                        
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
            logger_config.logger.error(f"query_permisos: {query_permisos}")
            logger_config.logger.error("No tiene permisos")
            return False
        else:
            logger_config.logger.info(f"query_permisos: {query_permisos}")
            logger_config.logger.info("Usuario tiene permisos")
            return True
    except requests.exceptions.RequestException as e:
        logger_config.logger.error(traceback.format_exc())
        logger_config.logger.error(f"Error en get_roles desde P-USHER: {e}")
        return False    
    except Exception as e:
        logger_config.logger.error(traceback.format_exc())
        logger_config.logger.error(f"Error en get_usr_cu: {e}")
        return False     

    
