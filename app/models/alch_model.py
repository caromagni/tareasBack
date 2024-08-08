# coding: utf-8
from sqlalchemy import ARRAY, Boolean, CHAR, Column, DateTime, Date, ForeignKey, Integer, String, Table, Time, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
Base = declarative_base()
metadata = Base.metadata

class Auditoria(Base):
    __tablename__ = 'auditoria'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    nombre_tabla = Column(String, nullable=False)
    id_registro = Column(UUID, nullable=False)
    operacion = Column(String, nullable=False)
    datos_anteriores = Column(JSONB)
    datos_nuevos = Column(JSONB)
    fecha_actualizacion = Column(DateTime, nullable=False)
    usuario_actualizacion = Column(String, nullable=False)
    ip_usuario = Column(String, nullable=False)

class Nomenclador(Base):
    __tablename__ = 'nomenclador'
    __table_args__ = {'schema': 'tareas'}

    c_oficppal = Column(CHAR(1), nullable=False)
    c_circun = Column(CHAR(1), nullable=False)
    c_oficina = Column(CHAR(2), nullable=False)
    c_nroficin = Column(CHAR(2), nullable=False)
    nroficin = Column(String(100), nullable=False)
    activo = Column(Boolean, nullable=False, server_default=text("true"))
    nomenclador = Column(CHAR(6), primary_key=True)
    desclarga = Column(String)
    lista = Column(Boolean)
    nroficin_corto = Column(String(20))
    desccorta = Column(String(30))
    codigo = Column(CHAR(6))
    publica_penal = Column(Boolean)
    tipo_oficina = Column(String(3))
    turnos = Column(Boolean, server_default=text("false"))
    turnos_pass = Column(String(100))
    turnos_des = Column(String(25))

class ActuacionExt(Base):
    __tablename__ = 'actuacion_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String)
    #id_tipo_actuacion = Column(UUID)
    id_tipo_actuacion = Column(ForeignKey('tareas.tipo_actuacion_ext.id'), nullable=False)
    tipo_actuacion = relationship('TipoActuacionExt')
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime, nullable=False)


class AutoReglaAsignacion(Base):
    __tablename__ = 'auto_regla_asignacion'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    habilitado = Column(Boolean, nullable=False)


class ExpedienteExt(Base):
    __tablename__ = 'expediente_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_ext = Column(UUID, nullable=False)
    caratula = Column(String)
    estado = Column(String)


class Grupo(Base):
    __tablename__ = 'grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_user_actualizacion = Column(UUID, nullable=False)
    fecha_actualizacion = Column(DateTime)
    nombre = Column(String)
    descripcion = Column(String)
    codigo_nomenclador = Column(ForeignKey('tareas.nomenclador.nomenclador'), nullable=False)
    eliminado  = Column(Boolean, default=False)
    nomenclador = relationship('Nomenclador')

class HerarquiaGrupoGrupo(Base):
    __tablename__ = 'herarquia_grupo_grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    #id_padre = Column(UUID)
    #id_hijo = Column(UUID)
    id_padre = Column(UUID, ForeignKey('tareas.grupo.id'))
    id_hijo = Column(UUID, ForeignKey('tareas.grupo.id'))
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    padre = relationship('Grupo', foreign_keys=[id_padre])
    hijo = relationship('Grupo', foreign_keys=[id_hijo])

class Label(Base):
    __tablename__ = 'label'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    codigo = Column(String, nullable=False)
    nombre = Column(String)
    fecha_actualizacion = Column(ARRAY(DateTime()), nullable=False)
    id_user_actualizacion = Column(UUID, nullable=False)
    descripcion = Column(String)


t_multimedia = Table(
    'multimedia', metadata,
    Column('id', UUID, nullable=False),
    Column('link', String),
    Column('id_tipo_link', UUID),
    Column('fecha_actualizacion', DateTime),
    Column('id_user_actualizacion', UUID),
    Column('id_entidad', UUID, nullable=False),
    Column('nombre_entidad', String, nullable=False),
    schema='tareas',
)


