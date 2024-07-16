# auditoria.py
from sqlalchemy import event
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.inspection import inspect
from datetime import datetime
from ..models.alch_model import Auditoria, Tarea, TipoTarea, Usuario, UsuarioGrupo, Grupo, HerarquiaGrupoGrupo 
import json
import uuid

modelos = {Tarea, Usuario, UsuarioGrupo, Grupo, TipoTarea, HerarquiaGrupoGrupo}  # Asegúrate de agregar todos los modelos que te interesan
print ("entra a Auditoría")


def convert_to_serializable(value):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, list):
        return [convert_to_serializable(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(convert_to_serializable(item) for item in value)
    elif isinstance(value, dict):
        return {k: convert_to_serializable(v) for k, v in value.items()}
    return value

def get_serializable_dict(instance):
    return {key: convert_to_serializable(value) for key, value in instance.__dict__.items() if not key.startswith('_sa_')}

@event.listens_for(scoped_session, 'after_flush')
def after_flush(session, flush_context):
    print("entra a after_flush")
    
    def get_user_actualizacion(instance):
        return str(instance.id_user_actualizacion) if hasattr(instance, 'id_user_actualizacion') else 'unknown'
    
    for instance in session.new:
        if isinstance(instance, tuple(modelos)):  # Reemplaza Tarea con el nombre de tu modelo
            print("diccionario:",instance.__dict__)
            nuevoID=uuid.uuid4()

            auditoria = Auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='INSERT',
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=get_user_actualizacion(instance),
                ip_usuario='192.168.68.201'  # obtener la IP real del usuario
            )
            session.add(auditoria)
            
    for instance in session.dirty: # Update
        if isinstance(instance, tuple(modelos)):  
            state = inspect(instance)
            
            changes = {attr.key: (convert_to_serializable(attr.history.deleted[0]), convert_to_serializable(attr.history.added[0]))
                       for attr in state.attrs if attr.history.has_changes()}
            
            print('changes:',changes)
            
            nuevoID=uuid.uuid4()
            auditoria = Auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='UPDATE',
                datos_anteriores={k: v[0] for k, v in changes.items()},
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=get_user_actualizacion(instance),
                ip_usuario='192.168.68.201'  # obtener la IP real del usuario
            )
            session.add(auditoria)

    for instance in session.deleted:
        if isinstance(instance, tuple(modelos)):  
            nuevoID=uuid.uuid4()
            auditoria = Auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='DELETE',
                datos_anteriores=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=instance.id_user_actualizacion,
                ip_usuario='192.168.68.201'  # Aquí debes obtener la IP real del usuario
            )
            session.add(auditoria)
