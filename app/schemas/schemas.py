from os import link
from typing_extensions import Required
from marshmallow import fields, validate, ValidationError, post_dump
from enum import Enum
#from marshmallow_sqlalchemy.fields import Nested
from apiflask import Schema
from apiflask.fields import Integer, String, DateTime, Date, Boolean, Nested, List
from apiflask.validators import Length, OneOf
#from flask_marshmallow import Marshmallow

from models.alch_model import TipoTarea, Tarea
import re
from datetime import datetime
#ma = Marshmallow()

##########Funciones de validación ##############################    

def validate_fecha(f):
    #print("Mes:",int(f[3:5]))
    #print(int(f[0:4]))
    patron = re.compile(r"^(0[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[0-2])[-/]\d{4}$")
    
    if not patron.match(f):
        raise ValidationError("Campo fecha inválido - Ingrese dd/mm/aaaa")

    # Intentar convertir la fecha usando datetime.strptime con ambos formatos
    try:
        if '/' in f:
            datetime.strptime(f, "%d/%m/%Y")
        elif '-' in f:
            datetime.strptime(f, "%d-%m-%Y")
    except ValueError:
        raise ValidationError("Campo fecha inválido - Ingrese dd/mm/aaaa")
    
    

def validate_expte(n):
    nro_causa = n[0:1] + "-" + n[1:11].lstrip('0') + "/" + n[11:13]
    return nro_causa

def validate_char(f):
    cadena = f [:2]
    if not re.match(r'^[a-zA-Z]+$', cadena):
        raise ValidationError("El campo debe comenzar con letras")

def validate_char_num(f):
    if f.len() < 6 or f.len() > 250:
            raise ValidationError("El campo debe ser mayor a 6 y menor a 250 caracteres")

def validate_num(f):
    if not f.isdigit():
        raise ValidationError("El campo debe contener sólo números")
    
def validate_email(f):
    # Expresión regular para validar una dirección de correo electrónico
    if not re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', f):
        raise ValidationError("El campo debe contener una dirección de email válida.")    

##########Clase enum para los estados de las tareas ###############################
class EstadoEnum(Enum):
    pendiente = 1
    en_proceso = 2
    realizada = 3
    cancelada = 4

##########Schemas para joins ###############################   
class SmartNested(Nested):
    def serialize(self, attr, obj, accessor=None):
        if attr not in obj.__dict__:
            return {"id": int(getattr(obj, attr + "_id"))}
        return super(SmartNested, self).serialize(attr, obj, accessor)

############Header Schema####################
class HeaderSchema(Schema):
    api_system = String()
###############ApiFlask####################  
class PageIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
###############Prioridad y Estado####################
class EstadoSchema(Schema):
    id = fields.Integer()
    descripcion = fields.String()

class PrioridadSchema(Schema):
    id = fields.Integer()
    descripcion = fields.String()    
###############Nomenclador####################
class NomencladorOut(Schema):
    nomenclador = String()
    desclarga = String()
    nroficin_corto = String()

################Actuaciones####################
class TipoActuacionOut(Schema):
    id = String()
    nombre = String()

class ActuacionOut(Schema):
    id = String()
    nombre = String()
    id_tipo_actuacion = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()  
    tipo_actuacion=String()
    #tipo_actuacion = Nested(TipoActuacionOut, only=("id", "nombre"))

###############Expedientes####################
class ExpedienteOut(Schema):    
    id = String()
    id_ext = String()
    caratula = String()
    nro_expte = String()
    estado = String()
###############Listas####################
class ListUsuario(Schema):
    id_usuario = String(required=True)

class ListGrupo(Schema):
    id_grupo = String(required=True)    


class ListUsrGrupo(Schema):
    asignado_default = Boolean()  
    id_grupo = String() 
###############Groups####################
class HerarquiaGroupGroupInput(Schema):
    eliminado = Boolean()
    
class HerarquiaGroupGroupOut(Schema):
    id_padre = String()
    id_hijo = String()

class GroupHOut(Schema):
    id_padre = String()
    id_hijo = String()
    nombre_padre = String()
    nombre_hijo = String()

class HerarquiaOut(Schema):
    id_padre = String()
    id_hijo = String()
    nombre_padre = String()
    nombre_hijo = String()
    path = String()
    path_name = String()
    level = Integer()        


class HerarquiaAllOut(Schema):
    id_padre = String()
    parent_name = String()
    parent_description = String()
    id_hijo = String()
    child_name = String()
    child_description = String()
    child_eliminado = Boolean()
    path = String()
    level = Integer()
    is_parentless = Boolean()
    group_id = String()

