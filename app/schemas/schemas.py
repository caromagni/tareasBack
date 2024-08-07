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
    first = Integer(default=1)
    rows = Integer(default=10)
###############Nomenclador####################
class NomencladorOut(Schema):
    nomenclador = String()
    desclarga = String()
    nroficin_corto = String()

###############Grupos####################
class HerarquiaGrupoGrupoOut(Schema):
    id_padre = String()
    id_hijo = String()

class GrupoHOut(Schema):
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

class GrupoIn1(Schema):
    nombre = String(required=True, validate=validate.Length(min=6, max=30))
    descripcion = String(required=True, validate=validate.Length(min=6, max=250))
    id_user_actualizacion = String(required=True)
    id_padre = String()  
    codigo_nomenclador = String(validate=validate.Length(min=6, max=6))

class GrupoIn(Schema):
    #nombre = String(required=True, validate=validate.Length(min=6, max=30))
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
    codigo_nomenclador = String(validate=[
        validate.Length(min=6, max=6, error="El campo debe ser de 6 caracteres"),
        validate_num  
    ])

class GrupoPatchIn(Schema):
    #nombre = String(required=True, validate=validate.Length(min=6, max=30))
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
    first = Integer(default=1)
    rows = Integer(default=10)
    nombre = String(default="")
    fecha_desde = String(validate=validate_fecha)
    fecha_hasta = String(validate=validate_fecha)

class GrupoOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    id_user_actualizacion = String()
    fecha_actualizacion = String()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga")) 
    eliminado = Boolean()

class UsuarioGrupoIdOut(Schema):
    id = String()
    fecha_actualizacion = DateTime()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
    nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida

class UsuarioGOut(Schema):
    id = String()
    nombre = String()
    apellido = String()

class HerarquiaGrupoOut(Schema):
    id = String()
    id_hijo = String()
    nombre_hijo = String()
    id_padre = String()
    nombre_padre = String()
    eliminado = Boolean()


class GrupoIdOut(Schema):
    id = String()
    nombre = String()
    descripcion = String()
    eliminado = Boolean()
    nomenclador = Nested(NomencladorOut, only=("nomenclador", "desclarga"))
    hijos = List(Nested(HerarquiaGrupoOut, only=("id_hijo","nombre_hijo", "eliminado")))
    padre = List(Nested(HerarquiaGrupoOut, only=("id_padre","nombre_padre", "eliminado")))
    usuarios = List(Nested(UsuarioGOut, only=("id", "nombre", "apellido")))
  

class GroupCountOut(Schema):
    count = Integer()
    data = Nested(GrupoOut, many=True)


class GruposUsuarioOut(Schema):
    id_usuario = String()
    nombre = String()
    apellido = String()
    id_grupo = String()
    nombre_grupo = String()

class UsuariosGrupoOut(Schema):
    nombre_grupo = String()
    id_usuario = String()
    nombre = String()
    apellido = String()
    
  

###############Usuarios####################
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
    id_grupo = String()

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
    id_grupo = String()

class UsuarioOut(Schema):
    id = String()
    fecha_actualizacion = DateTime()
    id_user_actualizacion = String()
    nombre = String()
    apellido = String()
    id_persona_ext = String()
    nombre_completo = String(dump_only=True)  # Indicar que es un campo solo de salida
    id_grupo = Nested(GrupoOut, only=("id", "nombre")) 
    

    @post_dump
    def add_nombre_completo(self, data, **kwargs):
        data['nombre_completo'] = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        return data
    
class TareaUsrOut(Schema):
    id = String()
    titulo = String()


class UsuarioIdOut(Schema):
    id = String()
    nombre = String()
    apellido = String()
    tareas = List(Nested(TareaUsrOut, only=("id", "titulo")))
    grupos = List(Nested(GrupoOut, only=("id", "nombre")))
    
################TipoTareas####################
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
    

###############Tareas####################  
class TareaIn(Schema):
    id_grupo = String(required=True)
    prioridad = Integer(required=True, validate=[
        validate.OneOf([1, 2, 3], error="El campo debe ser 1, 2 o 3")])
    id_actuacion = String(required=True)
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
    fecha_eliminacion = DateTime()
    id_usuario_asignado = String()   
    id_user_actualizacion = String(required=True)
    fecha_inicio = DateTime()
    fecha_fin = DateTime()
    plazo = Integer(default=0)

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
    fecha_eliminacion = DateTime()
    tipo_tarea = Nested(TipoTareaOut, only=("id", "nombre")) 
    grupo = Nested(GrupoOut, only=("id", "nombre"))
    

class TareaUsuarioOut(Schema):
    id = String()
    fecha_actualizacion = String()
    id_user_actualizacion = String()
    id_persona_ext = String()
    nombre = String()
    apellido = String()
    id_grupo = String()
    grupo = String()
        

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

    