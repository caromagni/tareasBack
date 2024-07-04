import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Grupo(Base):
    __tablename__ = 'grupo'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_user_actualizacion = Column(UUID(as_uuid=True))
    fecha_actualizacion = Column(DateTime(timezone=False))
    nombre = Column(String)
    descripcion = Column(String)

class HerarquiaGrupoGrupo(Base):
    __tablename__ = 'herarquia_grupo_grupo'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_padre = Column(UUID(as_uuid=True))
    id_hijo = Column(UUID(as_uuid=True))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    fecha_actualizacion = Column(DateTime(timezone=False))

class TipoTarea(Base):
    __tablename__ = 'tipo_tarea'
    __table_args__ = {'schema': 'tareas'}
    #id = Column(UUID(as_uuid=True), primary_key=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo_humano = Column(String)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    id_user_actualizacion = Column(UUID(as_uuid=True), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)


class Tarea(Base):
    __tablename__ = 'tarea'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_grupo = Column(UUID(as_uuid=True), ForeignKey('tareas.grupo.id'), nullable=False)
    prioridad = Column(Integer, nullable=False, default=0)
    id_actuacion = Column(UUID(as_uuid=True))
    titulo = Column(String)
    cuerpo = Column(String)
    id_expediente = Column(UUID(as_uuid=True))
    caratula_expediente = Column(String)
    id_tipo_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tipo_tarea.id'), nullable=False)
    eliminable = Column(Boolean)
    fecha_eliminacion = Column(DateTime(timezone=False))

    grupo = relationship('Grupo')
    tipo_tarea = relationship('TipoTarea')

class TareaXGrupo(Base):
    __tablename__ = 'tarea_x_grupo'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'))
    id_grupo = Column(UUID(as_uuid=True), ForeignKey('tareas.grupo.id'))
    id_user = Column(UUID(as_uuid=True))
    fecha_actualizacion = Column(DateTime(timezone=False))

class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'tareas'}
    #id = Column(UUID(as_uuid=True), primary_key=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    nombre = Column(String, nullable=False)
    apellido = Column(String)
    id_persona_ext = Column(UUID(as_uuid=True))

class UsuarioGrupo(Base):
    __tablename__ = 'usuario_grupo'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_grupo = Column(UUID(as_uuid=True), ForeignKey('tareas.grupo.id'))
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime(timezone=False))


class Label(Base):
    __tablename__ = 'label'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    codigo = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)
    id_user_actualizacion = Column(UUID(as_uuid=True), nullable=False)

class LabelXTarea(Base):
    __tablename__ = 'label_x_tarea'
    __table_args__ = {'schema': 'tareas'}
    label_id = Column(UUID(as_uuid=True), ForeignKey('tareas.label.id'), primary_key=True)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'), primary_key=True)
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))

class Inhabilidad(Base):
    __tablename__ = 'inhabilidad'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_tipo_inhabilidad = Column(UUID(as_uuid=True), ForeignKey('tareas.tipo_inhabilidad.id'), nullable=False)
    fecha_desde = Column(Time)
    fecha_hasta = Column(DateTime(timezone=False))
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)
    id_user_actualizacion = Column(UUID(as_uuid=True), nullable=False)
    id_grupo = Column(UUID(as_uuid=True), ForeignKey('tareas.grupo.id'))

    tipo_inhabilidad = relationship('TipoInhabilidad')

class TipoInhabilidad(Base):
    __tablename__ = 'tipo_inhabilidad'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    tipo = Column(String, nullable=False)
    nombre = Column(String, nullable=False)

