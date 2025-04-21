import requests
from models.alch_model import Usuario, Rol
from datetime import date, timedelta, datetime
from common.logger_config import logger
import uuid
from alchemy_db import db
import os

def get_roles():
    print('get_roles')
    #url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas'
    url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=simperiale@mail.jus.mendoza.gov.ar'
    #r=requests.get(url,headers={'Authorization': 'Bearer '+token})
    #x_api_key='CMEHOcd6gHaFrmnR2ryQrlPMTBM9XWsd'
    x_api_key=os.environ.get('PUSHER_API_KEY')
    x_api_system=os.environ.get('PUSHER_API_SYSTEM')
    #x_api_system='back_test'
    r=requests.get(url,headers={'x-api-key': x_api_key, 'x-api-system': x_api_system})
    
    resp=r.json()
    print("json roles:",resp)
    return resp


######################Control de acceso######################
def get_usr_cu(nombre_usuario=None, rol='', cu=''):
    tiempo_vencimiento = timedelta(days=360)
    query_usr = db.session.query(Usuario).filter(Usuario.email == nombre_usuario).first()
    if query_usr is None:
        logger.error("Usuario no encontrado")
        return False
    else:
        id_usuario = query_usr.id
        email = query_usr.email
        query_rol = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now()).all()
        if len(query_rol)==0:
            #######Consultar CU Api Usher##########
            roles = get_roles()
            for r in roles['lista_roles_cus']:
                ######ROL USHER##########
                print("rol:",r['descripcion_rol'])
                ######Casos de uso del rol##########
                for cu in r['casos_de_uso']:
                    nuevoIDRol=uuid.uuid4()
                    nuevo_rol = Rol(
                        id=nuevoIDRol, 
                        email=email,
                        id_usuario=id_usuario, 
                        fecha_actualizacion=datetime.now(),
                        rol=r['descripcion_rol'],
                        id_rol_ext=r['id_usuario_sistema_rol'],
                        descripcion_ext=cu['descripcion_corta_cu']
                    )
                    db.session.add(nuevo_rol)
                    db.session.commit()
                    print("Nuevo Rol Guardado:",nuevo_rol.id)
                
            db.session.commit()
            
        #query_permisos = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), Rol.url_api.like(f"%{url_api}%")).all()
        print("email:",email)
        print("cu:",cu)
        query_permisos = db.session.query(Rol).filter(Rol.email == email, Rol.fecha_actualizacion + tiempo_vencimiento >= datetime.now(), Rol.descripcion_ext.like(f"%{cu}%")).all()
        if len(query_permisos)==0:
            logger.error("No tiene permisos")
            return False
        else:
            return True
            
    
