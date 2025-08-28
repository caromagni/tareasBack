import jwt
from functools import wraps
import common.usher as usher_fnc
import common.logger_config as logger_config
from flask import request
from flask import g
import common.exceptions as exceptions
import config.config as config
import common.functions as functions
def require_role(rol=''):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            #try:
                logger_config.logger.info("CUSTOM ROLE DECORATOR")
                logger_config.logger.info("CUSTOM ROLE DECORATOR")
                x_api_key = request.headers.get('x-api-key')
                if x_api_key:
                    logger_config.logger.info("API Key detected in header")
                    # If API key is present, skip JWT verification
                    return f(*args, **kwargs)
                
                # If no API key, proceed with JWT verification
                
                rol=g.rol
                logger_config.logger.info(f"ROL: {rol}")
                auth_header = request.headers.get("Authorization", "")
                token = auth_header.replace("Bearer ", "")       
                decoded=jwt.decode(token, options={"verify_signature": False})
                metodo = request.method
                req_path = request.path
                url_cu = "/" + req_path.strip('/').split('/')[0]  # Get the first segment of the path

                logger_config.logger.info(f"metodo: {metodo}")
                logger_config.logger.info(f"url_cu: {url_cu}")
                #funcion que devuelve los casos de uso según la url del request
                use_cases = usher_fnc.get_api_cu_bd(metodo,url_cu)
                logger_config.logger.info(f"USE CASES: {use_cases}")
                logger_config.logger.info(f"FOR USER: {decoded['email']}")
                #funcion que devuelve los casos de uso según el operador
                can_pass=usher_fnc.get_usr_cu(decoded['email'], rol, use_cases)
                logger_config.logger.info(f"attempting to pass with user roles: {rol}")
                logger_config.logger.info(f"CAN PASS: {can_pass}")
                
                if(can_pass==False):
                    if (rol.lower() == 'superadmin') or (config.ALL_USERS_SUPERADMIN=="1"):
                        logger_config.logger.info(f"bypass through second if")
                        can_pass=True
                    else:
                        logger_config.logger.info(f"bypass through first if")
                        logger_config.logger.warning(f"Acceso denegado para el usuario {decoded['email']}")
                        raise exceptions.ForbiddenAccess(f"El usuario {decoded['email']} no tiene permisos para acceder a {url_cu} con método {metodo}")
                    
            
            # Si tiene permisos, continuar con la función original
                return f(*args, **kwargs)
            #except Exception as e:
            #    logger_config.logger.error(f"Error en require_role decorator: {e}")
            #    raise e    
                                               
        return wrapped
    return decorator

