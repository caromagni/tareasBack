from datetime import datetime

from common.error_handling import ValidationError

from flask import request

def get_user_ip():
    try:
        if request.headers.get('X-Forwarded-For'):
            # Si la solicitud ha pasado por un proxy, esta cabecera contendrá la IP real del cliente
            ip = request.headers['X-Forwarded-For'].split(',')[0]
        else:
            # Si no hay proxy, se obtiene la IP directamente
            ip = request.remote_addr
    except RuntimeError:
        return '0.0.0.0'
            
    return ip 

def controla_fecha(fecha_in=''):
    if (fecha_in == ""):
        return None    
    else:
        try:
            fecha = datetime.strptime(fecha_in, '%d/%m/%Y').date()
            
            return fecha
        except:
            raise ValidationError("Error en el ingreso de fecha, el formato debe ser dd/mm/aaaa")
   

def formato_expte(expte):
    l = len(expte)
    if(expte.rfind('-')<0):
        nro_causa = expte
    else: 
        if(expte[2:3].isdigit()):
            #número de una letra - P-9/21
            nro_causa = expte[0:1]+expte[2:l-3].zfill(10)+expte[-2:]
        else: 
            if(expte[3:4].isdigit()):   
                #número de dos letras - HC-9/21
                nro_causa = expte[0:2]+expte[3:l-3].zfill(9)+expte[-2:]
            else:     
                #número de dos letras - R(P)-9/21
                if(expte[5:6].isdigit()):
                    nro_causa = expte[0:1]+expte[2:3]+expte[5:l-3].zfill(9)+expte[-2:]
                else: 
                    #número de tres letras - R(HC)-9/21 
                    nro_causa = expte[0:1]+expte[2:4]+expte[6:l-3].zfill(8)+expte[-2:] 
    return nro_causa  

                