from flask import request, current_app
import jwt
import common.api_key as api_key
import common.error_handling as error_handling
import common.exceptions as exceptions
import common.logger_config as logger_config
import json
import base64
import bcrypt
import os

def verify_jwt_in_header():
   
    token_encabezado = request.headers.get('authorization')
    jwt_pk=current_app.config['JWT_PUBLIC_KEY'] 
    jwt_alg=current_app.config['JWT_ALGORITHM']
    jwt_aud=current_app.config['JWT_DECODE_AUDIENCE']
    #logger.info("Variable jwt_pk:",jwt_pk)
    #logger.info("Variable jwt_alg:",jwt_alg)
    #logger.info("Variable jwt_aud:",jwt_aud)

    if not token_encabezado:
        logger_config.logger.error("No se proporciono token en el encabezado")
        #raise UnauthorizedError('No se proporciono token en el encabezado')
        return None
       
    if token_encabezado:
        try:
            # Decodificar y verificar el token
            token = token_encabezado.split(' ')[1]
            print("token:",token)
            payload = jwt.decode(jwt=token, key=jwt_pk, leeway=50, algorithms=jwt_alg, audience=jwt_aud)
            print("payload:",payload)
            return payload
            
        except jwt.ExpiredSignatureError:
            raise Exception('Token expirado. Inicie sesión nuevamente.')
        except jwt.InvalidTokenError as e:
            raise Exception( 'Token inválido. Inicie sesión nuevamente.')
        except Exception as e:
            raise Exception( 'Error al decodificar el token. Inicie sesión nuevamente.')

def verify_api_key_in_header(api_key_provided=None, authorized_system=None):
    if not api_key_provided:
        logger_config.logger.error("No se proporciono api-key")
        #return False
        raise Exception( 'No se proporciono api-key')
    if not authorized_system:
        logger_config.logger.error("No se proporciono api-system")
        #return False
        raise Exception( 'No se proporciono api-system')

    #find the api key in the file and compare the hash
    stored_hashed_api_key='NOT_FOUND'
    file_path = './json/api_keys.json'
    if not os.path.exists(file_path):
        logger_config.logger.error(f"El archivo {file_path} no existe.")
        raise Exception(f"El archivo {file_path} no existe.")
    with open(file_path, 'r') as f:
        data = json.load(f)
    for api_key in data:
        if api_key['api_key_name'] == authorized_system:
            stored_hashed_api_key = api_key['api_key']
            print("FOUND")
            print(api_key)
            break
    
    if stored_hashed_api_key == 'NOT_FOUND':
        logger_config.logger.error("API Key not found")
        return False
    
    #convert stored_api_key to bytes
    try:
        logger_config.logger.info("will decode key from b64 to string")
        stored_api_key = base64.b64decode(stored_hashed_api_key)
        logger_config.logger.info("will use bcrypc to check")
        return bcrypt.checkpw(api_key_provided.encode('utf-8'), stored_api_key)
    except Exception as err:
        logger_config.logger.error(err)
        raise Exception(err)

def verify_header():
    ############### verifico si viene api key######################
    try:
        print("verifiy headers function in auth") 
        if request.method == 'OPTIONS':
            print("OPTIONS!!!!!!! ")
          
        else:
            token_payload = verify_jwt_in_header()
            x_api_key = request.headers.get('x-api-key')
            x_api_system = request.headers.get('x-api-system')
            x_user_rol = request.headers.get('x-user-role')
            #id Fuero de Paz de la tabla dominio
            x_dominio = '06737c52-5132-41bb-bf82-98af37a9ed80'
            #id Juzgado de Paz de Lavalle de la tabla organismo
            x_organismo = 'cb08f738-7590-4331-871e-26f0f09ff4ca'
            print("x_api_key:",x_api_key)
            print("x_api_system:",x_api_system)
            print("x_user_rol:",x_user_rol)
            # Verificar si se proporciona el token o API key
            if token_payload is None and x_api_key is None:
                logger_config.logger.info("Token o api key no validos")
                raise Exception("Token o api-key no validos")
        
            if token_payload is not None:    
                logger_config.logger.info("Token valido")        
                email=token_payload['email']
                return {"type":"JWT","user_name":email,"user_rol":x_user_rol, "dominio":x_dominio, "organismo":x_organismo} 
        
            if x_api_key is not None:
                if x_api_system is None:
                    #raise exceptions.UnauthorizedError("api-system no valida")
                    raise Exception("UnauthorizedError('api-system no valida')")
                
                result=verify_api_key_in_header(x_api_key, x_api_system)  
                if not result:
                    raise Exception("api-key no valida")
                else:
                    logger_config.logger.info(f"API Key valido: {x_api_key} - x_api_system: {x_api_system}")
                    return {"type":"api_key","user_name":x_api_system, "user_rol":x_user_rol, "dominio":x_dominio, "organismo":x_organismo} 
            
    except Exception as err:
        logger_config.logger.info("Error en la verificacion de header")
        logger_config.logger.error(err)
        raise Exception(err)
        