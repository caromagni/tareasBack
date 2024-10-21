# auditoria.py
from sqlalchemy import event
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.inspection import inspect
from datetime import datetime, date
from ..models.alch_model import Auditoria, Auditoria_Grupo, Auditoria_Tarea, Auditoria_TareaxGrupo, Auditoria_TareaAsignadaUsuario, TareaXGrupo, TareaAsignadaUsuario, Tarea, TipoTarea, Usuario, UsuarioGrupo, Grupo, HerarquiaGrupoGrupo 
import json
import uuid
from ..common.functions import get_user_ip

### modelos para los cuales se generará la auditoría ###
modelos = {Tarea, Usuario, UsuarioGrupo, Grupo, TipoTarea, HerarquiaGrupoGrupo, TareaXGrupo, TareaAsignadaUsuario} 

""" tablas_auditoria = {
    'tarea': Auditoria_Tarea,
    'grupo': Auditoria_Grupo,
    'tarea_x_grupo': Auditoria_TareaxGrupo,
    'tarea_asignada_usuario': Auditoria_TareaAsignadaUsuario,
    'auditoria': Auditoria
    # Otros mapeos de tablas
} """

def convert_to_serializable(value):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, list):
        return [convert_to_serializable(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(convert_to_serializable(item) for item in value)
    elif isinstance(value, dict):
        return {k: convert_to_serializable(v) for k, v in value.items()}
    try:
        # Intenta convertir cualquier otro objeto a cadena
        return str(value)
    except TypeError:
        # Si no puede ser convertido a string, deja el valor como None
        return None
        #return value

def get_serializable_dict(instance):
    return {key: convert_to_serializable(value) for key, value in instance.__dict__.items() if not key.startswith('_sa_')}
    """  try:
        return {key: convert_to_serializable(value) for key, value in instance.__dict__.items() if not key.startswith('_sa_')}
    except Exception as e:
        return ""     """
    #return {key: convert_to_serializable(value) for key, value in instance.__dict__.items() if not key.startswith('_sa_')}

@event.listens_for(scoped_session, 'after_flush')
def after_flush(session, flush_context):
    print("entra a after_flush")
    ip = get_user_ip()
    
    def get_nombre_tabla(modelo):
        print("modelo:", modelo)
        match modelo:
            case 'tarea':
                return 'Auditoria_Tarea'
            case 'grupo':
                return 'Auditoria_Grupo'
            case 'tarea_asignada_usuario':
                return 'Auditoria_TareaAsignadaUsuario'
            case 'tarea_x_grupo':
                print("entra a tarea_x_grupo")
                return 'Auditoria_TareaxGrupo'
            case _:
                return 'Auditoria'
    
    def get_user_actualizacion(instance):
        return str(instance.id_user_actualizacion) if hasattr(instance, 'id_user_actualizacion') else 'unknown'
    

    for instance in session.new:
        if isinstance(instance, tuple(modelos)):  
            print("Insert - Nombre de la tabla:", instance.__tablename__)
            nuevoID=uuid.uuid4()
            print("nuevoID:", nuevoID)
            tabla = get_nombre_tabla(instance.__tablename__)
            print("tabla:", tabla)
            tabla_auditoria = globals().get(f'{get_nombre_tabla(instance.__tablename__)}')
            #tabla_auditoria = tablas_auditoria.get(instance.__tablename__)
            print("#"*50)
            print("INSERT tabla_auditoria:", tabla)
            print("instance:", instance)
            auditoria = tabla_auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='INSERT',
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=get_user_actualizacion(instance),
                ip_usuario=ip
               # ip_usuario='192.168.68.201'  # obtener la IP real del usuario
                
            )
            print("auditoria:", auditoria)
            session.add(auditoria)
            
    for instance in session.dirty: # Update
        if isinstance(instance, tuple(modelos)):  
            print("Nombre de la tabla:", instance.__tablename__)
            state = inspect(instance)
            
            changes = {attr.key: (convert_to_serializable(attr.history.deleted[0]), convert_to_serializable(attr.history.added[0]))
                       for attr in state.attrs if attr.history.has_changes()}
            tabla = get_nombre_tabla(instance.__tablename__)
            tabla_auditoria = globals().get(f'{get_nombre_tabla(instance.__tablename__)}')
            nuevoID=uuid.uuid4()
            print("#"*50)
            print("UPDATE tabla_auditoria:", tabla)
            auditoria = tabla_auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='UPDATE',
                datos_anteriores={k: v[0] for k, v in changes.items()},
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=get_user_actualizacion(instance),
                ip_usuario=ip
            )
            session.add(auditoria)

    for instance in session.deleted:
        print("#"*50)
        print("instance:", instance)
        print("DELETE")
        if isinstance(instance, tuple(modelos)):  
            nuevoID=uuid.uuid4()
            tabla = get_nombre_tabla(instance.__tablename__)
            tabla_auditoria = globals().get(f'{get_nombre_tabla(instance.__tablename__)}')
            print("#"*50)
            print("DELETE tabla_auditoria:", tabla)
            auditoria = tabla_auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='DELETE',
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=get_user_actualizacion(instance),
                ip_usuario=ip
            )
            session.add(auditoria)
