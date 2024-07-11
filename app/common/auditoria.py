# auditoria.py
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from datetime import datetime
from ..models.alch_model import Auditoria, Tarea, TipoTarea, Usuario, Grupo, HerarquiaGrupoGrupo  # Asegúrate de importar tus modelos correctamente
import json
import uuid

modelos = {Tarea, Usuario, Grupo, TipoTarea, HerarquiaGrupoGrupo}  # Asegúrate de agregar todos los modelos que te interesan
print ("entra a Auditoría")


def convert_to_serializable(value):
    if isinstance(value, uuid.UUID) or isinstance(value, datetime):
        return str(value)
    # Si hay otros tipos específicos que necesitas convertir, puedes manejarlos aquí.
    return value

def get_serializable_dict(instance):
    return {key: convert_to_serializable(value) for key, value in instance.__dict__.items() if not key.startswith('_sa_')}

@event.listens_for(Session, 'after_flush')
def after_flush(session, flush_context):

    for instance in session.new:
        if isinstance(instance, tuple(modelos)):  # Reemplaza Tarea con el nombre de tu modelo
            print("diccionario:",instance.__dict__)
            nuevoID=uuid.uuid4()
            auditoria = Auditoria(
                id = nuevoID,
                nombre_tabla=instance.__tablename__,
                id_registro=instance.id,
                operacion='INSERT',
                #datos_anteriores=json.dumps({}),
                #datos_nuevos=json.dumps(get_serializable_dict(instance)),
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=instance.id_user_actualizacion,
                ip_usuario='192.168.68.201'  # Aquí debes obtener la IP real del usuario
            )
            session.add(auditoria)

    for instance in session.dirty: # Update
        if isinstance(instance, Tarea):  # Reemplaza Tarea con el nombre de tu modelo
            state = inspect(instance)
            changes = {attr.key: (state.history[attr.key].deleted, state.history[attr.key].added)
                       for attr in state.mapper.attrs if state.history[attr.key].has_changes()}
            
            nuevoID=uuid.uuid4()
            auditoria = Auditoria(
                nombre_tabla='tarea',
                id_registro=instance.id,
                operacion='UPDATE',
                #datos_anteriores=instance._sa_instance_state.committed_state,
                datos_anteriores={k: convert_to_serializable(v[0]) for k, v in changes.items()},
                #datos_nuevos={k: convert_to_serializable(v[1]) for k, v in changes.items()},
                datos_nuevos=get_serializable_dict(instance),
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=instance.id_user_actualizacion,
                ip_usuario='192.168.68.201'  # Aquí debes obtener la IP real del usuario
            )
            session.add(auditoria)

    for instance in session.deleted:
        if isinstance(instance, Tarea):  # Reemplaza Tarea con el nombre de tu modelo
            nuevoID=uuid.uuid4()
            auditoria = Auditoria(
                nombre_tabla='tarea',
                id_registro=instance.id,
                operacion='DELETE',
                datos_anteriores=instance.__dict__,
                fecha_actualizacion=datetime.now(),
                usuario_actualizacion=instance.id_user_actualizacion,
                ip_usuario='192.168.68.201'  # Aquí debes obtener la IP real del usuario
            )
            session.add(auditoria)