class TipoActuacionExt(Base):
    __tablename__ = 'tipo_actuacion_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tipo_actuacion_ext = Column(UUID, nullable=False)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class TipoAgrupacion(Base):
    __tablename__ = 'tipo_agrupacion'
    __table_args__ = {'schema': 'tareas', 'comment': 'un grupo de tareas puede ser de 1 tipo. este tipo determina si el grupo de tareas es "libre" o sea que cada tarea se puede finalizar u otro estado sin limites. en este caso el grupo seria para organizar solamente.\nsi el tipo del grupo es "secuencial" entonces las tareas solo se podran ir resolviendo / cerrando siguiendo el numero de orden.\nsi es de tipo "libre con tarea de cierre" entonces habra dentro del grupo de tareas una tarea que para poder cerrarla, todas las tareas anteriores deberan estar finalizadas.'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    habilitado = Column(Boolean, nullable=False)


class TipoInhabilidad(Base):
    __tablename__ = 'tipo_inhabilidad'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    tipo = Column(String, nullable=False)
    nombre = Column(String)


class TipoNota(Base):
    __tablename__ = 'tipo_nota'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    habilitado = Column(Boolean)


class TipoTarea(Base):
    __tablename__ = 'tipo_tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    codigo_humano = Column(String)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullabe=False)
    habilitado = Column(Boolean)
    id_user_actualizacion = Column(UUID, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    nombre = Column(String)
    apellido = Column(String)
    id_persona_ext = Column(UUID)


class AutoAccionAsignacion(Base):
    __tablename__ = 'auto_accion_asignacion'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_regla = Column(ForeignKey('tareas.auto_regla_asignacion.id'), nullable=False)
    id_grupo = Column(ForeignKey('tareas.grupo.id'), nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)

    grupo = relationship('Grupo')
    auto_regla_asignacion = relationship('AutoReglaAsignacion')


class AutoCondicionAsignacion(Base):
    __tablename__ = 'auto_condicion_asignacion'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_regla = Column(ForeignKey('tareas.auto_regla_asignacion.id'), nullable=False)
    atributo = Column(String, nullable=False)
    operador = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)

    auto_regla_asignacion = relationship('AutoReglaAsignacion')


class Inhabilidad(Base):
    __tablename__ = 'inhabilidad'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tipo_inhabilidad = Column(ForeignKey('tareas.tipo_inhabilidad.id'), nullable=False)
    fecha_desde = Column(Time)
    fecha_hasta = Column(DateTime)
    fecha_actualizacion = Column(DateTime, nullable=False)
    id_user_actualizacion = Column(UUID, nullable=False)
    id_grupo = Column(ForeignKey('tareas.grupo.id'))

    grupo = relationship('Grupo')
    tipo_inhabilidad = relationship('TipoInhabilidad')



class Tarea(Base):
    __tablename__ = 'tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_grupo = Column(ForeignKey('tareas.grupo.id'), nullable=False)
    prioridad = Column(Integer, nullable=False, server_default=text("0"))
    id_actuacion = Column(ForeignKey('tareas.actuacion_ext.id'))
    titulo = Column(String)
    cuerpo = Column(String)
    id_expediente = Column(ForeignKey('tareas.expediente_ext.id'))
    caratula_expediente = Column(String)
    id_tipo_tarea = Column(ForeignKey('tareas.tipo_tarea.id'), nullable=False)
    eliminable = Column(Boolean)
    fecha_eliminacion = Column(DateTime)
    id_usuario_asignado = Column(UUID)
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    fecha_creacion = Column(DateTime)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    plazo = Column(Integer)
    eliminado = Column(Boolean, default=False)

    tipo_tarea = relationship('TipoTarea')
    grupo = relationship('Grupo')
    expediente = relationship('ExpedienteExt')
    actuacion = relationship('ActuacionExt')

class UsuarioGrupo(Base):
    __tablename__ = 'usuario_grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    id_usuario = Column(ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)

    grupo = relationship('Grupo')
    usuario = relationship('Usuario')


class Agrupacion(Base):
    __tablename__ = 'agrupacion'
    __table_args__ = {'schema': 'tareas', 'comment': 'agrupa tareas para poderlas trabajar en conjunto. por ejemplo se pueden crear 4 tareas agrupadas de manera que 3 de esas tareas podrian ser de tipo notificar. y una cuarta tarea que sea de tipo remision. el id_conjunto es el que determina las tareas agrupadas. el numero de orden sirve para en el caso de que asi se desee, respetar el orden en el cual se van resolviendo las tareas.'}

    id = Column(UUID, primary_key=True)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    numero_orden = Column(Integer)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)
    id_conjunto = Column(UUID, nullable=False)
    id_tipo_agrupacion = Column(ForeignKey('tareas.tipo_agrupacion.id'), nullable=False)

    tarea = relationship('Tarea')
    tipo_agrupacion = relationship('TipoAgrupacion')


class FechaIntermedia(Base):
    __tablename__ = 'fecha_intermedia'
    __table_args__ = {'schema': 'tareas', 'comment': 'fechas de plazos intermedios que sirven a modo de alerta para uso general de la tarea'}

    id = Column(UUID, primary_key=True)
    fecha_alerta = Column(DateTime, nullable=False)
    mensaje = Column(String)
    apagada = Column(Boolean)
    habilitado = Column(Boolean)
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)

    tarea = relationship('Tarea')


t_label_x_tarea = Table(
    'label_x_tarea', metadata,
    Column('label_id', ForeignKey('tareas.label.id'), nullable=False),
    Column('tarea_id', ForeignKey('tareas.tarea.id'), nullable=False),
    Column('fecha_actualizacion', DateTime),
    Column('id_user_actualizacion', UUID),
    schema='tareas'
)


class Nota(Base):
    __tablename__ = 'nota'
    __table_args__ = {'schema': 'tareas', 'comment': 'campo libre de notas que puede tener en principio 3 niveles de visibilidad, personal, juzgado y externo(abogados)'}

    id = Column(UUID, primary_key=True)
    id_tipo_nota = Column(ForeignKey('tareas.tipo_nota.id'), nullable=False)
    nota = Column(String)
    fecha_actualizacion = Column(DateTime, nullable=False)
    id_usuario_actualizacion = Column(UUID)
    habilitado = Column(Boolean)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)

    tarea = relationship('Tarea')
    tipo_nota = relationship('TipoNota')


class TareaAsignadaUsuario(Base):
    __tablename__ = 'tarea_asignada_usuario'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_usuario = Column(ForeignKey('tareas.usuario.id'), nullable=False)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)
    fecha_asignacion = Column(DateTime, nullable=False)
    id_usuario_asignador = Column(UUID, nullable=False)
    notas = Column(String)

    tarea = relationship('Tarea')
    usuario = relationship('Usuario')


class TareaXGrupo(Base):
    __tablename__ = 'tarea_x_grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tarea = Column(ForeignKey('tareas.tarea.id'))
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    id_user = Column(UUID)
    fecha_actualizacion = Column(DateTime)

    grupo = relationship('Grupo')
    tarea = relationship('Tarea')
