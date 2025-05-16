import requests
import jwt
from functools import wraps
import common.usher as usher_fnc
from common.usher import get_usr_cu
from common.logger_config import logger

from flask import request
import time
def require_role(operador=''):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.info("CUSTOM ROLE DECORATOR")
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "")       
            decoded=jwt.decode(token, options={"verify_signature": False})
            url_cu = request.method.lower() + request.path
            logger.info("url_cu")
            logger.info(url_cu)
            #funcion que devuelve los casos de uso según la url del request
            use_cases = usher_fnc.get_api_cu(url_cu)
            logger.info("use_cases")
            logger.info(use_cases)
            #funcion que devuelve los casos de uso según el operador
            can_pass=usher_fnc.get_usr_cu(decoded['email'], operador, use_cases)
            logger.info("CAN PASS")
            logger.info(can_pass)
            return f(*args, **kwargs)
            # raise error-roles-no-found
        return wrapped
    return decorator