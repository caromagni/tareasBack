# coding: utf-8
from sqlalchemy import ARRAY, Boolean, CHAR, Column, DateTime, Date, ForeignKey, Integer, String, Table, Time, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

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

class Auditoria_Grupo(Base):
    __tablename__ = 'auditoria_grupo'
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

class Auditoria_Tarea(Base):
    __tablename__ = 'auditoria_tarea'
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

class Auditoria_TareaxGrupo(Base):
    __tablename__ = 'auditoria_tareaxgrupo'
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
    

class Auditoria_TareaAsignadaUsuario(Base):
    __tablename__ = 'auditoria_tarea_asignada_usuario'
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

class Organismo(Base):
    __tablename__ = 'organismo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_organismo_ext = Column(UUID, nullable=False)
    circunscripcion_judicial = Column(String, nullable=False)
    id_fuero = Column(UUID)
    descripcion = Column(String)
    descripcion_corta = Column(String)
    habilitado = Column(Boolean, nullable=False)
    eliminado = Column(Boolean,  default=False)
    id_tarea_grupo_base  = Column(UUID)
    instancia = Column(String)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    nombre = Column(String)
    apellido = Column(String)
    id_ext = Column(UUID)
    eliminado  = Column(Boolean, default=False)
    suspendido = Column(Boolean, default=False)
    username = Column(String)
    email = Column(String)
    dni = Column(String)
    id_persona_ext = Column(UUID)

class TipoActuacionExt(Base):
    __tablename__ = 'tipo_actuacion_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tipo_actuacion_ext = Column(UUID, nullable=False)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class ActuacionExt(Base):
    __tablename__ = 'actuacion_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_ext = Column(UUID)
    nombre = Column(String)
    #id_tipo_actuacion = Column(UUID)
    id_tipo_actuacion = Column(ForeignKey('tareas.tipo_actuacion_ext.id'), nullable=False)
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime, nullable=False)
    tipo_actuacion = relationship('TipoActuacionExt')


class AutoReglaAsignacion(Base):
    __tablename__ = 'auto_regla_asignacion'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    habilitado = Column(Boolean, nullable=False)
    eliminado = Column(Boolean, default=False)


class ExpedienteExt(Base):
    __tablename__ = 'expediente_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_ext = Column(UUID)
    caratula = Column(String)
    nro_expte= Column(String, default=None)
    estado = Column(String)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)

class URL(Base):
    __tablename__ = 'url'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tarea = Column(UUID)
    descripcion = Column(String)
    url= Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    
