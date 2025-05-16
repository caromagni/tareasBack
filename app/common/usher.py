import requests
from models.alch_model import Usuario, Rol, EP
from datetime import date, timedelta, datetime
from common.logger_config import logger
import uuid
from alchemy_db import db
from sqlalchemy import or_
import os

def get_roles(username=''):
    url=os.environ.get('PUSHER_URL')+username
    #url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta='+username 
    #simperiale@mail.jus.mendoza.gov.ar
    #r=requests.get(url,headers={'Authorization': 'Bearer '+token})
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
    
    resp=r.json()
    print("json roles:",resp)
    return resp

######################Casos de uso de la api######################
def get_api_cu(url=None):
    cu=[]
    if url is not None:
        cu_query= db.session.query(EP).filter(EP.url == url).first()
        if cu_query is not None:
            #print("caso de uso:",cu_query.caso_uso)
            cu=cu_query.caso_uso
       
    return cu

######################Control de acceso######################
def get_usr_cu(username=None, rol_usuario='', cu=None):
    logger.info("get_usr_cu - username: %s", username)
    logger.info("get_usr_cu - rol_usuario: %s", rol_usuario)
    logger.info("get_usr_cu - cu: %s", cu)
    if cu is None:
        logger.error("No hay casos de uso")
        return False
    
    pull_roles = True
    tiempo_vencimiento = timedelta(days=1)
    #tiempo_vencimiento = timedelta(minutes=30)
    query_usr = db.session.query(Usuario).filter(Usuario.email == username).first()
    if query_usr is None:
        logger.error("Usuario no encontrado")
        return False
    
    id_usuario = query_usr.id
    email = query_usr.email
    #Pregunto si el usuario tiene un rol
    query_rol = db.session.query(Rol).filter(Rol.email == email).all()
    if len(query_rol)>0:
        pull_roles = False
        #Pregunto si hay algún registro vencido
        logger.info("Controla roles vencidos")
        query_vencido = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento < datetime.now()).all()
        if len(query_vencido)>0:
            #Borro todos los registros del usuario
            logger.info("ROLES VENCIDOS")
            print("Borrando roles vencidos")
            query_vencido = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento < datetime.now()).delete()
            pull_roles = True    

    #######Consultar CU Api P-usher##########
    if pull_roles:
        logger.info("Get roles desde p-usher")
        roles = get_roles(username)
        for r in roles['lista_roles_cus']:
            ######ROL USHER##########
            #print("rol:",r['descripcion_rol'])
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
                #print("Nuevo Rol Guardado:",nuevo_rol.id)
            
        db.session.commit()
    
    #Controlo si el usuario con el rol elegido tiene permisos
    query_permisos = db.session.query(Rol).filter(Rol.email == email, Rol.rol == rol_usuario, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), or_(*[Rol.descripcion_ext.like(f"%{perm}%") for perm in cu])).all()
    if len(query_permisos)==0:
        logger.error("No tiene permisos")
        return False
    else:
        logger.info("Usuario tiene permisos")
        return True

    
