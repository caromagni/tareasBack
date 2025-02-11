
from traceback import print_exception
#from fastapi import HTTPException
from apiflask   import HTTPError
import secrets
import string
import bcrypt
import json
#from utils import *
from datetime import datetime, timedelta
import base64
import os

###########   CODE TO GENERATE API KEY ###########
###   THIS CAN BE RAN IN A SEPARATE PY FILE   ###

def generate_api_key(length=32):
    # Define characters pool (letters, digits)
    characters = string.ascii_letters + string.digits
    # Generate a secure random key
    api_key = ''.join(secrets.choice(characters) for i in range(length))
    return api_key

#api_key = generate_api_key()
#print("Generated API Key:", api_key)


#PARA PONER EN USHER
#PARA PONER EN USHER#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER
# Example expiration logic
def create_api_key_with_expiration(user_id, validity_days=30):
    api_key = generate_api_key()
    expiration_date = datetime.now() + timedelta(days=validity_days)
    # Store api_key and expiration_date in the database
    # (example database insert logic)
    return api_key, expiration_date


def hash_api_key(api_key):
    # Hash the API key
    hashed_key = bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt())
    return hashed_key

#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER
#PARA PONER EN USHER

#####  END OF CODE TO GENERATE API KEY  #####




# Verify the API key later
def verify_api_key(api_key_provided=None, authorized_system=None):
    if not api_key_provided:
        raise HTTPError(status_code=200, detail=searchError('err-auth-54'))
        #raise HTTPException(status_code=200, detail=searchError('err-auth-55'))
    if not authorized_system:
        raise HTTPError(status_code=200, detail=searchError('err-auth-56'))
        #raise HTTPException(status_code=200, detail=searchError('err-auth-56'))
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
        stored_api_key = base64.b64decode(stored_hashed_api_key)
        print("will use bcrypc to check")
        return bcrypt.checkpw(api_key_provided.encode('utf-8'), stored_api_key)
    except Exception as err:
        print(err)







# def store_api_key_in_localfile(api_key, expire_date, api_key_name):
#     file_path = 'api_keys.json'
#     # must convert hashed api key to Base 64 as it is of type bytes and this would blow an atomic bomb 
#     if isinstance(api_key, bytes):
#         api_key = base64.b64encode(api_key).decode('utf-8')

#     # If the file does not exist, create it with an empty list
#     if not os.path.exists(file_path):
#         with open(file_path, 'w') as f:
#             json.dump([], f)
    
#     # Load the existing data from the file
#     with open(file_path, 'r') as f:
#         data = json.load(f)
    
#     # Append the new API key details
#     data.append({
#         'api_key': api_key,
#         'expire_date': expire_date,
#         'api_key_name': api_key_name
#     })
    
#     # Write the updated data back to the file
#     with open(file_path, 'w') as f:
#         json.dump(data, f, indent=4)
