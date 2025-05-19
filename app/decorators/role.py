import requests
import jwt
from functools import wraps
import common.usher as usher_fnc
import common.epcache as epcache
from common.usher import get_usr_cu
from common.logger_config import logger

from flask import request
import time
def require_role(rol=''):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.info("CUSTOM ROLE DECORATOR")
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "")       
            decoded=jwt.decode(token, options={"verify_signature": False})
            url_cu = request.method.lower() + request.path
            logger.info(f"url_cu: {url_cu}")
            #funcion que devuelve los casos de uso según la url del request
            #use_cases = usher_fnc.get_api_cu(url_cu)
            use_cases = epcache.EPCache().get_api_cu(url_cu)
            #funcion que devuelve los casos de uso según el operador
            can_pass=usher_fnc.get_usr_cu(decoded['email'], rol, use_cases)
            logger.info(f"CAN PASS: {can_pass}")
            if not can_pass:
                # ❌ Si no tiene permisos, devolver 403
                logger.warning(f"Acceso denegado para el usuario {decoded['email']}")
                """ return jsonify({
                    "code": 403,
                    "error": "Forbidden",
                    "error_description": "No tiene permisos para acceder a este recurso"
                }), 403 """

            # Si tiene permisos, continuar con la función original
            return f(*args, **kwargs)
            # raise error-roles-no-found
        return wrapped
    return decorator