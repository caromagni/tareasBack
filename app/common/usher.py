import requests

def get_roles(token=''):
    url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas'
    r=requests.get(url,headers={'Authorization': 'Bearer '+token})
    resp=r.json()
    return resp