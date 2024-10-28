import uuid
from models.usuario_model import get_grupos_by_usuario
from sqlalchemy.orm import scoped_session, joinedload
from datetime import datetime, timedelta
from common.functions import controla_fecha
from models.grupo_hierarchy import find_parent_id_recursive

from flask import current_app

from models.alch_model import Label, Grupo, HerarquiaGrupoGrupo

    

##########################NOTAS #############################################
def buscar_grupo_padre_recursivo(id):
    session: scoped_session = current_app.session
    padre = session.query(Grupo.id,
                  Grupo.eliminado,          
                  HerarquiaGrupoGrupo.id_padre,
                  HerarquiaGrupoGrupo.id_hijo
                  ).join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_hijo
                  ).filter(HerarquiaGrupoGrupo.id_padre).all() 
    print('padre:', padre)
    
    if not padre:
        return id
    else:
        return buscar_grupo_padre_recursivo(padre.id)

def insert_label(nombre='', color= '', eliminado=False, fecha_eliminacion=None, fecha_actualizacion=None, id_user_creacion=None, id_grupo=None, fecha_creacion=None):
    session: scoped_session = current_app.session

    nuevoID_label=uuid.uuid4()
    # id_grupo = get_grupos_by_usuario(id_user_creacion)
    id_grupo_padre=find_parent_id_recursive(session, id_grupo)

    print('id_grupo_padre:', id_grupo_padre)

    nueva_label = Label(
        eliminado=eliminado,
        fecha_actualizacion=fecha_actualizacion,
        fecha_creacion=datetime.now(),
        fecha_eliminacion=fecha_eliminacion,
        id_user_creacion=id_user_creacion,
        id=nuevoID_label,
        color=color,
        id_grupo_padre=id_grupo_padre,
        nombre=nombre,
    )

    session.add(nueva_label)
       
    session.commit()
    return nueva_label

def update_label(id='', **kwargs):
    session: scoped_session = current_app.session
    label = session.query(Label).filter(Label.id == id, Label.eliminado==False).first()
   
    if label is None:
        return None
    
    if 'eliminado' in kwargs:
        label.eliminado = kwargs['eliminado']
    if 'id_tarea' in kwargs:
        label.id_tarea = kwargs['id_tarea']           
    if 'id_tipo_label' in kwargs:
        label.id_tipo_label = kwargs['id_tipo_label']
    if 'label' in kwargs:
        label.nombre = kwargs['nombre']
  
        
    label.fecha_actualizacion = datetime.now()
    

    ###################Formatear el resultado####################
    result = {
        "id": label.id,
        "titulo": label.titulo,
        "id_tipo_label": label.id_tipo_label,
        "tipo_label": label.tipo_label,
        "id_tarea": label.id_expediente,
        "label": label.label,
        "eliminado": label.eliminado,
        "fecha_eliminacion": label.fecha_eliminacion,
        "fecha_actualizacion": label.fecha_actualizacion,
        "fecha_creacion": label.fecha_creacion,
        
    }

    session.commit()
    return result


def get_all_label(page=1, per_page=10, nombre='', id_grupo_padre=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=None, eliminado=None, label_color=''):
   
    session: scoped_session = current_app.session
    
    # Convert fecha_desde to datetime object
    if isinstance(fecha_desde, str):
        fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    
    # Set fecha_hasta to current datetime if not provided
    if fecha_hasta is None:
        fecha_hasta = datetime.now()
    elif isinstance(fecha_hasta, str):
        fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')

    query = session.query(Label).filter(Label.fecha_creacion.between(fecha_desde, fecha_hasta))
    print('consulta por parámetros de labels')
    print(query)
    if nombre != '':
        query = query.filter(Label.nombre.ilike(f'%{nombre}%'))

    if id_grupo_padre is not None:
        query = query.filter(Label.id_grupo_padre== id_grupo_padre)

    if id_tarea is not None:
        query = query.filter(Label.id_tarea== id_tarea)

    if id_user_creacion is not None:
        query = query.filter(Label.id_user_creacion == id_user_creacion)

    if eliminado is not None:
        query = query.filter(Label.eliminado == eliminado)

    #muestra datos
    print("Query:", query.all())
    total= len(query.all()) 

    result = query.order_by(Label.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    return result, total

def get_label_by_id(id):
    session: scoped_session = current_app.session
    res = session.query(Label).filter(Label.id == id).first()
    print('consulta labels por id')
    print(res)

    if res is not None:
        return res 
    else:
        print("Label no encontrada")
        return None

def delete_label(id_label):
    session: scoped_session = current_app.session
    label = session.query(Label).filter(Label.id == id_label, Label.eliminado==False).first()
    print('label id a borrar:', label)
    if label is not None:              
        label.eliminado=True
        label.fecha_eliminacion=datetime.now()
        # label.fecha_actualizacion=datetime.now()
        session.commit()
        return label
    
    else:
        print("Label no encontrada")
        return None
