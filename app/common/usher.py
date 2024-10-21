import requests

def get_roles(token=''):
    print('get_roles')
    url='http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas'
    r=requests.get(url,headers={'Authorization': 'Bearer '+token})
    resp=r.json()
    print("json roles:",resp)
    return resp