from flask import request, current_app
from common.api_key import *
import jwt
from common.error_handling import UnauthorizedError, ValidationError
from common.logger_config import logger
import traceback


def verify_jwt_in_header():
    token_encabezado = request.headers.get('Authorization')
    jwt_pk=current_app.config['JWT_PUBLIC_KEY'] 
    jwt_alg=current_app.config['JWT_ALGORITHM']
    jwt_aud=current_app.config['JWT_DECODE_AUDIENCE']
    logger.info("Variable jwt_pk:",jwt_pk)
    logger.info("Variable jwt_alg:",jwt_alg)
    logger.info("Variable jwt_aud:",jwt_aud)

    if not token_encabezado:
        logger.error("No se proporciono token en el encabezado")
        return None
   
    
    if token_encabezado:
        try:
            print("###########Token a decodificar############")
            # Decodificar y verificar el token
            token = token_encabezado.split(' ')[1]
            print("token:",token)
            payload = jwt.decode(jwt=token, key=jwt_pk, leeway=50, algorithms=jwt_alg, audience=jwt_aud)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token expirado. Inicie sesión nuevamente.')
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError( 'Token inválido. Inicie sesión nuevamente.')
        except Exception as e:
            raise UnauthorizedError( 'Error al decodificar el token. Inicie sesión nuevamente.')

def verify_api_key_in_header(api_key_provided=None, authorized_system=None):
    if not api_key_provided:
        logger.error("No se proporciono api-key")
        return False
        #raise UnauthorizedError( 'No se proporciono api-key')
    if not authorized_system:
        logger.error("No se proporciono api-system")
        return False
        #raise UnauthorizedError( 'No se proporciono api-system')

    #find the api key in the file and compare the hash
    stored_hashed_api_key='NOT_FOUND'
    file_path = 'api_keys.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    print("DATA OF FILE")
    print(data)
    for api_key in data:
        if api_key['api_key_name'] == authorized_system:
            stored_hashed_api_key = api_key['api_key']
            print("FOUND")
            print(api_key)
            break
    
    if stored_hashed_api_key == 'NOT_FOUND':
        print("API Key not found")
        return False
    
    #convert stored_api_key to bytes
    try:
        print("will decode key from b64 to string")
        logger.info("will decode key from b64 to string")
        stored_api_key = base64.b64decode(stored_hashed_api_key)
        print("will use bcrypc to check")
        logger.info("will use bcrypc to check")
        return bcrypt.checkpw(api_key_provided.encode('utf-8'), stored_api_key)
    except Exception as err:
        logger.error(err)
        print(err)

def verify_header():
    ############### verifico si viene api key######################
    try:
        token_payload = verify_jwt_in_header()
        x_api_key = request.headers.get('x-api-key')
        x_api_system = request.headers.get('x-api-system')

        # Verificar si se proporciona el token o API key
        if token_payload is None and x_api_key is None:
            #raise UnauthorizedError("Token o api-key no validos")
            logger.info("Token o api key no validos")
            return None
       
        if token_payload is not None:            
            email=token_payload['email']
            return {"type":"JWT","user_name":email} 
       
        if x_api_key is not None:
            if x_api_system is None:
                raise UnauthorizedError("api-system no valida")
            result=verify_api_key_in_header(x_api_key, x_api_system)  
            if not result:
                raise UnauthorizedError("api-key no valida")
            else:
                return {"type":"api_key","user_name":x_api_system} 
    except Exception as err:
        logger.error(err)
        #print(traceback.format_exc())
        return None            