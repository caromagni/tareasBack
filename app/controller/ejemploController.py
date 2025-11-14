#functions here are inside controller folder, so they have use case logic and are not just a simple CRUD operation
#funtion to get all ejemplos for a group or a user
from models.alch_model import ActuacionExt, TipoActuacionExt
from models.ejemplo_model import get_all_ejemplo



def get_ejemplos(data):

    res = get_all_ejemplo()
    # DO STUFF WITH RES DATA, LIKE FILTERING OR SORTING OR ANY OTHER LOGIC HERE



    return res

    # THEN RETURN TO BLUEPRINT

   
