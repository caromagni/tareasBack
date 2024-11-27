from time import sleep
import uwsgi
from common.rabbitmq_utils import *
    
# Consumir mensajes de la cola
def chk_messagges():
    tiempo=30
    if uwsgi.worker_id() == 1:
             recibir_de_rabbitmq()   
             sleep(tiempo)  
      

""" def chequea_txid(app=''):
    tiempo=int(app.config["SLEEP"])
    if uwsgi.worker_id() == 1:
        while True:
            print("---- RUNING CHECK TXID ----")
            url=app.config["URL_SCAPI"]
            pending_count = Evidencia.objects(tx__txstatus='pending').count()
            if pending_count > 0:
                # Si hay documentos pendientes, recupera la colección y la recorre
                pending = Evidencia.objects(tx__txstatus='pending').all()  
                for registro in pending:
                    txid=registro['tx']['txid']
                    url_get=url+'/api/v1/tx/'
                    response=requests.get(url_get+str(txid))
                    txstatus=response.json()['success']
                    if(txstatus):
                        txdate=response.json()['data']['timestamp']
                        print("Chequendo TX en blockchain - txid: ",registro['tx']['txid']," --> ",txstatus)
                        print ("Fecha transaccion:",txdate)
                        Evidencia.objects(tx__txid=txid).update(creado=txdate, tx__txstatus='success') 
                        print("---- txstatus UPDATED ----") 
            sleep(tiempo) """
    