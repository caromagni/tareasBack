from flask import request, current_app
from ..api_key import *
import jwt
from .error_handling import UnauthorizedError, ValidationError

def verify_token():
    token_encabezado = request.headers.get('Authorization')
    jwt_pk=current_app.config['JWT_PUBLIC_KEY'] 
    jwt_alg=current_app.config['JWT_ALGORITHM']
    jwt_aud=current_app.config['JWT_DECODE_AUDIENCE']

    if not token_encabezado:
        return None
    
    if token_encabezado:
        try:
            # Decodificar y verificar el token
            token = token_encabezado.split(' ')[1]
            print("token:",token)
            payload = jwt.decode(jwt=token, key=jwt_pk, algorithms=jwt_alg, audience=jwt_aud)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token expirado. Inicie sesión nuevamente.')
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError( 'Token inválido. Inicie sesión nuevamente.')
        except Exception as e:
            raise UnauthorizedError( 'Error al decodificar el token. Inicie sesión nuevamente.')

    
def verificar_header():
    ############### verifico si viene api key######################
        token_payload = verify_token()
        x_api_key = request.headers.get('x-api-key')
        x_api_system = request.headers.get('x-api-system')
        print("x_api_system:",x_api_system)
        print("x_api_key:",x_api_key)
        # Verificar si se proporciona el token o API key
        if token_payload is None and x_api_key is None:
            #raise UnauthorizedError("Token o api-key no validos")
            print("Token o api key no validos")
       
        if token_payload is not None:            
            nombre_usuario=token_payload['preferred_username']
            print("###########Token valido############")
            print("nombre_usuario:",nombre_usuario)
            return True
       
        if x_api_key is not None:
            if x_api_system is None:
                raise UnauthorizedError("api-system no valida")
            if not verify_api_key(x_api_key, x_api_system):
                raise UnauthorizedError("api-key no valida")
            else:
                return True    