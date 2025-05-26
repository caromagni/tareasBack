import jwt
from functools import wraps
import common.usher as usher_fnc
import common.logger_config as logger_config
from flask import request

def require_role(rol=''):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger_config.logger.info("CUSTOM ROLE DECORATOR")
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "")       
            decoded=jwt.decode(token, options={"verify_signature": False})
            metodo = request.method
            url_cu = request.path
            logger_config.logger.info(f"metodo: {metodo}")
            logger_config.logger.info(f"url_cu: {url_cu}")
            #funcion que devuelve los casos de uso según la url del request
            use_cases = usher_fnc.get_api_cu(metodo,url_cu)
            logger_config.logger.info(f"USE CASES: {use_cases}")
            #funcion que devuelve los casos de uso según el operador
            can_pass=usher_fnc.get_usr_cu(decoded['email'], rol, use_cases)
            logger_config.logger.info(f"CAN PASS: {can_pass}")
            if not can_pass:
                logger_config.logger.warning(f"Acceso denegado para el usuario {decoded['email']}")

            # Si tiene permisos, continuar con la función original
            return f(*args, **kwargs)
            # raise error-roles-no-found
        return wrapped
    return decorator