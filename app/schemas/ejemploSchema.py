from apiflask import Schema




class EjemploOut(Schema):
    #puede ser cualquier cosa, es ejemplo
    id_padre = String()
    id_hijo = String()
    nombre_padre = String()
    nombre_hijo = String()


class EjemploIn(Schema):
    #puede ser cualquier cosa, es ejemplo
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


#importar luego en controller