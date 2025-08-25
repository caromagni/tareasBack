from functools import wraps
import common.logger_config as logger_config
import common.exceptions as exceptions
import common.functions as functions
import uuid
from flask import request

def to_uuid(val):
    """Intenta convertir un valor a UUID, si no es válido devuelve None."""
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None

def process_dict(diccionario, ruta=""):
    """
    Convierte en UUID todos los campos id o id_XXX si son válidos,
    incluso en estructuras anidadas, y devuelve la ruta completa del error.
    """
    
    for campo, valor in list(diccionario.items()):
        #print("Campo:", campo, "Valor:", valor, "tipo:", type(valor))
        ruta_actual = f"{ruta}.{campo}" if ruta else campo

        if campo == "id" or campo.startswith("id_"):
            uuid_convertido = to_uuid(valor)
            if uuid_convertido is None:
                return False, ruta_actual  # Error con ruta completa

        elif isinstance(valor, dict):
            #print("es un diccionario:", valor)
            ok, campo_error = process_dict(valor, ruta_actual)
            if not ok:
                return False, campo_error

        elif isinstance(valor, list):
            #print("es una lista:", valor)
            for idx, elemento in enumerate(valor):
                if isinstance(elemento, dict):
                    ok, campo_error = process_dict(elemento, f"{ruta_actual}[{idx}]")
                    if not ok:
                        return False, campo_error

    return True, None

def validar_ids_str(key, value):
    """
    Valida un valor string que puede contener uno o varios UUIDs separados por coma.
    Devuelve lista de objetos UUID si todo es válido.
    """
    #ids = [v.strip() for v in value.split(",") if v.strip()]
    ids = value.split(",")
    for i in range(len(ids)):
        ids[i] = ids[i].strip()
        if not functions.es_uuid(ids[i]):
            return False, f"{key}: {ids[i]}"
        
    return True, ids    


def check_fields():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            print("ENTRA - kwargs en decorador:", kwargs)
            
            for key, value in kwargs.items():
                print("key en kwargs:", key)
                print("value en decorador:", value)

                if isinstance(value, str):
                    #and (key == "id" or key.startswith("id_"))
                    if key == "id" or key.startswith("id_"):
                        ok, result = validar_ids_str(key, value)
                        if not ok:
                            raise exceptions.ValidationError(
                                f"El campo '{result}' no contiene un UUID válido."
                            )
                    #if key.startswith('fecha') ..... validar fecha
                       
                #controla si un campo (key) es un json con id o id_XXX
                """ elif isinstance(value, (dict, list)):
                    print("es un diccionario o lista:", value)
                    ok, campo_error = process_dict(value, key)
                    if not ok:
                        raise exceptions.ValidationError(
                            f"El campo '{campo_error}' no contiene un UUID válido."
                        )  """
            

            return f(*args, **kwargs)
        return wrapped
    return decorator    