class Grupo(Base):
    __tablename__ = 'grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_dominio = Column(ForeignKey('tareas.dominio.id'), nullable=False)
    id_organismo = Column(ForeignKey('tareas.organismo.id'), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    id_user_actualizacion = Column(ForeignKey('tareas.usuario.id'))
    id_user_asignado_default = Column(ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime, nullable=False)
    eliminado  = Column(Boolean, default=False)
    suspendido = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_hasta = Column(DateTime, nullable=True)
    base = Column(Boolean, default=False)
    user_actualizacion = relationship('Usuario', foreign_keys=[id_user_actualizacion])
    user_asignado_default= relationship('Usuario', foreign_keys=[id_user_asignado_default])
    organismo = relationship('Organismo', foreign_keys=[id_organismo])
    dominio = relationship('Dominio', foreign_keys=[id_dominio])

class HerarquiaGrupoGrupo(Base):
    __tablename__ = 'herarquia_grupo_grupo'
    __table_args__ = {'schema': 'tareas', 'comment': 'relaciona grupos entre si, por ejemplo un grupo padre puede tener varios grupos hijos. esto permite crear una estructura de grupos jerarquica.'}

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
    __table_args__ = {'schema': 'tareas', 'comment': 'campo libre de labels que puede tener en principio 3 niveles de visibilidad, personal, juzgado y externo(abogados)'}

    eliminado = Column(Boolean)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_eliminacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    #id = Column(UUID, primary_key=True)
    id_label = Column('id', UUID, primary_key=True)
    id_grupo_base = Column(UUID)
    id_user_creacion = Column(UUID, nullable=False)
    id_user_actualizacion = Column(UUID)
    nombre = Column(String)
    color = Column(String)


# t_multimedia = Table(
#     'multimedia', metadata,
#     Column('id', UUID, nullable=False),
#     Column('link', String),
#     Column('id_tipo_link', UUID),
#     Column('fecha_actualizacion', DateTime),
#     Column('id_user_actualizacion', UUID),
#     Column('id_entidad', UUID, nullable=False),
#     Column('nombre_entidad', String, nullable=False),
#     schema='tareas',
# )



class TipoAgrupacion(Base):
    __tablename__ = 'tipo_agrupacion'
    __table_args__ = {'schema': 'tareas', 'comment': 'un grupo de tareas puede ser de 1 tipo. este tipo determina si el grupo de tareas es "libre" o sea que cada tarea se puede finalizar u otro estado sin limites. en este caso el grupo seria para organizar solamente.\nsi el tipo del grupo es "secuencial" entonces las tareas solo se podran ir resolviendo / cerrando siguiendo el numero de orden.\nsi es de tipo "libre con tarea de cierre" entonces habra dentro del grupo de tareas una tarea que para poder cerrarla, todas las tareas anteriores deberan estar finalizadas.'}

    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    habilitado = Column(Boolean, nullable=False)
    eliminado = Column(Boolean, default=False)


class TipoInhabilidad(Base):
    __tablename__ = 'tipo_inhabilidad'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_inhabilidad_ext = Column(UUID)
    tipo = Column(String, nullable=False)
    nombre = Column(String)


class TipoNota(Base):
    __tablename__ = 'tipo_nota'
    __table_args__ = {'schema': 'tareas'}

    eliminado = Column(Boolean)
    fecha_actualizacion = Column(DateTime)
    fecha_eliminacion = Column(DateTime)
    eliminado = Column(Boolean, default=False)
    id = Column(UUID, primary_key=True)
    id_user_actualizacion = Column(UUID)
    nombre = Column(String, nullable=False)


class TipoTarea(Base):
    __tablename__ = 'tipo_tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_ext = Column(UUID)
    codigo_humano = Column(String)
    nombre = Column(String, nullable=False)
    eliminado = Column(Boolean, nullable=False, default=False)
    suspendido = Column(Boolean, default=False)
    id_user_actualizacion  = Column(ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime, nullable=False)
    base = Column(Boolean, default=False)
    origen_externo = Column(Boolean, default=False)
    nivel = Column(String)
    id_dominio = Column(ForeignKey('tareas.dominio.id'), nullable=False)
    id_organismo = Column(ForeignKey('tareas.organismo.id'), nullable=False)

    user_actualizacion = relationship('Usuario')
    dominio = relationship('Dominio')
    organismo = relationship('Organismo')
    
class SubtipoTarea(Base):
    __tablename__ = 'subtipo_tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_ext = Column(UUID)
    id_tipo = Column(ForeignKey('tareas.tipo_tarea.id'), nullable=False)
    nombre = Column(String)
    nombre_corto = Column(String)
    eliminado = Column(Boolean, default=False)
    suspendido = Column(Boolean, default=False)
    id_user_actualizacion = Column(UUID, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    base = Column(Boolean, default=False)
    origen_externo = Column(Boolean, default=False)
    tipo_tarea = relationship('TipoTarea')

""" class TipoTareaDominio(Base):
    _tablename_ = 'tipo_tarea_x_dominio'
    _table_args_ = {
        'schema': 'tareas',
        'comment': 'Relación entre tipo de tarea, dominio y organismo.'
    }

    id = Column(UUID, primary_key=True)
    id_dominio = Column(ForeignKey('tareas.dominio.id'), nullable=False)
    id_tipo_tarea = Column(ForeignKey('tareas.tipo_tarea.id'), nullable=False)
    id_organismo = Column(ForeignKey('tareas.organismo.id'), nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)

    # Relaciones
    dominio = relationship('Dominio')
    tipo_tarea = relationship('TipoTarea')
    organismo = relationship('Organismo')     """

class Dominio(Base):
    __tablename__ = 'dominio'
    __table_args__ = {'schema': 'tareas', 'comment': 'los dominios son los fuero judiciales, por ejemplo civil, penal, laboral, etc. cada dominio puede tener uno o mas tipos de tarea asociados.'}

    id = Column(UUID, primary_key=True)
    id_dominio_ext = Column(UUID, nullable=False)
    descripcion = Column(String, nullable=False)
    descripcion_corta = Column(String, nullable=False)
    prefijo = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    habilitado = Column(Boolean, default=True)
    eliminado = Column(Boolean, default=False)
    id_user_actualizacion = Column(ForeignKey('tareas.usuario.id'), nullable=False)

class TipoTareaDominio(Base):
    __tablename__ = 'tipo_tarea_x_dominio'
    __table_args__ = {'schema': 'tareas', 'comment': 'relaciona los tipos de tarea con los dominios, para que cada tipo de tarea y subtipo se pueda clasificar y puede existir para mas de un dominio(fuero) y grupo.'}

    id = Column(UUID, primary_key=True)
    id_tipo_tarea = Column(ForeignKey('tareas.tipo_tarea.id'), nullable=False)
    id_dominio = Column(ForeignKey('tareas.dominio.id'), nullable=False)
    id_organismo = Column(ForeignKey('tareas.organismo.id'), nullable=False)
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    id_user_actualizacion = Column(ForeignKey('tareas.usuario.id'), nullable=False)

    tipo_tarea = relationship('TipoTarea')
    dominio = relationship('Dominio')
    organismo = relationship('Organismo')



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
    id_ext = Column(UUID)
    #id_tipo_inhabilidad = Column(ForeignKey('tareas.tipo_inhabilidad.id'), nullable=False)
    id_tipo_inhabilidad = Column(UUID)
    tipo = Column(String)
    id_organismo = Column(ForeignKey('tareas.organismo.id'), nullable=False)
    id_juez =Column(UUID)
    fecha_desde = Column(Time)
    fecha_hasta = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    descripcion = Column(String)
    eliminado = Column(Boolean, default=False)

    grupo = relationship('Grupo')
    organismo = relationship('Organismo')


class Tarea(Base):
    __tablename__ = 'tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    prioridad = Column(Integer, nullable=False, server_default=text("0"))
    id_actuacion = Column(ForeignKey('tareas.actuacion_ext.id'))
    titulo = Column(String)
    cuerpo = Column(String)
    id_expediente = Column(ForeignKey('tareas.expediente_ext.id'))
    caratula_expediente = Column(String)
    id_tipo_tarea = Column(ForeignKey('tareas.tipo_tarea.id'))
    id_subtipo_tarea = Column(ForeignKey('tareas.subtipo_tarea.id'))
    eliminable = Column(Boolean, default=True)
    fecha_eliminacion = Column(DateTime)
    id_usuario_asignado = Column(UUID)
    id_user_actualizacion = Column(ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime)
    fecha_creacion = Column(DateTime)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    plazo = Column(Integer)
    eliminado = Column(Boolean, default=False)
    estado = Column(Integer)
    tiene_notas_desnz = Column(Boolean, default=False)

    tipo_tarea = relationship('TipoTarea')
    subtipo_tarea = relationship('SubtipoTarea')
    grupo = relationship('Grupo')
    expediente = relationship('ExpedienteExt')
    actuacion = relationship('ActuacionExt')
    user_actualizacion = relationship('Usuario')

class UsuarioGrupo(Base):
    __tablename__ = 'usuario_grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    id_usuario = Column(ForeignKey('tareas.usuario.id'))
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    eliminado = Column(Boolean, default=False)

    grupo = relationship('Grupo')
    usuario = relationship('Usuario')

class RolExt(Base):
    __tablename__ = 'rol_ext'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    email = Column(String)
    rol = Column(String, nullable=False)
    id_rol_ext = Column(UUID)
    id_organismo = Column(UUID)
    descripcion_ext = Column(String)
    fecha_actualizacion = Column(DateTime)



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
    eliminado = Column(Boolean, default=False)
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)

    tarea = relationship('Tarea')


# t_label_x_tarea = Table(
#     'label_x_tarea', metadata,
#     Column('label_id', ForeignKey('tareas.label.id'), nullable=False),
#     Column('tarea_id', ForeignKey('tareas.tarea.id'), nullable=False),
#     Column('fecha_actualizacion', DateTime),
#     Column('id_user_actualizacion', UUID),
#     schema='tareas'
# )
class LabelXTarea(Base):
    __tablename__ = 'label_x_tarea'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tarea = Column(ForeignKey('tareas.tarea.id'))
    id_label = Column(ForeignKey('tareas.label.id'))
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    activa = Column(Boolean, default=False)

    label = relationship('Label')
    tarea = relationship('Tarea')

class Nota(Base):
    __tablename__ = 'nota'
    __table_args__ = {'schema': 'tareas', 'comment': 'campo libre de notas que puede tener en principio 3 niveles de visibilidad, personal, juzgado y externo(abogados)'}

    eliminado = Column(Boolean)
    fecha_actualizacion = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_eliminacion = Column(DateTime, nullable=False)
    id = Column(UUID, primary_key=True)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)
    id_tipo_nota = Column(ForeignKey('tareas.tipo_nota.id'), nullable=False)
    id_user_creacion = Column(ForeignKey('tareas.usuario.id'), nullable=False)
    id_user_actualizacion = Column(UUID)
    nota = Column(String)
    tarea = relationship('Tarea')
    tipo_nota = relationship('TipoNota')
    titulo = Column(String)
    user_creacion = relationship('Usuario')
    #usuario_actualizacion = relationship('Usuario')



