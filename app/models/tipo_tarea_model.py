import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import TipoTarea


def get_tipo_tarea_by_id(id):
    session: scoped_session = current_app.session
    
    res = session.query(tipo_tarea).filter(tipo_tarea.id == id).first()
    
    results = [] 

    if res is not None:
        # #Traigo los grupos del tipo_tarea
        # res_grupos = session.query(tipo_tarea.id_tipo_tarea, Grupo.id, Grupo.nombre
        #                           ).join(Grupo, Grupo.id==tipo_tareaGrupo.id_grupo).filter(tipo_tareaGrupo.id_tipo_tarea== res.id).all()
        
        # #Traigo los grupos hijos
        # res_tareas = session.query(tipo_tarea.id_tipo_tarea, Tarea.id, Tarea.titulo
        #                           ).join(Tarea, Tarea.id==TareaAsignadatipo_tarea.id_tipo_tarea).filter(TareaAsignadatipo_tarea.id_tipo_tarea== res.id).all()
        

        if res_tipo_tarea is not None:
            for row in res_tipo_tarea:
                tipo_tarea = {
                    "id": row.id,
                    "nombre": row.nombre
                }
                tipo_tarea.append(tipo_tarea)


        ###################Formatear el resultado####################
        result = {
            "id": res.id,
            "nombre": res.nombre,
            "descripcion": res.descripcion,
            "habilitado": res.habilitado,
            "codigo": res.codigo_humano,
        }

        results.append(result)
   
    else:
        return None
    
    return results 

def get_all_tipo_tareas():
    session: scoped_session = current_app.session
    return session.query(tipo_tarea).all()



def insert_tipo_tarea(id='', codigo_humano = '', nombre='', descripcion='', habilitado=None, id_user_actualizacion=None):
    
    session: scoped_session = current_app.session
    nuevoID_tipo_tarea=uuid.uuid4()
    print("nuevo_tipo_tarea:",nuevoID_tipo_tarea)
    nuevo_tipo_tarea = tipo_tarea(
        id=nuevoID_tipo_tarea,
        codigo_humano=codigo_humano,
        nombre=nombre,
        descripcion=descripcion,
        descripcion=descripcion,
        habilitado=habilitado,        
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    print("nuevo_tipo_tarea:",nuevo_tipo_tarea)
    session.add(nuevo_tipo_tarea)
    
    session.commit()

    return nuevo_tipo_tarea


def update_tipo_tarea(id='', **kwargs):
    session: scoped_session = current_app.session
    tipo_tarea = session.query(tipo_tarea).filter(tipo_tarea.id == id).first()
   
    if tipo_tarea is None:
        return None
    
    print("tipo_tarea encontrado:",tipo_tarea)

    update_data = {}
    if 'codigo_humano' in kwargs:
        tipo_tarea.codigo_humano = kwargs['codigo_humano']
    if 'nombre' in kwargs:
        tipo_tarea.nombre = kwargs['nombre']
    if 'descripcion' in kwargs:
        tipo_tarea.descripcion = kwargs['descripcion']
    if 'habilitado' in kwargs:
        tipo_tarea.habilitado = kwargs['habilitado']        
    if 'id_user_actualizacion' in kwargs:
        tipo_tarea.id_user_actualizacion = kwargs['id_user_actualizacion']

    tipo_tarea.fecha_actualizacion = datetime.now()

    session.commit()
    return tipo_tarea