class GroupIn(Schema):
    nombre= String(required=True, validate=[
        validate.Length(min=6, max=100, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    descripcion= String(required=True, validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    id_user_asignado_default= String()
    id_padre = String() 
    base = Boolean(default=False)
    codigo_nomenclador = String(validate=[
        validate.Length(min=6, max=6, error="El campo debe ser de 6 caracteres"),
        validate_num  
    ])

class GroupPatchIn(Schema):
    base = Boolean(default=False)
    nombre= String(validate=[
        validate.Length(min=6, max=100, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    descripcion= String(validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    id_user_asignado_default= String(allow_none=True)
    id_padre = String()  
    codigo_nomenclador = String(validate=[
        validate.Length(min=6, max=6, error="El campo debe ser de 6 caracteres"),
        validate_num  
    ])
    suspendido = Boolean()
    usuario = List(Nested(ListUsuario))

class GroupGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    eliminado = Boolean(default=False)
    suspendido = Boolean(default=False)
    path_name = Boolean(default=False)

class UsuarioDefaultOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida
    
    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class GetGroupOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioDefaultOut, only=("id", "nombre", "apellido", "nombre_completo"))
    id_user_asignado_default = String()
    user_asignado_default = Nested(UsuarioDefaultOut, only=("id", "nombre", "apellido", "nombre_completo"))
    fecha_actualizacion = String()
    fecha_creacion = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()
    suspendido = Boolean()
    path_name = String()
    path = String()
    level = Integer()
    base = Boolean()

class GroupxUsrOut(Schema):
    id_grupo = String()
    nombre = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()
    grupo_eliminado = Boolean()
    grupo_suspendido = Boolean()

class GroupOut(Schema):
    id_grupo = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioDefaultOut, only=("id", "nombre", "apellido", "nombre_completo"))
    id_user_asignado_default = String()
    user_asignado_default = Nested(UsuarioDefaultOut, only=("id", "nombre", "apellido", "nombre_completo"))
    fecha_actualizacion = String()
    fecha_creacion = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()
    suspendido = Boolean()
    path_name = String()
    path = String()
    level = Integer()
    base = Boolean()

class GroupDelOut(Schema):
    id_grupo = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioDefaultOut, only=("id", "nombre", "apellido", "nombre_completo"))
    id_user_asignado_default = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()
    suspendido = Boolean()
    base = Boolean()

class GroupTareaOut(Schema):
    id_grupo = String()
    nombre = String()
    descripcion = String()
    asignada = Boolean()
    fecha_asignacion = String()


class UsuarioGroupIdOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_ext = String()
    usr_eliminado = Boolean()
    usr_suspendido = Boolean()
    eliminado_grupo = Boolean()
    #nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida


class UsuarioGOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    activo = Boolean()

class HerarquiaGroupOut(Schema):
    id = String()
    id_hijo = String()
    nombre_hijo = String()
    id_padre = String()
    nombre_padre = String()
    eliminado = Boolean()



class MsgErrorOut(Schema):
    valido = String()
    ErrorCode = Integer()
    ErrorDesc = String()
    ErrorMsg = String()

class GroupsUsuarioOut(Schema):
    #id_usuario = String()
    #nombre = String()
    #apellido = String()
    id_grupo = String()
    nombre_grupo = String()
    codigo_nomenclador = String()
    descripcion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    fecha_creacion = String()
    fecha_hasta= String()
    fecha_actualizacion= String()
    id_user_actualizacion= String()
    
    
class GroupsBaseUsrOut(Schema):
    #id_usuario = String()
    #nombre = String()
    #apellido = String()
    id_padre = String()
    id_grupo = String()
    nombre_grupo = String()
    codigo_nomenclador = String()
    descripcion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    fecha_creacion = String()
    fecha_hasta= String()
    fecha_actualizacion= String()
    id_user_actualizacion= String()

class UsuariosGroupIn(Schema):
    grupos = String(metadata={"description": "ids separados por comas. Ej: id1, id2, id3"})
        
class UsuariosGroupOut(Schema):
    id_grupo = String()
    nombre_grupo = String()
    id_usuario = String()
    nombre = String()
    apellido = String()
    username = String()
    email = String()
    eliminado = Boolean()
    suspendido = Boolean()
    eliminado_grupo = Boolean()
    nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida
    
    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data
    
###############Tareas y Tipo de Tareas Base####################  
class TipoTareaIn(Schema):
    codigo_humano = String(required=True, validate=[
        validate.Length(min=4, max=20, error="El campo debe ser mayor a 4 caracteres y menor a 20 caracteres"),
        validate_char
    ])
    nombre = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    base = Boolean(default=False)

class TipoTareaPatchIn(Schema):
    codigo_humano = String(validate=[
        validate.Length(min=4, max=20, error="El campo debe ser mayor a 4 caracteres y menor a 20 caracteres"),
        validate_char
    ])
    nombre = String(validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    base = Boolean(default=False)

class TipoTareaOut(Schema):
    id = String()
    nombre = String()
    codigo_humano = String()
    id_user_actualizacion = String()
    eliminado = Boolean()
    base = Boolean()


class SubtipoTareaIn(Schema):
    id_tipo = String(required=True)
    nombre = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    base = Boolean(default=False)
    id_user_actualizacion = String()

class SubtipoTareaPatchIn(Schema):
    id_tipo = String()
    nombre = String(validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    base = Boolean(default=False)
    id_user_actualizacion = String()

class SubtipoTareaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    id_tipo_tarea = String()
    eliminado = Boolean()

class SubtipoTareaOut(Schema):
    id = String()
    id_tipo = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre"))
    nombre = String()
    eliminado = Boolean()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    base = Boolean()


class TareaxGroupOut(Schema):
    id = String()    
    titulo = String()
    estado = Integer()
    id_tipo_tarea = String()
    #tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre"))
    id_subtipo_tarea = String()
    #subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    fecha_creacion = String()
    fecha_inicio = String()
    fecha_fin = String()   

class GroupsBaseIn(Schema):
    id_grupo = String()
    usuarios = Boolean()

class GroupsBaseOut(Schema):
    id = String()
    id_padre = String()
    id_hijo = String()
    parent_name = String()
    child_name = String()
    path = String()
    path_name = String()
    is_parentless = Boolean()
    eliminado = Boolean()
    suspendido = Boolean()
    is_base = Boolean()
    usuarios = List(Nested(UsuariosGroupOut))
    
class GroupIdOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    base= Boolean()
    eliminado = Boolean()
    fecha_creacion = DateTime()
    fecha_actualizacion = DateTime()
    id_user_actualizacion = String()
    id_user_asignado_default = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga"))
    hijos = List(Nested(HerarquiaGroupOut, only=("id_hijo","nombre_hijo", "eliminado")))
    padre = List(Nested(HerarquiaGroupOut, only=("id_padre","nombre_padre", "eliminado")))
    usuarios = List(Nested(UsuarioGOut, only=("id", "nombre", "apellido","activo")))
    tareas = List(Nested(TareaxGroupOut))     

class UsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_ext = String()
    nombre_completo = String(dump_only=True)  
    username = String()
    email = String()
    dni = String()
    eliminado = Boolean()
    suspendido = Boolean()

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class TareaIn(Schema):
    prioridad = Integer(required=True, metadata={"description": "1 (alta), 2 (media), 3 (baja)"}, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String()
    titulo = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    cuerpo = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    id_expediente = String()
    caratula_expediente = String()
    nro_expte = String()
    nombre_actuacion= String()    
    id_tipo_tarea = String(required=True)
    id_subtipo_tarea = String()
    eliminable = Boolean()
    fecha_inicio = String(required=True, validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"},validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ), default=1)
    username = String()

class TareaPatchIn(Schema):
    prioridad = Integer(metadata={"description": "1 (alta), 2 (media), 3 (baja)"}, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String()
    titulo = String(validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    cuerpo = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    id_expediente = String()
    #caratula_expediente = String(validate=[
    #    validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
    #    validate_char
    #])
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    id_user_actualizacion = String()
    fecha_inicio = String(validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"},validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ))

class TareaPatchV2In(Schema):
    id_tarea = String(required=True)
    prioridad = Integer(metadata={"description": "1 (alta), 2 (media), 3 (baja)"}, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String()
    titulo = String(validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    cuerpo = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    id_expediente = String()
    caratula_expediente = String(validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    id_user_actualizacion = String()
    fecha_inicio = String(validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"},validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ))
    
class IdTarea(Schema):
    id = String()

class TareaPatchLoteV2In(Schema):
    upd_tarea = List(Nested(TareaPatchV2In))

class TareaPatchLoteIn(Schema):
    tareas = List(Nested(IdTarea))
    titulo = String()
    prioridad = Integer(metadata={"description": "1 (alta), 2 (media), 3 (baja)"}, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String()
    id_expediente = String()
    caratula_expediente = String(validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    id_user_actualizacion = String()
    fecha_inicio = String(validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"},validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ))
        
class TareaPatchLoteOut(Schema):
    tareas_error = List(String())
    tareas_ok = List(Nested(IdTarea))

class TipoNotaTareaOut(Schema):
    id = String()
    nombre = String()

class NotaTareaOut(Schema):
    id = String()
    titulo = String()
    nota = String()
    id_tipo_nota = String()
    fecha_creacion = String()
    id_user_creacion = String()
    user_creacion = Nested(UsuarioOut, only=("id", "nombre", "apellido", "nombre_completo"))
    id_user_actualizacion = String()
    tipo_nota = Nested(TipoNotaTareaOut, only=("id", "nombre")) 
    eliminado = Boolean()

class TareaOut(Schema):
    id = String()
    prioridad = Integer()
    estado = Integer()
    id_actuacion = String()
    actuacion = Nested(ActuacionOut, only=("id", "nombre"))
    titulo = String()
    cuerpo = String()
    id_expediente = String()
    expediente = Nested(ExpedienteOut, only=("id", "caratula", "nro_expte"))
    #caratula_expediente = String()
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_inicio = String()
    fecha_fin = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    id_user_actualizacion = String()
    user_actualizacion= Nested(UsuarioOut, only=("id","nombre","apellido","nombre_completo"))
    plazo = Integer()
    fecha_creacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    reasignada_usr = Boolean(default=False)
    reasignada_grupo = Boolean(default=False)
    notas = List(Nested(NotaTareaOut))
    tiene_notas = Boolean()

class TareaxGrupoOut(Schema):
    id = String()
    estado = Integer()
    titulo = String()
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    tarea_eliminado = Boolean()
    eliminado_grupo = Boolean()
    fecha_actualizacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    reasignada_usr = Boolean(default=False)
    reasignada_grupo = Boolean(default=False)

    #grupo = Nested(GroupOut, only=("id", "nombre"))
class LabelIdIn(Schema):
    id = String()  

class TareaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    id_tarea = String()
    id_usuario_asignado= String()
    titulo = String(default="")
    labels = String(metadata={"description": "ids separados por comas. Ej: id1, id2, id3"})
    grupos = String(metadata={"description": "ids separados por comas. Ej: id1, id2, id3"})
    #labels = List(String(), metadata={"description": "Array de IDs de labels (strings)"})
    id_tipo_tarea = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    fecha_fin_desde = String(validate=validate_fecha)
    fecha_fin_hasta = String(validate=validate_fecha)
    id_expediente = String()
    id_actuacion = String()
    prioridad = Integer(metadata={"description": "1 (alta), 2 (media), 3 (baja)"})
    eliminado = Boolean()
    tiene_notas = Boolean()
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"})
  
class TareaNotasGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    id_tarea = String()
    id_usuario_asignado= String()
    titulo = String(default="")
    id_tipo_tarea = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_expediente = String()
    id_actuacion = String()
    prioridad = Integer(metadata={"description": "1 (alta), 2 (media), 3 (baja)"})
    eliminado = Boolean()
    tiene_notas = Boolean()
    estado = Integer(metadata={"description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"})
  

####################Grupos - Tareas - Usuarios ####################
class GroupAllOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    id_user_asignado_default = String(required=True)
    fecha_actualizacion = String()
    fecha_creacion = String()
    id_user_actualizacion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    codigo_nomenclador = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    usuarios = List(Nested(UsuarioGroupIdOut))
    tareas = List(Nested(TareaxGrupoOut))

class GroupCountOut(Schema):
    count = Integer()
    data = Nested(GroupOut, many=True)

class GetGroupCountOut(Schema):
    count = Integer()
    data = Nested(GetGroupOut, many=True)

class GroupCountAllOut(Schema):
    count = Integer()
    data = Nested(GroupAllOut, many=True)

###############Usuario Base ####################
class UsuarioIn(Schema):
    nombre = String(required=True, validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 3 y menor a 30 caracteres"),
        validate_char
    ])
    apellido = String(required=True, validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 3 y menor a 30 caracteres"),
        validate_char
    ])
    #id_user_actualizacion = String()
    id_ext = String()
    grupo = List(Nested(ListUsrGrupo))
    dni = String(validate=[validate.Length(min=6, max=8, error="El campo documento debe tener entre 6 y 8 números") ,validate_num])
    email = String(validate=[validate.Length(min=6, max=254, error="El campo debe ser mayor a 6 y menor a 254 caracteres"), validate_email])
    username = String(validate=[validate.Length(min=4, max=200, error="El campo debe ser mayor a 4 y menor a 15 caracteres")])
 
    

class UsuarioInPatch(Schema):
    nombre = String(validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 3 y menor a 30 caracteres"),
        validate_char
    ])
    apellido = String(validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 3 y menor a 30 caracteres"),
        validate_char
    ])
    suspendido = Boolean()
    eliminado = Boolean()
    id_user_actualizacion = String()
    id_ext = String()
    grupo = List(Nested(ListUsrGrupo))
    dni = String(validate=[validate.Length(min=6, max=8, error="El campo documento debe tener entre 6 y 8 números") ,validate_num])
    email = String(validate=[validate.Length(min=6, max=254, error="El campo debe ser mayor a 6 y menor a 254 caracteres"), validate_email])
    #username = String(validate=[validate.Length(min=4, max=15, error="El campo debe ser mayor a 4 y menor a 15 caracteres")])
 

class UsuarioGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    apellido = String(default="")
    #id_grupo = String()
    dni = String()  
    username = String()
    eliminado = Boolean()
    suspendido = Boolean()


class UsuarioTareaOut(Schema):
    id_usuario = String()
    nombre = String()
    apellido = String()
    asignada = Boolean()
    fecha_asignacion = String()

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class DetalleUsuarioAllOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    nombre_completo = String(dump_only=True)
    id_ext = String()
    eliminado = Boolean()
    suspendido = Boolean()
    grupo = List(Nested(GroupxUsrOut))
    tareas = List(Nested(TareaOut, only=("id", "titulo", "id_tipo_tarea", "tipo_tarea","eliminado")))
    dni = String()
    email = String()
    username = String()

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data
    
class UsuarioAllOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    nombre_completo = String(dump_only=True)
    id_ext = String()
    eliminado = Boolean()
    suspendido = Boolean()
    grupo = List(Nested(GroupOut), only=("id_grupo", "nombre", "codigo_nomenclador", "nomenclador", "eliminado", "suspendido"))
    tareas = List(Nested(TareaOut, only=("id", "titulo", "id_tipo_tarea", "tipo_tarea","eliminado")))
    dni = String()
    email = String()
    username = String()

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class DetalleUsuarioCountAllOut(Schema):
    count = Integer()
    data = Nested(DetalleUsuarioAllOut, many=True) 

class UsuarioCountAllOut(Schema):
    count = Integer()
    data = Nested(UsuarioAllOut, many=True)


class UsuarioCountOut(Schema):
    count = Integer()
    data = Nested(UsuarioOut, many=True)     

class CasoUsoOut(Schema):
    id = String()
    descripcion_ext = String()

class UsuarioRolOut(Schema):
    #id = String()
    email = String()
    rol= String()
    usuario_cu = List(Nested(CasoUsoOut))


class UsuarioCountRolOut(Schema):
    count = Integer()
    data = Nested(UsuarioRolOut, many=True)

class TareaAllOut(Schema):
    id = String()
    #id_grupo = String()
    #prioridad = Integer()
    #estado = Integer()
    prioridad = fields.Nested(PrioridadSchema, metadata={
        "description": "1 (alta), 2 (media), 3 (baja)"
    })
    #prioridad = Integer()
    estado = fields.Nested(EstadoSchema, metadata={
        "description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"
    })
    #estado = Integer()
    id_actuacion = String()
    titulo = String()
    cuerpo = String()
    id_expediente = String()
    #caratula_expediente = String()
    expediente = Nested(ExpedienteOut, only=("id", "caratula", "nro_expte"))
    actuacion = Nested(ActuacionOut, only=("id", "nombre"))
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_inicio = String()
    fecha_fin = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioOut, only=("id","nombre","apellido","nombre_completo"))
    plazo = Integer()
    fecha_creacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    grupo = List(Nested(GroupTareaOut))
    usuario = List(Nested(UsuarioTareaOut))
    reasignada_usuario = Boolean()
    reasignada_grupo = Boolean()
    tiene_notas = Boolean()


class TareaPatchLoteV2Out(Schema):
    tareas_error = List(String())
    tareas_ok = List(Nested(TareaAllOut))

class TareaCountAllOut(Schema):
    count = Integer()
    data = Nested(TareaAllOut, many=True)

class TareaUsuarioIn(Schema):
    id_tarea = String(required=True)
    id_usuario = String(required=True)
    id_user_actualizacion = String()
    notas = String(validate=[
        validate.Length(min=4, error="El campo debe ser mayor a 4 caracteres"),
        validate_char
    ])

class TareaAlertaIn(Schema):
    dias_aviso = Integer(required=True)
    grupos_usr = Boolean(default=False)
    
class TareaUsrOut(Schema):
    id = String()
    titulo = String()
    reasignada=Boolean()
    fecha_inicio=String()
    fecha_fin=String()

class UsuarioIdOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    id_ext = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    dni = String()
    email = String()
    username = String()
    tareas = List(Nested(TareaUsrOut, only=("id", "titulo", "reasignada", "fecha_inicio", "fecha_fin")))
    grupo = List(Nested(GroupOut, only=("id_grupo", "nombre")))
    

class TipoTareaCountOut(Schema):
    count = Integer()
    data = Nested(TipoTareaOut, many=True)   

class SubtipoTareaCountOut(Schema):
    count = Integer()
    data = Nested(SubtipoTareaOut, many=True)         


class TareaCountOut(Schema):
    count = Integer()
    data = Nested(TareaOut, many=True)      

class TareaUsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    id_ext = String()
    nombre = String()
    apellido = String()
    id_grupo = String()
    grupo = String()

class UsuarioGroupTareaOut(Schema):
    id_usuario = String()
    nombre = String()
    apellido = String()
    asignada = Boolean()
    fecha_asignacion = String()
    grupos_usr = List(Nested(GroupOut, only=("id_grupo", "nombre")))

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class TareaIdOut(Schema):
    id = String()
    titulo = String()
    cuerpo = String()
    id_grupo = String()
    grupo = Nested(GroupOut, only=("id_grupo", "nombre"))
    prioridad = Integer()
    prioridad = fields.Nested(PrioridadSchema, metadata={
        "description": "1 (alta), 2 (media), 3 (baja)"
    })
    estado = fields.Nested(EstadoSchema, metadata={
        "description": "1 (pendiente), 2 (en proceso), 3 (realizada), 4 (cancelada)"
    })
    id_expediente = String()
    caratula_expediente = String()
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = DateTime()
    fecha_inicio = DateTime()
    fecha_fin = DateTime()
    plazo = Integer()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    grupo = List(Nested(GroupTareaOut))
    actuacion = Nested(ActuacionOut, only=("id", "nombre"))
    expediente = Nested(ExpedienteOut, only=("id", "caratula","nro_expte"))
    usuario = List(Nested(UsuarioGroupTareaOut))
    notas = List(Nested(NotaTareaOut))
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioOut, only=("id","nombre","apellido","nombre_completo"))
    reasignada_usuario = Boolean()
    reasignada_grupo = Boolean()

class TareaHIstoriaUserIdOut(Schema):
    id_task = String()
    titulo = String()
    id_usuario = String()
    apellido = String()
    username = String()
    eliminado = Boolean()
    eliminado_anterior = Boolean()
    fecha_actualizacion_anterior = String()
    #eliminado_nueva = Boolean()
    fecha_actualizacion = String()


class TareaxGrupoIdOut(Schema):
    id = String()
    titulo = String()
    cuerpo = String()
    prioridad = Integer()
    estado = Integer()
    id_actuacion = String()
    id_expediente = String()
    caratula_expediente = String()
    id_tipo_tarea = String()
    id_subtipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_inicio = String()
    fecha_fin = String()
    plazo = Integer()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    actuacion = Nested(ActuacionOut, only=("id", "nombre"))
    expediente = Nested(ExpedienteOut, only=("id", "caratula"))
    #usuarios = List(Nested(UsuarioTareaOut))
    #notas = List(Nested(NotaTareaOut))
    id_user_actualizacion = String()
    user_actualizacion = Nested(UsuarioOut, only=("id","nombre","apellido","nombre_completo"))


###############Marshmallow####################
class TipoTareaSchema(Schema):
    class Meta:
        model = TipoTarea
        include_relationships = True
        load_instance = True
        include_fk=True
    
    id = fields.String()
    codigo_humano = fields.String()
    nombre =fields.String() 
    id_user_actualizacion = fields.String() 
    fecha_actualizacion =fields.DateTime()

                                          

class TareaSchema(Schema):
    class Meta:
        model = Tarea
        include_relationships = True
        load_instance = True
        include_fk=True

    id = fields.String()
    id_grupo = fields.String()
    id_prioridad = fields.String()
    id_actuacion = fields.String()
    titulo = fields.String()
    cuerpo = fields.String()
    id_expediente = fields.String()
    caratula_expediente = fields.String()
    id_tipo_tarea = fields.String()
    eliminable = fields.Boolean()
    fecha_eliminacion = fields.DateTime()
    #tipo_tarea = fields.String() 
    tipo_tarea = fields.Nested(TipoTareaSchema, only=("id", "nombre"))  

############## Schemas de Entrada de Datos ##############################
    
class LoadFechaSchema(Schema):
    class Meta:
        ordered = True

    #expte = fields.String(required = True, validate=validate.Length(min=6, max=13))
    fecha_desde = fields.String(validate=validate_fecha)
    fecha_hasta = fields.String(validate=validate_fecha)
    expte = fields.String(validate=validate.Length(min=6, max=13))
    primer = fields.Boolean()



class LoadExpedienteSchema(Schema):
    class Meta:
        ordered = True

    expte = fields.String(required = True, validate=validate.Length(min=6, max=13))
    fecha_desde = fields.String(validate=validate_fecha)
    fecha_hasta = fields.String(validate=validate_fecha)
    primer = fields.Boolean()



############### Notas y Tipo de Notas Base####################  

class TipoNotaIn(Schema):
   
    nombre = String(required=True, validate=[
        validate.Length(min=3, max=25, error="El campo debe ser mayor a 6 y menor a 25 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    habilitado = Boolean()
    eliminado = Boolean()

class TipoNotaOut(Schema):
    id = String()
    nombre = String()
    id_user_actualizacion = String()
    eliminado = Boolean()
    habilitado = Boolean()

class TipoNotaCountOut(Schema):
    count = Integer()
    data = Nested(TipoNotaOut, many=True)   
 
    
class NotaIn(Schema):    
    titulo = String(required=True, validate=[
        validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"),
        validate_char
    ])
    nota = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres")) 
    id_tipo_nota = String(required=True)
    eliminado = Boolean(default=False)
    # id_user_creacion = String(required=True)
    id_tarea = String()


class NotaPatchIn(Schema):
    titulo = String(required=True, validate=[
        validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"),
        validate_char
    ])
    nota = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    id_tipo_nota = String()
    eliminado = Boolean()
    id_user_creacion = String(required=True)
    fecha_creacion= String(validate=validate_fecha)
    fecha_eliminacion = String(validate=validate_fecha)
    fecha_actualizacion = String(validate=validate_fecha)

    
class NotaOut(Schema):
    id = String()
    titulo = String()
    nota = String()
    id_tipo_nota = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    tipo_nota = Nested(TipoNotaOut, only=("id", "nombre")) 
    id_user_creacion = String()
    user_creacion = Nested(UsuarioOut, only=("id", "nombre", "apellido"))
    id_user_actualizacion = String()
    id_tarea = String()

class NotaAllOut(Schema):
    id = String()
    titulo = String()
    nota = String()
    id_tipo_nota = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    id_user_creacion = String()
    user_creacion = Nested(UsuarioOut, only=("id", "nombre", "apellido", "nombre_completo"))
    id_user_actualizacion = String()
    tipo_nota = Nested(TipoNotaOut, only=("id", "nombre")) 
    id_tarea = String()


class NotaIdOut(Schema):
    id = String()
    titulo = String()
    nota = String()
    id_tipo_nota = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String() 
    fecha_actualizacion = String()   
    tipo_nota = Nested(TipoNotaOut, only=("id", "nombre")) 
    id_tarea = String()
    id_user_creacion = String()
    user_creacion = Nested(UsuarioOut, only=("id", "nombre", "apellido"))
    id_user_actualizacion = String()

    
class NotaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    titulo = String(default="")
    id_tipo_nota = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_user_creacion = String()
    id_tarea = String()
    eliminado = Boolean()

class NotaCountAllOut(Schema):
    count = Integer()
    data = Nested(NotaAllOut, many=True)
    

class NotaCountOut(Schema):
    count = Integer()
    data = Nested(NotaAllOut, many=True)    

############## Labels ####################  
    
class LabelIn(Schema):    
    nombre = String(required=True, validate=[
        validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"),
        validate_char
    ])
    color = String(required=True, validate=validate.Length(min=7, max=7, error="El campo debe ser #xxxxxx")) 
    id_grupo = String(required=True)
    eliminado = Boolean()
    id_user_creacion = String(required=True)
    fecha_creacion = String(validate=validate_fecha)
    fecha_eliminacion = String(validate=validate_fecha)
    # fecha_actualizacion = String(validate=validate_fecha)
    id_tarea = String()
    #ids_labels = List(String(),required=False, many=True)


class LabelPatchIn(Schema):
    titulo = String(required=True, validate=[
        validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"),
        validate_char
    ])
    nombre = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    eliminado = Boolean()
    id_user_creacion = String(required=True)
    fecha_creacion= String(validate=validate_fecha)
    fecha_eliminacion = String(validate=validate_fecha)
    fecha_actualizacion = String(validate=validate_fecha)

    
class LabelOut(Schema):
    id = String()
    nombre = String()
    color = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    id_user_creacion = String()
    id_grupo_base = String()
    

class LabelAllOut(Schema):
    id_label = String()
    nombre = String()
    color = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    id_user_creacion = String()
    id_grupo_base = String()


class LabelIdOut(Schema):
    id = String()
    nombre = String()
    color = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    id_user_creacion = String()
    id_grupo_base = String()

    
class LabelGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_usuario_creacion = String()
    id_tarea = String()
    eliminado = Boolean()
    fecha_creacion = String()

class LabelCountAllOut(Schema):
    count = Integer()
    data = Nested(LabelAllOut, many=True)
    

class LabelCountOut(Schema):
    count = Integer()
    data = Nested(LabelOut, many=True)    


############## Labels x Tarea####################  

class LabelXTareaIn(Schema):  
    ids_labels = List(String(),required=True, many=True)
    id_tarea = String(required=True)
    # id_user_actualizacion = String(required=True)
    # fecha_actualizacion = String(validate=validate_fecha)

class LabelXTareaPatchIn(Schema):
    id_tarea = String(required=True)
    id_label = String(required=True)
    # id_user_actualizacion = String(required=True)
    # fecha_actualizacion = String(validate=validate_fecha)

class LabelXTareaInsert(Schema):
    id = String(required=True)
    # activa= Boolean()
    id_tarea = String(required=True)
    id_label = String(required=True)
    # id_user_actualizacion = String()
    # fecha_actualizacion = String(validate=validate_fecha)
    
class LabelXTareaOut(Schema):
    status = fields.String(required=True)
    message = fields.String(required=True)
    data = fields.List(fields.Nested(LabelXTareaInsert))
    # activa= Boolean()
    # id_tarea = String(required=True)
    # id_label = String(required=True)
    # id_user_actualizacion = String(required=True)
    # fecha_actualizacion = String(validate=validate_fecha)

class LabelXTareaPrueba(Schema):
    status = fields.String(required=True)
    message = fields.String(required=True)
    data = fields.List(fields.Nested(LabelXTareaInsert))



class LabelXTareaAllOut(Schema):
    id = String()
    activa= Boolean()
    id_tarea = String(required=True)
    ids_labels = List(String(),required=True, many=True)
    id_user_actualizacion = String()
    fecha_actualizacion = String(validate=validate_fecha)


class LabelXTareaIdOut(Schema):
    activa= Boolean()
    id= String(required=True)
    id_tarea = String(required=True)
    id_label = String(required=True)
    nombre = String()
    color = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String(validate=validate_fecha)

class LabelXTareaIdCountAllOut(Schema):
    count = Integer()
    data = Nested(LabelXTareaIdOut, many=True)

class LabelXTareaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_usuario_actualizacion = String()
    id_tarea = String()
    id_label = String()
    activa = Boolean()

class LabelXTareaCountAllOut(Schema):
    count = Integer()
    data = Nested(LabelXTareaAllOut, many=True)
    

class LabelXTareaCountOut(Schema):
    count = Integer()
    data = Nested(LabelXTareaOut, many=True)  

class CUInput(Schema):
    codigo = String(required=True, validate=validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"))
    descripcion = String(required=True, validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    
class CUOut(Schema):
    id = String()
    codigo = String()
    descripcion = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    

class CUCountOut(Schema):
    count = Integer()
    data = Nested(CUOut, many=True)    


class ListCU(Schema):
    codigo = String()

class EPInput(Schema):
    metodo = String(required=True, validate=validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"))
    url = String(required=True, validate=validate.Length(min=3, max=25, error="El campo debe ser mayor a 3 y menor a 25 caracteres"))
    descripcion = String(required=True, validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    caso_uso = List(Nested(ListCU))


class EPOut(Schema):
    metodo = String()
    url = String()
    descripcion = String()
    caso_uso = String()
    fecha_actualizacion = String()

class EPCountOut(Schema):
    count = Integer()
    data = Nested(EPOut, many=True)