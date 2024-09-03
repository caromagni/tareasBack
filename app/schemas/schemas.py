from os import link
from typing_extensions import Required
from marshmallow import fields, validate, ValidationError, post_dump
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
    
##########Schemas para joins ###############################   
class SmartNested(Nested):
    def serialize(self, attr, obj, accessor=None):
        if attr not in obj.__dict__:
            return {"id": int(getattr(obj, attr + "_id"))}
        return super(SmartNested, self).serialize(attr, obj, accessor)

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
    eliminado = Boolean()

class GroupGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)

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

class TipoTareaOut(Schema):
    id = String()
    nombre = String()
    codigo_humano = String()
    id_user_actualizacion = String()
    eliminado = Boolean()

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
    eliminable = Boolean()
    id_user_actualizacion = String(required=True)
    plazo = Integer(default=0)
    usuario = List(Nested(ListUsuario))
    grupo = List(Nested(ListGrupo))
    

class TareaOut(Schema):
    id = String()
    id_grupo = String()
    prioridad = Integer()
    id_actuacion = String()
    titulo = String()
    cuerpo = String()
    id_expediente = String()
    caratula_expediente = String()
    id_tipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = String()
    fecha_inicio = String()
    fecha_fin = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    plazo = Integer()
    fecha_creacion = String()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    grupo = Nested(GroupOut, only=("id", "nombre"))
  
class TareaGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    titulo = String(default="")
    id_tipo_tarea = String()
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)
    id_usuario_asignado = String()
    id_expediente = String()
    
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
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 6 y menor a 30 caracteres"),
        validate_char
    ])
    apellido = String(required=True, validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 6 y menor a 30 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    id_persona_ext = String()
    grupo = List(Nested(ListGrupo))
    

class UsuarioInPatch(Schema):
    nombre = String(validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 6 y menor a 30 caracteres"),
        validate_char
    ])
    apellido = String(validate=[
        validate.Length(min=3, max=50, error="El campo debe ser mayor a 6 y menor a 30 caracteres"),
        validate_char
    ])
    id_user_actualizacion = String()
    id_persona_ext = String()
 

class UsuarioGetIn(Schema):
    page = Integer(default=1)
    per_page = Integer(default=10)
    nombre = String(default="")
    apellido = String(default="")
    id_grupo = String()
   

class UsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
    nombre_completo = String(dump_only=True)  
    eliminado = Boolean()
    suspendido = Boolean()

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


class UsuarioIdOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    eliminado = Boolean()
    suspendido = Boolean()
    tareas = List(Nested(TareaUsrOut, only=("id", "titulo")))
    grupos = List(Nested(GroupOut, only=("id", "nombre")))
    


class TipoTareaCountOut(Schema):
    count = Integer()
    data = Nested(TipoTareaOut, many=True)      

################Actuaciones####################
class TipoActuacionOut(Schema):
    id = String()
    nombre = String()

class ActuacionOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_tipo_actuacion = String()
    tipo_actuacion = Nested(TipoActuacionOut, only=("id", "nombre"))
    id_user_actualizacion = String()
    fecha_actualizacion = String()  
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
    id_actuacion = String()
    id_expediente = String()
    caratula_expediente = String()
    id_tipo_tarea = String()
    eliminable = Boolean()
    eliminado = Boolean()
    fecha_eliminacion = DateTime()
    fecha_inicio = DateTime()
    fecha_fin = DateTime()
    plazo = Integer()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
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

    