class Agrupacion(Base):
    __tablename__ = 'agrupacion'
    __table_args__ = {'schema': 'tareas', 'comment': 'agrupa tareas para poderlas trabajar en conjunto. por ejemplo se pueden crear 4 tareas agrupadas de manera que 3 de esas tareas podrian ser de tipo notificar. y una cuarta tarea que sea de tipo remision. el id_conjunto es el que determina las tareas agrupadas. el numero de orden sirve para en el caso de que asi se desee, respetar el orden en el cual se van resolviendo las tareas.'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    numero_orden = Column(Integer)
    id_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'), nullable=False)
    id_conjunto = Column(UUID(as_uuid=True), nullable=False)
    id_tipo_agrupacion = Column(UUID(as_uuid=True), ForeignKey('tareas.tipo_agrupacion.id'), nullable=False)

    tipo_agrupacion = relationship('TipoAgrupacion')

class TipoAgrupacion(Base):
    __tablename__ = 'tipo_agrupacion'
    __table_args__ = {'schema': 'tareas', 'comment': 'un grupo de tareas puede ser de 1 tipo. este tipo determina si el grupo de tareas es "libre" o sea que cada tarea se puede finalizar u otro estado sin limites. en este caso el grupo seria para organizar solamente. si el tipo del grupo es "secuencial" entonces las tareas solo se podran ir resolviendo / cerrando siguiendo el numero de orden. si es de tipo "libre con tarea de cierre" entonces habra dentro del grupo de tareas una tarea que para poder cerrarla, todas las tareas anteriores deberan estar finalizadas.'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    habilitado = Column(Boolean, nullable=False)

class Nota(Base):
    __tablename__ = 'nota'
    __table_args__ = {'schema': 'tareas', 'comment': 'campo libre de notas que puede tener en principio 3 niveles de visibilidad, personal, juzgado y externo(abogados)'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_tipo_nota = Column(UUID(as_uuid=True), ForeignKey('tareas.tipo_nota.id'), nullable=False)
    nota = Column(String)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)
    id_user_actualizacion = Column(UUID(as_uuid=True))
    habilitado = Column(Boolean)
    id_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'), nullable=False)

    tipo_nota = relationship('TipoNota')

class TipoNota(Base):
    __tablename__ = 'tipo_nota'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    habilitado = Column(Boolean)

class Multimedia(Base):
    __tablename__ = 'multimedia'
    __table_args__ = {'schema': 'tareas', 'comment': 'contenido multimedia en forma de link que puede estar asociado a cualquier entidad. ya sea una tarea , una nota, un grupo, un usuario etc. nombre entidad refiere al nombre de la tabla que puede tener una entrada de tipo multimedia , id entidad es el id de la entrada en alguna de esas tablas que tiene multimedia asociado'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    link = Column(String)
    id_tipo_link = Column(UUID(as_uuid=True))
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_user_actualizacion = Column(UUID(as_uuid=True))
    id_entidad = Column(UUID(as_uuid=True), nullable=False)
    nombre_entidad = Column(String, nullable=False)

class TipoActuacionExt(Base):
    __tablename__ = 'tipo_actuacion_ext'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_tipo_actuacion_ext = Column(UUID(as_uuid=True), nullable=False)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)

class FechaIntermedia(Base):
    __tablename__ = 'fecha_intermedia'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    fecha_alerta = Column(DateTime(timezone=False))
    mensaje = Column(String)
    apagada = Column(Boolean)
    habilitado = Column(Boolean)
    id_user_actualizacion = Column(UUID(as_uuid=True), ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime(timezone=False))
    id_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'), nullable=False)
    
    usuario = relationship('Usuario', foreign_keys=[id_user_actualizacion])

class AutoReglaAsignacion(Base):
    __tablename__ = 'auto_regla_asignacion'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False))
    habilitado = Column(Boolean, nullable=False)

class AutoCondicionAsignacion(Base):
    __tablename__ = 'auto_condicion_asignacion'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_regla = Column(UUID(as_uuid=True), ForeignKey('tareas.auto_regla_asignacion.id'), nullable=False)
    atributo = Column(String, nullable=False)
    operador = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)

    regla_asignacion = relationship('AutoReglaAsignacion')

class AutoAccionAsignacion(Base):
    __tablename__ = 'auto_accion_asignacion'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_regla = Column(UUID(as_uuid=True), ForeignKey('tareas.auto_regla_asignacion.id'), nullable=False)
    id_grupo = Column(UUID(as_uuid=True), ForeignKey('tareas.grupo.id'), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=False), nullable=False)

    regla_asignacion = relationship('AutoReglaAsignacion')
    grupo = relationship('Grupo')

class TareaAsignadaUsuario(Base):
    __tablename__ = 'tarea_asignada_usuario'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('tareas.usuario.id'), nullable=False)
    id_tarea = Column(UUID(as_uuid=True), ForeignKey('tareas.tarea.id'), nullable=False)
    fecha_asignacion = Column(DateTime(timezone=False), nullable=False)
    id_usuario_asignador = Column(UUID(as_uuid=True), nullable=False)
    notas = Column(String)

    usuario = relationship('Usuario', foreign_keys=[id_usuario])
    tarea = relationship('Tarea')

class ExpedienteExt(Base):
    __tablename__ = 'expediente_ext'
    __table_args__ = {'schema': 'tareas'}
    id = Column(UUID(as_uuid=True), primary_key=True)
    id_ext = Column(UUID(as_uuid=True), nullable=False)
    caratula = Column(String)
    estado = Column(String)

# Optionally, add the comment on this table
# e.g.,
# COMMENT ON TABLE tareas.expediente_ext IS 'Comment on expediente_ext table';


# Optionally, add the comment on this table
# e.g.,
# COMMENT ON TABLE tareas.tipo_tarea IS 'Comment on tipo_tarea table';

# Optionally, add comments on the tables that are missing
# COMMENT ON TABLE tareas.<table_name> IS 'Comment on <table_name> table';

# Optionally, add the comments on the columns that are missing
# e.g.,
# COMMENT ON COLUMN tareas.<table_name>.<column_name> IS 'Comment on <column_name> column';
