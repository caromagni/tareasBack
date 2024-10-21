import requests

def get_public_key(auth_url,realm):
    r=requests.get(auth_url+"/realms/"+realm)
    key=r.json()['public_key']
    return key