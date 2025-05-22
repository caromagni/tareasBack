from common.utils import *
import json
import os
from datetime import datetime
##########################  TIPO NOTAS #############################################

def get_all_EP(username=None):
    ruta_archivo = os.path.join(current_app.config.get("JSON_CU_PATH", "."), "ep_cu.json")

    # Leemos el archivo
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        datos = []

    total = len(datos)

    # Ordenamos por 'url'
    datos.sort(key=lambda x: x.get("url", ""))

    return datos, total

def insert_EP(username, **kwargs):
    if username is not None:
        id_user_actualizacion = get_username_id(username)
    else:
        raise Exception("Usuario no ingresado")

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)

    metodo = kwargs.get('metodo', '').upper()
    url = kwargs.get('url', '').lower()
    descripcion = kwargs.get('descripcion', '')

    cu = kwargs.get("caso_uso", [])

    nuevo_registro_json = {
        "metodo": metodo,
        "url": url,
        "descripcion": descripcion,
        "caso_uso": cu
    }        
    ##########################################
    #Guardo en el archivo json
    ruta_archivo = 'ep_cu.json'
    datos = []

    # Leer archivo si existe
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []

    datos.append(nuevo_registro_json)

    # Guardar nuevamente
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    print("Datos guardados en el archivo JSON:", nuevo_registro_json)
    return nuevo_registro_json

""" def exportar_eps_a_json():
    path_archivo = "ep_cu.json"
    eps = db.session.query(EP).all()
    resultado = []

    for ep in eps:
        resultado.append({
            "url": ep.url,
            "descripcion": ep.descripcion,
            "caso_uso": [{"codigo": c} for c in ep.caso_uso]  # asumimos que es una lista de strings
        })

    with open(path_archivo, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)
    cant = len(resultado)
    return resultado, cant     """
    