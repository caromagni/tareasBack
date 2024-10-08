from os import link
from typing_extensions import Required
from marshmallow import fields, validate, ValidationError, post_dump
from enum import Enum
#from marshmallow_sqlalchemy.fields import Nested
from apiflask import Schema
from apiflask.fields import Integer, String, DateTime, Date, Boolean, Nested, List
from apiflask.validators import Length, OneOf
#from flask_marshmallow import Marshmallow

from ..models.alch_model import TipoTarea, Tarea
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
###############Nomenclador####################
class NomencladorOut(Schema):
    nomenclador = String()
    desclarga = String()
    nroficin_corto = String()

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
    id_hijo = String()
    child_name = String()
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
    id_user_actualizacion = String(required=True)
    id_padre = String() 
    base = Boolean(default=False)
    codigo_nomenclador = String(validate=[
        validate.Length(min=6, max=6, error="El campo debe ser de 6 caracteres"),
        validate_num  
    ])

class GroupPatchIn(Schema):
    nombre= String(validate=[
        validate.Length(min=6, max=100, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    descripcion= String(validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String(required=True)
    id_padre = String()  
    codigo_nomenclador = String(validate=[
        validate.Length(min=6, max=6, error="El campo debe ser de 6 caracteres"),
        validate_num  
    ])
    suspendido = Boolean()

class GroupGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    eliminado = Boolean(default=False)
    suspendido = Boolean(default=False)
    path_name = Boolean(default=False)

class GroupOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()
    suspendido = Boolean()
    path_name = String()
    level = Integer()
    base = Boolean()

class GroupTareaOut(Schema):
    id = String()
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
    id_persona_ext = String()
    #nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida


class UsuarioGOut(Schema):
    id = String()
    nombre = String()
    apellido = String()

class HerarquiaGroupOut(Schema):
    id = String()
    id_hijo = String()
    nombre_hijo = String()
    id_padre = String()
    nombre_padre = String()
    eliminado = Boolean()


class GroupIdOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    eliminado = Boolean()
    fecha_creacion = DateTime()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga"))
    hijos = List(Nested(HerarquiaGroupOut, only=("id_hijo","nombre_hijo", "eliminado")))
    padre = List(Nested(HerarquiaGroupOut, only=("id_padre","nombre_padre", "eliminado")))
    usuarios = List(Nested(UsuarioGOut, only=("id", "nombre", "apellido")))
  


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
    

class UsuariosGroupOut(Schema):
    nombre_grupo = String()
    id_usuario = String()
    nombre = String()
    apellido = String()
    
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
    id_user_actualizacion = String(required=True)
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
    id_user_actualizacion = String(required=True)
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
    id_user_actualizacion = String(required=True)

class SubtipoTareaPatchIn(Schema):
    id_tipo = String()
    nombre = String(validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    base = Boolean(default=False)
    id_user_actualizacion = String(required=True)

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

class ListUsuario(Schema):
    id_usuario = String()

class ListGrupo(Schema):
    id_grupo = String()    
    
class TareaIn(Schema):
    prioridad = Integer(required=True, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String()
    titulo = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    cuerpo = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"))
    id_expediente = String()
    caratula_expediente = String(validate=[
        validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres"),
        validate_char
    ])
    id_tipo_tarea = String(required=True)
    id_subtipo_tarea = String()
    eliminable = Boolean()
    id_user_actualizacion = String(required=True)
    fecha_inicio = String(validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = fields.Integer(validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ))

class TareaPatchIn(Schema):
    prioridad = Integer(validate=[
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
    id_user_actualizacion = String(required=True)
    fecha_inicio = String(validate=validate_fecha)
    fecha_fin = String(validate=validate_fecha)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    estado = fields.Integer(validate=validate.OneOf(
        [estado.value for estado in EstadoEnum], 
        error="El campo debe ser 1 (pendiente), 2 (en proceso), 3 (realizada) o 4 (cancelada)"
    ))

class TareaOut(Schema):
    id = String()
    prioridad = Integer()
    estado = Integer()
    id_actuacion = String()
    titulo = String()
    cuerpo = String()
    id_expediente = String()
    caratula_expediente = String()
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
    plazo = Integer()
    fecha_creacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    reasignada_usr = Boolean(default=False)
    reasignada_grupo = Boolean(default=False)
    

    #grupo = Nested(GroupOut, only=("id", "nombre"))
  
class TareaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    titulo = String(default="")
    id_tipo_tarea = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_usuario_asignado = String()
    id_grupo = String()
    id_expediente = String()
    id_actuacion = String()
    prioridad = Integer()
    eliminado = Boolean()
    estado = Integer()
    
####################Grupos - Tareas - Usuarios ####################
class GroupAllOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
    id_user_actualizacion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    codigo_nomenclador = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    usuarios = List(Nested(UsuarioGroupIdOut))
    tareas = List(Nested(TareaOut))

class GroupCountOut(Schema):
    count = Integer()
    data = Nested(GroupOut, many=True)

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
    id_user_actualizacion = String()
    id_persona_ext = String()
    grupo = List(Nested(ListGrupo))
    dni = String(validate=[validate.Length(min=6, max=8, error="El campo documento debe tener entre 6 y 8 números") ,validate_num])
    email = String(validate=[validate.Length(min=6, max=254, error="El campo debe ser mayor a 6 y menor a 254 caracteres"), validate_email])
    username = String(validate=[validate.Length(min=4, max=15, error="El campo debe ser mayor a 4 y menor a 15 caracteres")])
 
    

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
    id_user_actualizacion = String(required=True)
    id_persona_ext = String()
    grupo = List(Nested(ListGrupo))
    dni = String(validate=[validate.Length(min=6, max=8, error="El campo documento debe tener entre 6 y 8 números") ,validate_num])
    email = String(validate=[validate.Length(min=6, max=254, error="El campo debe ser mayor a 6 y menor a 254 caracteres"), validate_email])
    username = String(validate=[validate.Length(min=4, max=15, error="El campo debe ser mayor a 4 y menor a 15 caracteres")])
 

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

class UsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
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

class UsuarioTareaOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    asignada = Boolean()
    fecha_asignacion = String()

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
    id_persona_ext = String()
    eliminado = Boolean()
    suspendido = Boolean()
    grupos = List(Nested(GroupOut), only=("id", "nombre", "codigo_nomenclador", "nomenclador", "eliminado", "suspendido"))
    tareas = List(Nested(TareaOut, only=("id", "titulo", "id_tipo_tarea", "tipo_tarea","eliminado")))
    dni = String()
    email = String()
    username = String()

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data

class UsuarioCountAllOut(Schema):
    count = Integer()
    data = Nested(UsuarioAllOut, many=True) 

class UsuarioCountOut(Schema):
    count = Integer()
    data = Nested(UsuarioOut, many=True)     


class TareaAllOut(Schema):
    id = String()
    #id_grupo = String()
    prioridad = Integer()
    estado = Integer()
    id_actuacion = String()
    titulo = String()
    cuerpo = String()
    id_expediente = String()
    caratula_expediente = String()
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
    plazo = Integer()
    fecha_creacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    subtipo_tarea = Nested(SubtipoTareaOut, only=("id", "nombre"))
    grupos = List(Nested(GroupTareaOut))
    usuarios = List(Nested(UsuarioTareaOut))

class TareaCountAllOut(Schema):
    count = Integer()
    data = Nested(TareaAllOut, many=True)

class TareaUsuarioIn(Schema):
    id_tarea = String(required=True)
    id_usuario = String(required=True)
    id_user_actualizacion = String(required=True)
    notas = String(validate=[
        validate.Length(min=4, error="El campo debe ser mayor a 4 caracteres"),
        validate_char
    ])

class TareaUsrOut(Schema):
    id = String()
    titulo = String()
    reasignada=Boolean()


class UsuarioIdOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    dni = String()
    email = String()
    username = String()
    tareas = List(Nested(TareaUsrOut, only=("id", "titulo", "reasignada")))
    grupos = List(Nested(GroupOut, only=("id", "nombre")))
    

class TipoTareaCountOut(Schema):
    count = Integer()
    data = Nested(TipoTareaOut, many=True)   

class SubtipoTareaCountOut(Schema):
    count = Integer()
    data = Nested(SubtipoTareaOut, many=True)       
   

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
    estado = String()
    


class TareaCountOut(Schema):
    count = Integer()
    data = Nested(TareaOut, many=True)      

class TareaUsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    id_persona_ext = String()
    nombre = String()
    apellido = String()
    id_grupo = String()
    grupo = String()
        
class TareaIdOut(Schema):
    id = String()
    titulo = String()
    cuerpo = String()
    id_grupo = String()
    grupo = Nested(GroupOut, only=("id", "nombre"))
    prioridad = Integer()
    estado = Integer()
    id_actuacion = String()
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
    grupos = List(Nested(GroupOut, only=("id", "nombre")))
    actuacion = Nested(ActuacionOut, only=("id", "nombre"))
    expediente = Nested(ExpedienteOut, only=("id", "caratula"))
    usuarios = List(Nested(UsuarioOut, only=("id", "nombre", "apellido")))


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
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String(required=True)
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
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    nota = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a 6 y menor a 250 caracteres")) 
    id_tipo_nota = String(required=True)
    eliminado = Boolean()
    id_user_creacion = String(required=True)
    fecha_creacion = String(validate=validate_fecha)
    id_tarea = String()
    fecha_eliminacion = String(validate=validate_fecha)
    fecha_actualizacion = String(validate=validate_fecha)


class NotaPatchIn(Schema):
    titulo = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
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

class NotaAllOut(Schema):
    id = String()
    titulo = String()
    nota = String()
    id_tipo_nota = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_actualizacion = String()
    fecha_creacion = String()
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

    
class NotaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    titulo = String(default="")
    id_tipo_nota = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_usuario_creacion = String()
    id_tarea = String()
    eliminado = Boolean()
    fecha_creacion = String()

class NotaCountAllOut(Schema):
    count = Integer()
    data = Nested(NotaAllOut, many=True)
    

class NotaCountOut(Schema):
    count = Integer()
    data = Nested(NotaOut, many=True)    

############## Labels ####################  
    
class LabelIn(Schema):    
    nombre = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
        validate_char
    ])
    color = String(validate=validate.Length(min=6, max=250, error="El campo debe ser mayor a #xxxxxx")) 
    id_grupo = String(required=True)
    eliminado = Boolean()
    id_user_creacion = String(required=True)
    fecha_creacion = String(validate=validate_fecha)
    fecha_eliminacion = String(validate=validate_fecha)
    fecha_actualizacion = String(validate=validate_fecha)


class LabelPatchIn(Schema):
    titulo = String(required=True, validate=[
        validate.Length(min=6, max=50, error="El campo debe ser mayor a 6 y menor a 50 caracteres"),
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
    id_grupo_padre = String()

class LabelAllOut(Schema):
    id = String()
    nombre = String()
    color = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    id_user_creacion = String()
    id_grupo_padre = String()


class LabelIdOut(Schema):
    id = String()
    nombre = String()
    color = String()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_creacion = String()
    fecha_actualizacion = String()
    id_user_creacion = String()
    id_grupo_padre = String()

    
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