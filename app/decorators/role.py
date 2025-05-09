import requests
import jwt
from functools import wraps
from common.usher import get_usr_cu
from common.logger_config import logger

from flask import request
import time
def require_role(use_cases):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.info("CUSTOM ROLE DECORATOR")
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "")       
            decoded=jwt.decode(token, options={"verify_signature": False})
            can_pass=get_usr_cu(decoded['email'],'Operador',use_cases)
            logger.info("CAN PASS")
            logger.info(can_pass)
            return f(*args, **kwargs)
            # raise error-roles-no-found
        return wrapped
    return decorator