class TareaAsignadaUsuario(Base):
    __tablename__ = 'tarea_asignada_usuario'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_usuario = Column(ForeignKey('tareas.usuario.id'), nullable=False)
    id_tarea = Column(ForeignKey('tareas.tarea.id'), nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    fecha_asignacion = Column(DateTime) 
    id_user_actualizacion= Column(UUID, nullable=False)
    notas = Column(String)
    eliminado = Column(Boolean, default=False)

    tarea = relationship('Tarea')
    usuario = relationship('Usuario')


class TareaXGrupo(Base):
    __tablename__ = 'tarea_x_grupo'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_tarea = Column(ForeignKey('tareas.tarea.id'))
    id_grupo = Column(ForeignKey('tareas.grupo.id'))
    id_user_actualizacion = Column(UUID)
    fecha_actualizacion = Column(DateTime)
    fecha_asignacion = Column(DateTime)
    eliminado = Column(Boolean, default=False)

    grupo = relationship('Grupo')
    tarea = relationship('Tarea')


class UsuarioRol(Base):
    __tablename__ = 'usuario_rol'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    id_usuario_grupo = Column(ForeignKey('tareas.usuario_grupo.id'), nullable=False)
    id_rol_ext = Column(ForeignKey('tareas.rol_ext.id'), nullable=False)
    base_desnz = Column(Boolean, default=False)
    fecha_actualizacion = Column(DateTime)
    id_user_actualizacion = Column(UUID)
    eliminado = Column(Boolean, default=False)
    id_dominio = Column(ForeignKey('tareas.dominio.id'), nullable=False)

    usuario_grupo = relationship('UsuarioGrupo')
    rol_ext = relationship('RolExt')
    dominio = relationship('Dominio')

class Parametros(Base):
    __tablename__ = 'parametros'
    __table_args__ = {'schema': 'tareas'}

    id = Column(UUID, primary_key=True)
    table = Column(String)
    columns = Column(ARRAY(String))
    activo = Column(Boolean)  

class EP(Base):
    __tablename__ = 'endpoint'
    __table_args__ = {'schema': 'tareas', 'comment': 'endpoints de la api y casos de uso permitidos para ser consumidos'}

    id = Column(UUID, primary_key=True)
    url = Column(String)
    descripcion = Column(String)
    caso_uso = Column(JSONB)
    metodo = Column(String)
    fecha_actualizacion = Column(DateTime, nullable=False)
    id_user_actualizacion = Column(UUID)


