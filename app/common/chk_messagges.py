from time import sleep
import uwsgi
#from app.common.rabbitmq_utils import RabbitMQHandler
from common.rabbitmq_utils import RabbitMQHandler
    
# Consumir mensajes de la cola

def chk_messagges(app):
    tiempo=10
    handler = RabbitMQHandler()
    handler.connect()
    #if uwsgi.worker_id() == 1:
    #if uwsgi.worker_id() == 1:
    while True:
        print("handler.channel: ", handler.channel)
        if handler.channel:
            with app.app_context():
                print("---- RUNNING CHECK MESSAGES ----")
                try:
                    handler.start_consuming()
                    sleep(tiempo)
                except Exception as e:
                    print("Error en chk_messagges:", e)
                    sleep(tiempo)
                
    """         if handler.channel:
                with app.app_context():
                    print("---- RUNNING CHECK MESSAGES ----")
                    try:
                        handler.start_consuming()
                        sleep(tiempo)
                    except Exception as e:
                        print("Error en chk_messagges:", e)
                        sleep(tiempo) """
                       
            
      

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
    