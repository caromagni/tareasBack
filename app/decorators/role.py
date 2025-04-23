import requests
import jwt
from functools import wraps
from common.usher import get_usr_cu
from flask import request
import time
def require_role(use_cases):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            print("CUSTOM ROLE DECORATOR")
            auth_header = request.headers.get("Authorization", "")
            token = auth_header.replace("Bearer ", "")       
            decoded=jwt.decode(token, options={"verify_signature": False})
            print(decoded['email'])
            can_pass=get_usr_cu(decoded['email'],'',use_cases)
            print("CAN PASS")
            print(can_pass)
            #get_roles()
            # array=get_user_roles(username)
            # for rol in roles:
            #     for sub_rol in array
            #     if rol==
            #     return true
            return f(*args, **kwargs)
            # raise error-roles-no-found
        return wrapped
    return decorator