from functools import wraps
import common.logger_config as logger_config
import common.exceptions as exceptions
import common.functions as functions
import uuid

def to_uuid(val):
    """Intenta convertir un valor a UUID, si no es válido devuelve None."""
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None
    
def check_fields():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            logger_config.logger.info("CUSTOM CHECK DECORATOR")
            query_data = kwargs.get('query_data', {})
            if isinstance (query_data, dict):
                    for campo, valor in query_data.items():
                        if campo =='id' or campo.startswith('id_'):
                            # Verifica si el campo es un UUID válido
                            """ if not functions.es_uuid(valor):
                                # Intenta convertir el valor a UUID
                                raise exceptions.ValidationError(
                                    f"Decorador check - El campo '{campo}' debe ser un UUID válido: {valor}"
                                ) """

                            uuid_val = to_uuid(valor)
                            if uuid_val is None:
                                raise exceptions.ValidationError(
                                    f"El campo '{campo}' debe ser un UUID válido: {valor}"
                                )
                            query_data[campo] = uuid_val
                    kwargs['query_data'] = query_data
            return f(*args, **kwargs)
        return wrapped
    return decorator