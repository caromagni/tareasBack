import uuid
from sqlalchemy.orm import scoped_session, joinedload
from datetime import datetime, timedelta
from common.functions import controla_fecha
from common.utils import *
from common.error_handling import ValidationError
from flask import current_app
from alchemy_db import db
from .alch_model import Nota, TipoNota, Tarea, Usuario, TareaAsignadaUsuario, Grupo, TareaXGrupo, Inhabilidad
import traceback
##########################  TIPO NOTAS #############################################

def get_all_tipo_nota(page=1, per_page=10):
    print("get_tipo_notas - ", page, "-", per_page)
    
    todo = db.session.query(TipoNota).all()
    total= len(todo)
    res = db.session.query(TipoNota).order_by(TipoNota.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_nota(username=None, id='', nombre='', id_user_actualizacion='', habilitado=True, eliminado=False):
    
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")
    
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

    db.session.add(nuevo_tipo_nota)
    db.session.commit()
    return nuevo_tipo_nota

def delete_tipo_nota(username=None, id=None):
    
    if id is None:
        raise ValidationError("ID de nota no ingresado")
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")
    
    tipo_nota = db.session.query(TipoNota).filter(TipoNota.id == id, TipoNota.eliminado==False).first()
    if tipo_nota is not None:
        tipo_nota.eliminado=True
        tipo_nota.fecha_actualizacion=datetime.now()
        tipo_nota.id_user_actualizacion=id_user_actualizacion
        tipo_nota.fecha_eliminacion=datetime.now()
        db.session.commit()
        return tipo_nota
    
    else:
        print("Tipo de nota no encontrado")
        return None
    

##########################  NOTAS #############################################

def insert_nota(username=None, titulo='', nota='', id_tipo_nota=None, eliminado=False, fecha_creacion=None, id_tarea=None):
    

    """ notas = db.session.query(Nota).filter(Nota.eliminado==False).all()
    
    if notas is not None:
        for n in notas:
            tareasnota = db.session.query(Tarea).filter(Tarea.id == n.id_tarea, Tarea.eliminado==False).first()
            if tareasnota is not None:
                tareasnota.tiene_notas_desnz=True    """
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")

    tarea_nota = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()

    if eliminado is None:
        eliminado=False
        
    if username is not None:
        id_user_creacion = verifica_username(username)

    tarea_nota = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()

    if tarea_nota is None:
        raise ValidationError("Tarea no encontrada")
    
    notastarea = db.session.query(Nota).filter(Nota.id_tarea == id_tarea, Nota.eliminado==False).all()
    
    if len(notastarea)==0:
        tarea_nota.tiene_notas_desnz=False

    print("NOTAS QUERIED")
    print("*************")
    try:
        nuevoID_nota=uuid.uuid4()

        nueva_nota = Nota(
        eliminado=eliminado,
        fecha_actualizacion=datetime.now(),
        fecha_creacion=datetime.now(),
        id_tarea=id_tarea,
        id_tipo_nota=id_tipo_nota,
        id_user_creacion=id_user_creacion,
        id_user_actualizacion=None,
        id=nuevoID_nota,
        nota=nota,
        titulo=titulo,
    )

        db.session.add(nueva_nota)

        
        tarea_nota.fecha_actualizacion=datetime.now()
        tarea_nota.id_user_actualizacion=id_user_creacion
        if eliminado==False:
            tarea_nota.tiene_notas_desnz=True

        db.session.commit()
        return nueva_nota
    
    except Exception as e:
        traceback.print_exc()
        print(f"Error inserting nota: {e}")
     #   raise
    

    

    

def update_nota(id='', **kwargs):
    
    nota = db.session.query(Nota).filter(Nota.id == id, Nota.eliminado==False).first()
   
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

    db.session.commit()
    return result

def get_all_nota(page=1, per_page=10, titulo='', id_tipo_nota=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), eliminado=None):
   
    
    
    print('consulta por fechas y id')
    print(fecha_desde)
    print(fecha_hasta)
    # # Convert fecha_desde to datetime object
    # if isinstance(fecha_desde, str):
    #     fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    
    # # Set fecha_hasta to current datetime if not provided
    # if fecha_hasta is None:
    #     fecha_hasta = datetime.now()

    # elif isinstance(fecha_hasta, str):
    #     fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')

    query = db.session.query(Nota).filter(Nota.fecha_creacion.between(fecha_desde, fecha_hasta), Nota.eliminado==False)
    # filter(Nota.fecha_creacion.between(fecha_desde, fecha_hasta))
    print('consulta por parámetros de notas')
    print("id tarea:",id_tarea)
    
    print(query.count())
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
    
    res = db.session.query(Nota).options(joinedload(Nota.tipo_nota)).filter(Nota.id == id).first()
    print('consulta notas por id')
    print(res)

    if res is not None:
        return res 
    else:
        print("Nota no encontrada")
        return None

def delete_nota(username=None, id_nota=None):
    
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado")  
    
    nota = db.session.query(Nota).filter(Nota.id == id_nota, Nota.eliminado==False).first()

    if nota is None:
        raise ValidationError("Nota no encontrada")
    
      
    if(nota.id_user_creacion != id_user_actualizacion):
        raise ValidationError("Usuario no autorizado para eliminar la nota")

    #print("Tarea de nota a eliminar:", nota.id_tarea)
            
    nota.eliminado=True
    nota.fecha_eliminacion=datetime.now()
    nota.fecha_actualizacion=datetime.now()
    nota.id_user_actualizacion=id_user_actualizacion

    tarea_nota = db.session.query(Tarea, Nota.id).join(Nota, Tarea.id==nota.id_tarea).filter(Tarea.eliminado==False, Nota.eliminado==False, Nota.id is not id_nota, Tarea.id==nota.id_tarea, Nota.id_tarea==nota.id_tarea).all()
    print("#"*50)
    #print("Tarea nota:", len(tarea_nota))
    #print("Tarea id:", nota.id_tarea)
    if len(tarea_nota)==0:
        tarea = db.session.query(Tarea).filter(Tarea.id==nota.id_tarea, Tarea.eliminado==False).first()
        tarea.tiene_notas_desnz=False
    """ else:
        print("Tarea tiene más notas")
        for t in tarea_nota:
            #print("Tarea con notas:", t.id)
            print("Nota a elimnar:", id_nota)
            print("Id de nota sin eliminar:", t.id) """
        
    
    

    
    db.session.commit()
    return nota    
    
   
