import uuid
from sqlalchemy.orm import scoped_session, joinedload
from datetime import datetime, timedelta
from common.functions import controla_fecha

from flask import current_app

from .alch_model import Nota, TipoNota, Usuario, TareaAsignadaUsuario, Grupo, TareaXGrupo, Inhabilidad


def get_all_tipo_nota(page=1, per_page=10):
    print("get_tipo_notas - ", page, "-", per_page)
    session: scoped_session = current_app.session
    todo = session.query(TipoNota).all()
    total= len(todo)
    res = session.query(TipoNota).order_by(TipoNota.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_nota(id='', nombre='', id_user_actualizacion='', habilitado=True, eliminado=False):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_nota = TipoNota(
        eliminado=False,
        fecha_actualizacion=datetime.now(),
        fecha_eliminacion=None,
        habilitado=True, 
        id_user_actualizacion=id_user_actualizacion,
        id=nuevoID,
        nombre=nombre,
    )

    session.add(nuevo_tipo_nota)
    session.commit()
    return nuevo_tipo_nota

def delete_tipo_nota(id):
    session: scoped_session = current_app.session
    tipo_nota = session.query(TipoNota).filter(TipoNota.id == id, TipoNota.eliminado==False).first()
    if tipo_nota is not None:
        tipo_nota.eliminado=True
        tipo_nota.fecha_actualizacion=datetime.now()
        session.commit()
        return tipo_nota
    else:
        print("Tipo de nota no encontrado")
        return None
    

##########################NOTAS #############################################

def insert_nota(titulo='', nota='', id_tipo_nota=None, eliminado=False, id_user_creacion=None, id_user_actualizacion=None, fecha_creacion=None, id_tarea=None):
    session: scoped_session = current_app.session

    nuevoID_nota=uuid.uuid4()

    nueva_nota = Nota(
        eliminado=eliminado,
        fecha_actualizacion=datetime.now(),
        fecha_creacion=datetime.now(),
        id_tarea=id_tarea,
        id_tipo_nota=id_tipo_nota,
        id_user_creacion=id_user_creacion,
        id_user_actualizacion=id_user_creacion,
        id=nuevoID_nota,
        nota=nota,
        titulo=titulo,
    )

    session.add(nueva_nota)
       
    session.commit()
    return nueva_nota

def update_nota(id='', **kwargs):
    session: scoped_session = current_app.session
    nota = session.query(Nota).filter(Nota.id == id, Nota.eliminado==False).first()
   
    if nota is None:
        return None
    
    if 'eliminado' in kwargs:
        nota.eliminado = kwargs['eliminado']
    if 'id_tarea' in kwargs:
        nota.id_tarea = kwargs['id_tarea']           
    if 'id_tipo_nota' in kwargs:
        nota.id_tipo_nota = kwargs['id_tipo_nota']
    if 'nota' in kwargs:
        nota.nota = kwargs['nota']
    if 'titulo' in kwargs:
        nota.titulo = kwargs['titulo'].upper()  
        
    nota.fecha_actualizacion = datetime.now()
    nota.id_user_actualizacion = kwargs['id_user_actualizacion']
    

    ###################Formatear el resultado####################
    result = {
        "id": nota.id,
        "titulo": nota.titulo,
        "id_tipo_nota": nota.id_tipo_nota,
        "tipo_nota": nota.tipo_nota,
        "id_tarea": nota.id_expediente,
        "nota": nota.nota,
        "eliminado": nota.eliminado,
        "id_user_creacion": nota.id_user_creacion,
        "user_creacion": nota.user_creacion,
        "id_user_actualizacion": nota.id_user_actualizacion,
        "fecha_eliminacion": nota.fecha_eliminacion,
        "fecha_actualizacion": nota.fecha_actualizacion,
        "fecha_creacion": nota.fecha_creacion,
        
    }

    session.commit()
    return result

def get_all_nota(page=1, per_page=10, titulo='', id_tipo_nota=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=None, eliminado=None):
   
    session: scoped_session = current_app.session
    
    # Convert fecha_desde to datetime object
    if isinstance(fecha_desde, str):
        fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    
    # Set fecha_hasta to current datetime if not provided
    if fecha_hasta is None:
        fecha_hasta = datetime.now()
    elif isinstance(fecha_hasta, str):
        fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')

    query = session.query(Nota).filter(Nota.fecha_creacion.between(fecha_desde, fecha_hasta))
    print('consulta por parámetros de notas')
    print("id tarea:",id_tarea)
    print(query)
    if titulo != '':
        query = query.filter(Nota.titulo.ilike(f'%{titulo}%'))

    if id_tipo_nota is not None:
        query = query.filter(Nota.id_tipo_nota== id_tipo_nota)

    if id_tarea is not None:
        query = query.filter(Nota.id_tarea== id_tarea)

    if id_user_creacion is not None:
        query = query.filter(Nota.id_user_creacion == id_user_creacion)

    if eliminado is not None:
        query = query.filter(Nota.eliminado == eliminado)

    #muestra datos
    print("Query:", query.all())
    total= len(query.all()) 

    result = query.order_by(Nota.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    return result, total

def get_nota_by_id(id):
    session: scoped_session = current_app.session
    res = session.query(Nota).options(joinedload(Nota.tipo_nota)).filter(Nota.id == id).first()
    print('consulta notas por id')
    print(res)

    if res is not None:
        return res 
    else:
        print("Nota no encontrada")
        return None

def delete_nota(id_nota):
    session: scoped_session = current_app.session
    nota = session.query(Nota).filter(Nota.id == id_nota, Nota.eliminado==False).first()
    if nota is not None:              
        nota.eliminado=True
        nota.fecha_eliminacion=datetime.now()
        nota.fecha_actualizacion=datetime.now()
        session.commit()
        return nota
    
    else:
        print("Nota no encontrada")
        return None
