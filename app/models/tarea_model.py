import uuid
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import scoped_session
from datetime import datetime, timedelta
from common.functions import controla_fecha
from sqlalchemy import desc
from flask import current_app
import traceback
from models.alch_model import Tarea, TipoTarea, Label, LabelXTarea, Usuario, Nota, TareaAsignadaUsuario, Grupo, TareaXGrupo, UsuarioGrupo, Inhabilidad, SubtipoTarea, ExpedienteExt, ActuacionExt
from models.alch_model import Auditoria_TareaAsignadaUsuario 
from common.utils import *
from common.logger_config import logger
from alchemy_db import db
from sqlalchemy import func, cast, Text
from sqlalchemy.types import Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from cache import cache
def nombre_estado(estado):
    if estado == 1:
        return "Pendiente"
    if estado == 2:
        return "En proceso"
    if estado == 3:
        return "Finalizada"
    if estado == 4:
        return "Cancelada"

def nombre_prioridad(prioridad):
    if prioridad == 1:
        return "Alta"
    if prioridad == 2:
        return "Media"
    if prioridad == 3:
        return "Baja"

def es_habil(fecha):
    """ if fecha.weekday() >= 5:
        return True  """ 
    return fecha.weekday() < 5  
    
def calcular_fecha_vencimiento(fecha, plazo):
    logger.info("calcula fecha vencimiento:" + str(fecha) + "-" + str(plazo))
    #fecha_vencimiento = datetime.strptime(fecha, '%d/%m/%Y')
    fecha_vencimiento=fecha
    dias_agregados = 0
    while dias_agregados < plazo:
        fecha_vencimiento = fecha_vencimiento + timedelta(days=1)
        if es_habil(fecha_vencimiento):
            dias_agregados = dias_agregados + 1

    return fecha_vencimiento

def calcular_dias_vencimiento(fecha_vencimiento):
    """Calcula los días hábiles restantes hasta la fecha de vencimiento"""
    fecha_actual = datetime.now().date()  # Tomar solo la fecha, sin hora
    fecha_vencimiento = fecha_vencimiento.date()  # Asegurar que es solo fecha
    
    dias_vencimiento = 0
    fecha_intermedia = fecha_actual
    
    while fecha_intermedia < fecha_vencimiento:
        if es_habil(fecha_intermedia):
            dias_vencimiento += 1
        fecha_intermedia += timedelta(days=1)  # Pasar al siguiente día
    
    logger.info("dias_vencimiento:" + str(dias_vencimiento) + "-" + str(fecha_vencimiento))
    return dias_vencimiento

def tareas_a_vencer(username=None, dias_aviso=None):
    total = 0
    if username is not None:
        id_user = verifica_username(username)

        if id_user is not None:
            verifica_usr_id(id_user)
        else:
            raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if dias_aviso is None:
        dias_aviso = 365  # Por defecto, 365 días de aviso

    logger.info("tareas_a_vencer")
    #Busco las tareas asignadas a todos los grupos del usuario username
    tareas = (db.session.query(Tarea)
              .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
              .join(Grupo, TareaXGrupo.id_grupo == Grupo.id)
              .join(UsuarioGrupo, Grupo.id == UsuarioGrupo.id_grupo)
              .filter(Tarea.fecha_fin >= datetime.now(),  # Solo tareas activas
                      Tarea.eliminado == False,
                      Tarea.estado != 3,
                      UsuarioGrupo.id_usuario==id_user,
                      UsuarioGrupo.eliminado==False)  # Estado activo
              .all())
    if tareas is not None:
        total = len(tareas)
        logger.info("Cantidad de tareas_a_vencer:" + str(total))    

    logger.info("Cantidad de tareas_a_vencer:" + str(total))
    tareas_vencer = [tarea for tarea in tareas if calcular_dias_vencimiento(tarea.fecha_fin) <= dias_aviso]
    total = len(tareas_vencer)
    return tareas_vencer, total


def insert_tarea(usr_header=None, id_grupo=None, prioridad=0, estado=1, id_actuacion=None, titulo='', cuerpo='', id_expediente=None, caratula_expediente='', nro_expte='', nombre_actuacion='', id_tipo_tarea=None, id_subtipo_tarea=None, eliminable=False, fecha_eliminacion=None, id_user_actualizacion=None, fecha_inicio=None, fecha_fin=None, plazo=0, usuario=None, grupo=None, username=None):
    
    print("##############Validaciones Insert Tarea################")
    id_grupo=None
    id_usuario_asignado=None
    #if type_header is not "api_key":
    if usr_header is not None:
        print("usr_header:", usr_header)
        print("verifying token username")
        id_user_actualizacion = verifica_username(usr_header)
    else:
        #raise Exception("Error en el ingreso de Usuario. Usuario no existente")
    
        if username is not None:
            #print("verifying username: " + username)
            logger.info("verifying username: " + username)
            id_user_actualizacion = verifica_username(username)
        else:
            logger.error("Error en el ingreso de Usuario. Usuario no existente")
            raise Exception("Error en el ingreso de Usuario. Usuario no existente")  
          

    if id_expediente is not None:
        print("#"*50)
        print("id_expediente:", id_expediente)
        print("#"*50)
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == id_expediente).first()

        if expediente is None:
            #Cuando viene del portal o de expedientes, se ingresa el id_ext
            logger.info("Expediente no encontrado - Busca id_ext")
            expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id_ext == id_expediente).first()
            if expediente is None:
                logger.info("Expediente no encontrado - Inserta expediente")
                nuevoID_expte=uuid.uuid4()
                insert_expte = ExpedienteExt(id=nuevoID_expte, 
                                            id_ext=id_expediente, 
                                            caratula=caratula_expediente,
                                            nro_expte=nro_expte,
                                            fecha_actualizacion=datetime.now(),
                                            id_user_actualizacion=id_user_actualizacion)
                db.session.add(insert_expte)
                id_expediente = nuevoID_expte
            else:
                logger.info("Expediente encontrado - Update del expediente")
                #id_expediente = expediente.id
                if caratula_expediente is not None and caratula_expediente.strip() != "":
                    logger.info("Modifica caratula_expediente:" + caratula_expediente)
                    expediente.caratula = caratula_expediente
                if nro_expte is not None and nro_expte.strip() != "":    
                    logger.info("Modifica nro_expte:" + nro_expte)
                    expediente.nro_expte=nro_expte
                expediente.fecha_actualizacion = datetime.now()
                id_expediente = expediente.id

    if id_actuacion is not None:
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == id_actuacion).first()
        
        if actuacion is None:
            actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id_ext == id_actuacion).first()
            if actuacion is None:
                logger.info("Actuacion no encontrada - Inserta actuacion")
                nuevoID_actuacion=uuid.uuid4()
                insert_actuacion = ActuacionExt(id=nuevoID_actuacion,
                                                id_ext=id_actuacion,
                                                nombre=nombre_actuacion,
                                                id_tipo_actuacion=id_tipo_tarea,
                                                id_user_actualizacion=id_user_actualizacion,
                                                fecha_actualizacion=datetime.now())
                db.session.add(insert_actuacion)
                id_actuacion = nuevoID_actuacion
                logger.info("actuacion insertada")
            else:
                #actuacion.id_actuacion = actuacion.id
                logger.info("Actuacion encontrada - Update de actuacion")
                if nombre_actuacion is not None and nombre_actuacion.strip() != "":
                    actuacion.nombre = nombre_actuacion
                    actuacion.id_user_actualizacion = id_user_actualizacion
                    actuacion.fecha_actualizacion = datetime.now()
                id_actuacion = actuacion.id
            
    if id_tipo_tarea is not None:
        tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea, TipoTarea.eliminado==False).first()
        if tipo_tarea is None:
            logger.error("Tipo de tarea no encontrado")
            raise Exception("Tipo de tarea no encontrado")
        nombre_tipo=tipo_tarea.nombre
        if id_subtipo_tarea is not None:
            subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.eliminado==False).first()
            if subtipo_tarea is None:
                logger.error("Subtipo de tarea no encontrado")
                raise Exception("Subtipo de tarea no encontrado")
            nombre_subtipo = subtipo_tarea.nombre
            subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.id_tipo == id_tipo_tarea).first()
            if subtipo_tarea is None:
                logger.error("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
    else:
        if id_subtipo_tarea is not None:
            logger.error("Debe ingresar el tipo de tarea")
            raise Exception("Debe ingresar el tipo de tarea")
            



#   /$$$$$$  /$$$$$$ /$$    /$$    /$$ /$$$$$$  /$$$$$$ 
#  /$$__  $$|_  $$_/| $$   | $$   | $$|_  $$_/ /$$__  $$
# | $$  \__/  | $$  | $$   | $$   | $$  | $$  | $$  \ $$
# |  $$$$$$   | $$  | $$   |  $$ / $$/  | $$  | $$$$$$$$
#  \____  $$  | $$  | $$    \  $$ $$/   | $$  | $$__  $$
#  /$$  \ $$  | $$  | $$     \  $$$/    | $$  | $$  | $$
# |  $$$$$$/ /$$$$$$| $$$$$$$$\  $/    /$$$$$$| $$  | $$
#  \______/ |______/|________/ \_/    |______/|__/  |__/

#we need to review this, as the calcular_fecha_vencimiento will modify the original fecha fin date.
#we need to check if the fecha_fin is not None, and if it is, we need to calculate the fecha_fin
#else, the fecha fin in must always match the fecha_inicio + plazo or it will be inconsistent

    ####################Calculo de plazo##################
    con_plazo=False
    if fecha_inicio is None:
        fecha_inicio = datetime.now().date()
        

   #format date from DD/MM/YYYY to DD-MM-YYYY
    fecha_inicio = controla_fecha(fecha_inicio)

    #print("after format")
    #print(fecha_inicio)
    
    if plazo>0:
        query_inhabilidad = db.session.query(Inhabilidad).all()
        if len(query_inhabilidad)>0:  
            #fecha_inicio = fecha_inicio + " 23:59:59"     
            query_inhabilidad = db.session.query(Inhabilidad).filter(Inhabilidad.fecha_desde <= fecha_inicio, Inhabilidad.fecha_hasta >= fecha_inicio).all()
            if query_inhabilidad is not None:
                for row in query_inhabilidad:
                    plazo=plazo+1
        print("calcular fecha")
        fecha_fin = calcular_fecha_vencimiento(fecha_inicio, plazo)
   
    tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea).first()
    if tipo_tarea is None:
       msg = "Tipo de tarea no encontrado"
       return None, msg
    print("DATES FORMATS TO BE INSERTED")
    print("fecha_inicio:", fecha_inicio)
    print("fecha_fin:", fecha_fin)
    print("fecha_creacion:", datetime.now())
    nuevoID_tarea=uuid.uuid4()
    print("DATE DEBUG")
    print("datetime.now():", datetime.now())
    print("fecha_inicio:", fecha_inicio)
    print("fecha_fin:", fecha_fin)
    nueva_tarea = Tarea(
        id=nuevoID_tarea,
        prioridad=prioridad,
        estado=estado,
        id_actuacion=id_actuacion,
        titulo=titulo,
        cuerpo=cuerpo,
        id_expediente=id_expediente,
        #caratula_expediente=caratula_expediente,
        id_tipo_tarea=id_tipo_tarea,
        id_subtipo_tarea=id_subtipo_tarea,
        eliminable=eliminable,
        id_user_actualizacion=id_user_actualizacion,
        fecha_eliminacion=fecha_eliminacion,
        fecha_actualizacion=datetime.now(),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fecha_creacion=datetime.now(),
        plazo=plazo
    )

    db.session.add(nueva_tarea) 

    if grupo is not None:
        for group in grupo:
            id_grupo=group['id_grupo']
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == id_grupo, Grupo.eliminado==False).first()
            if existe_grupo is None:
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))
            
            if existe_grupo.suspendido==True:
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            id_usuario_asignado = existe_grupo.id_user_asignado_default
            
            nuevoID_tareaxgrupo=uuid.uuid4()
            tareaxgrupo= TareaXGrupo(
                id=nuevoID_tareaxgrupo,
                id_grupo=id_grupo,
                id_tarea=nuevoID_tarea,
                id_user_actualizacion=id_user_actualizacion,
                fecha_asignacion=datetime.now(),
                fecha_actualizacion=datetime.now()
            ) 
            db.session.add(tareaxgrupo) 

    else:
        logger.error("Debe ingresar al menos un grupo")
        raise Exception ("Debe ingresar al menos un grupo")
        
    #Asigna el grupo del usuario que crea la tarea por defecto
    
        """ if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
            id_grupo, id_usuario_asignado = verifica_grupo_id(id_user_actualizacion)
            #usr_grupo = verifica_grupo_id(id_user_actualizacion)
        else:
            raise Exception("Debe ingresar username o id_user_actualizacion") 


            if id_grupo is not None:
                existe_grupo = db.session.query(Grupo).filter(Grupo.id == id_grupo, Grupo.eliminado==False, Grupo.suspendido==False).first()
                if existe_grupo is not None:
                    nuevoID_tareaxgrupo=uuid.uuid4()
                    tareaxgrupo= TareaXGrupo(
                        id=nuevoID_tareaxgrupo,
                        id_grupo=id_grupo,
                        id_tarea=nuevoID_tarea,
                        id_user_actualizacion=id_user_actualizacion,
                        fecha_asignacion=datetime.now(),
                        fecha_actualizacion=datetime.now()
                    )
                    db.session.add(tareaxgrupo) """

                           

    if usuario is not None:
        for user in usuario:
            id_usuario = user['id_usuario']
            existe_usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario, Usuario.eliminado==False).first()
            if existe_usuario is None:
                logger.error("Error en el ingreso de Usuario. Usuario no existente")
                raise Exception("Error en el ingreso de Usuario. Usuario no existente")
            
            if existe_usuario.eliminado==True:
                logger.error("Error en el ingreso de Usuario. Usuario eliminado")
                raise Exception("Error en el ingreso de Usuarios. Usuario eliminado: " + existe_usuario.apelllido + '- id: ' + str(existe_usuario.id))

            if existe_usuario is not None:
                nuevoID=uuid.uuid4()
                asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=nuevoID_tarea,
                    id_usuario=user['id_usuario'],
                    id_user_actualizacion=id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now()
                )
                db.session.add(asigna_usuario)
    
    if id_usuario_asignado is not None:
        existe_usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario_asignado, Usuario.eliminado==False).first()
        if existe_usuario is not None:
            nuevoID=uuid.uuid4()
            asigna_usuario = TareaAsignadaUsuario(
                id=nuevoID,
                id_tarea=nuevoID_tarea,
                id_usuario=id_usuario_asignado,
                id_user_actualizacion=id_user_actualizacion,
                fecha_asignacion=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
            db.session.add(asigna_usuario)

           
       
    db.session.commit()
    return nueva_tarea

def update_tarea(id_tarea='', username=None, **kwargs):
    ################################
    controla_tipo=False
    id_grupo=None
    id_usuario_asignado=None
    
    print("update_tarea")
    tarea = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()

    if username is not None:
        id_user_actualizacion = verifica_username(username)

        if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")

    print("id_user_actualizacion:", id_user_actualizacion)        
    
    if tarea is None:
        return None
    
    #if 'caratula_expediente' in kwargs:
        #tarea.caratula_expediente = kwargs['caratula_expediente'].upper()
    if 'cuerpo' in kwargs:
        tarea.cuerpo = kwargs['cuerpo']
    if 'eliminable' in kwargs:
        tarea.eliminable = kwargs['eliminable']
    if 'id_actuacion' in kwargs:
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == kwargs['id_actuacion']).first()
        if actuacion is None:
            raise Exception("Actuacion no encontrada")
        tarea.id_actuacion = kwargs['id_actuacion']
    if 'id_expediente' in kwargs:
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == kwargs['id_expediente']).first()
        if expediente is None:
            raise Exception("Expediente no encontrado")
        tarea.id_expediente = kwargs['id_expediente']    
    #Validacion de tipo y subtipo de tarea
    if 'id_tipo_tarea' in kwargs:
        tipo = db.session.query(TipoTarea).filter(TipoTarea.id == kwargs['id_tipo_tarea'], TipoTarea.eliminado==False).first()
        if tipo is  None:
            raise Exception("Tipo de tarea no encontrado:" + kwargs['id_tipo_tarea'])
        
        nombre_tipo=tipo.nombre
        if 'id_subtipo_tarea' in kwargs:
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            nombre_subtipo = subtipo.nombre
            #print("nombre_subtipo:",nombre_subtipo)
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.id_tipo == kwargs['id_tipo_tarea']).first()
            if subtipo is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
           
            tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
            tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']
        #no se ingreso subtipo de tarea, verifico con el subtipo actual
        else:
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == tarea.id_subtipo_tarea, SubtipoTarea.id_tipo==kwargs['id_tipo_tarea']).first()
            if subtipo is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' no se corresponde al subtipo de tarea actual")

            tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
    else:
        #no se ingreso tipo de tarea , verifico con el tipo actual         
        if 'id_subtipo_tarea' in kwargs:
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            #verifico que el subtipo de tarea corresponda al tipo de tarea actual
            nombre_subtipo = subtipo.nombre
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs["id_subtipo_tarea"], SubtipoTarea.id_tipo==tarea.id_tipo_tarea).first()
            if subtipo is None:
                raise Exception("El tipo de tarea actual no se corresponde con el subtipo ingresado: '" + nombre_subtipo )
            tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']

    if 'plazo' in kwargs:
        tarea.plazo = kwargs['plazo']
    if 'prioridad' in kwargs:
        tarea.prioridad = kwargs['prioridad']
    if 'estado' in kwargs:
        tarea.estado = kwargs['estado']    
    if 'titulo' in kwargs:
        tarea.titulo = kwargs['titulo'].upper() 
    if 'fecha_inicio' in kwargs:
        fecha_inicio = datetime.strptime(kwargs['fecha_inicio'], "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        tarea.fecha_inicio = fecha_inicio
    if 'fecha_fin' in kwargs:
        fecha_fin = datetime.strptime(kwargs['fecha_fin'], "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        tarea.fecha_fin = fecha_fin        
    
                
    tarea.id_user_actualizacion = id_user_actualizacion  
    tarea.fecha_actualizacion = datetime.now()
    usuarios=[]
    grupos=[]
    if 'grupo' in kwargs:
        print("Grupos:", kwargs['grupo'])
        #elimino los grupos existentes para esa tarea 
        grupo_tarea=db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_tarea)

        for grupo in grupo_tarea:
            print("Encuentra grupo y lo borra:", grupo.id_grupo)
            grupo.eliminado=True
            grupo.fecha_actualizacion=datetime.now()
            grupo.id_user_actualizacion=id_user_actualizacion

        #controlo que el grupo exista y lo asocio a la tarea
        for group in kwargs['grupo']:
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                print("Grupo no encontrado")
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                print("Grupo eliminado")
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            if existe_grupo.suspendido==True:
                print("Grupo suspendido")
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            nuevoID=uuid.uuid4()
            tareaxgrupo = db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_tarea, TareaXGrupo.id_grupo==group['id_grupo']).first()
            if tareaxgrupo is None:
                nuevo_tarea_grupo = TareaXGrupo(
                    id=nuevoID,
                    id_grupo=group['id_grupo'],
                    id_tarea=id_tarea,
                    id_user_actualizacion= id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now()
                )
                
                db.session.add(nuevo_tarea_grupo)
            else:
                print("Reactiva grupo")
                if tareaxgrupo.eliminado==True:
                    tareaxgrupo.eliminado=False
                    tareaxgrupo.fecha_actualizacion=datetime.now()
                    tareaxgrupo.fecha_actualizacion=datetime.now()
                    tareaxgrupo.id_user_actualizacion=id_user_actualizacion   

            grupo = {
                "id_grupo": existe_grupo.id,
                "nombre": existe_grupo.nombre,
                "asignado": 'True',
                "fecha_asisgnacion": datetime.now()
            }
            grupos.append(grupo)

    print("Grupos asignados a la tarea:", grupos)

    if 'usuario' in kwargs:
        #elimino los usuarios existentes para esa tarea
        usuarios_tarea=db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_tarea)
        if usuarios_tarea:
            for usuario in usuarios_tarea:
                usuario.eliminado=True
                usuario.fecha_actualizacion=datetime.now()

        #controlo que el usuario exista y lo asocio a la tarea
        for user in kwargs['usuario']:
            existe_usuario = db.session.query(Usuario).filter(Usuario.id == user['id_usuario']).first()
            if existe_usuario is None:
                raise Exception("Error en el ingreso de usuarios. Usuario no existente")
            
            if existe_usuario.eliminado==True:
                raise Exception("Error en el ingreso de usuarios. Usuario eliminado: " + existe_usuario.apellido + ' - id: ' + str(existe_usuario.id))

            nuevoID=uuid.uuid4()
            asigna_usuario = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_tarea, TareaAsignadaUsuario.id_usuario==user['id_usuario']).first()
            if asigna_usuario is None:
                nuevo_asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=id_tarea,
                    id_usuario=user['id_usuario'],
                    id_user_actualizacion= id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now()
                )
                db.session.add(nuevo_asigna_usuario)
            else:
                #si el usuario ya tuvo la tarea reasigno el usuario
                if asigna_usuario.eliminado==True:
                    asigna_usuario.eliminado=False
                    asigna_usuario.fecha_actualizacion=datetime.now()
                    asigna_usuario.fecha_actualizacion=datetime.now()
                    asigna_usuario.id_user_actualizacion=id_user_actualizacion

            usuario = {
                "id_usuario": existe_usuario.id,
                "nombre": existe_usuario.nombre,
                "apellido": existe_usuario.apellido,
                "asignado": 'True',
                "fecha_asignacion": datetime.now()
            }
            usuarios.append(usuario)
    """ else:
        #Asigna el usuario que crea la tarea por defecto
        if id_usuario_asignado is not None:
            existe_usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario_asignado, Usuario.eliminado==False).first()
            if existe_usuario is not None:
                nuevoID=uuid.uuid4()
                asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=id,
                    id_usuario=id_usuario_asignado,
                    id_user_actualizacion= id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now()
                )
                db.session.add(asigna_usuario) 
                
                usuario = {
                "id": existe_usuario.id,
                "nombre": existe_usuario.nombre,
                "apellido": existe_usuario.apellido,
                "asignado": 'True',
                "fecha_asignacion": datetime.now()
                }
                usuarios.append(usuario)  """
    print ("Arma el resultado")
    ###################Formatear el resultado####################
    result = {
        "id": tarea.id,
        "titulo": tarea.titulo,
        "fecha_inicio": tarea.fecha_inicio,
        "fecha_fin": tarea.fecha_fin,
        "plazo": tarea.plazo,
        "prioridad": tarea.prioridad,
        "id_tipo_tarea": tarea.id_tipo_tarea,
        "id_subtipo_tarea": tarea.id_subtipo_tarea,
        "tipo_tarea": tarea.tipo_tarea,
        "subtipo_tarea": tarea.subtipo_tarea,
        "id_expediente": tarea.id_expediente,
        "expediente": tarea.expediente,
       #"caratula_expediente": tarea.caratula_expediente,
        "id_actuacion": tarea.id_actuacion,
        "actuacion": tarea.actuacion,
        "cuerpo": tarea.cuerpo,
        "eliminable": tarea.eliminable,
        "eliminado": tarea.eliminado,
        "fecha_eliminacion": tarea.fecha_eliminacion,
        "fecha_actualizacion": tarea.fecha_actualizacion,
        "fecha_creacion": tarea.fecha_creacion,
        "id_grupo": tarea.id_grupo,
        "grupo": grupos,
        "usuario": usuarios
    }

    db.session.commit()
    return result

def update_lote_tareas_v2(username=None, **kwargs):
    print("update_tarea_V2 --")
    print(kwargs)
    print("#"*50)

    if username is not None:
        id_user_actualizacion = verifica_username(username)
        if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if 'upd_tarea' in kwargs:
        upd_tarea = kwargs['upd_tarea']
        datos = []
        datos_error = []
        for tareas_update in upd_tarea:
           resp = update_tarea(tareas_update['id'], username, **tareas_update)
           if resp is None:
                datos_error.append("Tarea no procesada:"+tareas_update['id'])
               
           datos.append(resp)

    result = {
        "tareas_error": datos_error,
        "tareas_ok": datos
    }

    return result

def update_lote_tareas_v2(username=None, **kwargs):
    print("update_tarea_V2")

    
    if username is not None:
        id_user_actualizacion = verifica_username(username)
        if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if 'upd_tarea' in kwargs:
        upd_tarea = kwargs['upd_tarea']
        datos = []
        datos_error = []
        for tareas_update in upd_tarea:
           resp = update_tarea(tareas_update['id_tarea'], username, **tareas_update)
           if resp is None:
                datos_error.append("Tarea no procesada:"+tareas_update['id_tarea'])
               
           datos.append(resp)

    result = {
        "tareas_error": datos_error,
        "tareas_ok": datos
    }

    return result

def update_lote_tareas(username=None, **kwargs):
    
    print("update_tarea")

    
    if username is not None:
        id_user_actualizacion = verifica_username(username)
        if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if 'id_actuacion' in kwargs:
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == kwargs['id_actuacion']).first()
        if actuacion is None:
            raise Exception("Actuacion no encontrada")
        
    if 'id_expediente' in kwargs:
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == kwargs['id_expediente']).first()
        if expediente is None:
            raise Exception("Expediente no encontrado")
        
    if 'id_tipo_tarea' in kwargs:
        tipo = db.session.query(TipoTarea).filter(TipoTarea.id == kwargs['id_tipo_tarea'], TipoTarea.eliminado==False).first()
        if tipo is  None:
            raise Exception("Tipo de tarea no encontrado")
                     
        if 'id_subtipo_tarea' in kwargs:
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            else:
                subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.id_tipo == kwargs['id_tipo_tarea']).first()
                if subtipo is None:
                    raise Exception("El tipo de tarea y el subtipo de tarea no se corresponden")
    if 'grupo' in kwargs:
        for group in kwargs['grupo']:
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                print("Grupo no encontrado")
                raise Exception("Error en el ingreso de grupos. Grupo no existente: ") + group['id_grupo']
            
            if existe_grupo.eliminado==True:
                print("Grupo eliminado")
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            if existe_grupo.suspendido==True:
                print("Grupo suspendido")
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))
    if 'usuario' in kwargs:
        for user in kwargs['usuario']:
            existe_usuario = db.session.query(Usuario).filter(Usuario.id == user['id_usuario']).first()
            if existe_usuario is None:
                raise Exception("Error en el ingreso de usuarios. Usuario no existente: ") +  user['id_usuario']
            
            if existe_usuario.eliminado==True:
                raise Exception("Error en el ingreso de usuarios. Usuario eliminado: " + existe_usuario.apellido + ' - id: ' + str(existe_usuario.id))

            
    tarea_error=[]
    tarea_procesada=[]
    if 'tareas' in kwargs:
        for tareas_update in kwargs['tareas']:
            if 'id' in tareas_update:
                id_tarea=tareas_update['id']
                tarea = db.session.query(Tarea).filter(Tarea.id == id_tarea).first()
                if tarea is None:
                    tarea_error.append("Tarea no encontrada:"+id_tarea)
                if tarea.eliminado==True:
                    tarea_error.append("Tarea eliminada:"+id_tarea)
                else:
                    print("Tarea encontrada:", tarea.id)
                    if 'caratula_expediente' in kwargs:
                        tarea.caratula_expediente = kwargs['caratula_expediente'].upper()
                        print("Caratula:", tarea.caratula_expediente)
                    if 'cuerpo' in kwargs:
                        tarea.cuerpo = kwargs['cuerpo']
                        print("Cuerpo:", tarea.cuerpo)
                    if 'eliminable' in kwargs:
                        tarea.eliminable = kwargs['eliminable']
                        print("Eliminable:", tarea.eliminable)
                    if 'id_actuacion' in kwargs:
                        tarea.id_actuacion = kwargs['id_actuacion']
                        print("Actuacion:", tarea.id_actuacion)
                    if 'id_expediente' in kwargs:
                        tarea.id_expediente = kwargs['id_expediente'] 
                        print("Expediente:", tarea.id_expediente)   
                    if 'plazo' in kwargs:
                        tarea.plazo = kwargs['plazo']
                        print("Plazo:", tarea.plazo)
                    if 'prioridad' in kwargs:
                        tarea.prioridad = kwargs['prioridad']
                        print("Prioridad:", tarea.prioridad)
                    if 'estado' in kwargs:
                        tarea.estado = kwargs['estado']    
                        print("Estado:", tarea.estado)
                    if 'titulo' in kwargs:
                        tarea.titulo = kwargs['titulo']
                        print("Titulo:", tarea.titulo) 
                    #Validacion de tipo y subtipo de tarea
                    if 'id_tipo_tarea' in kwargs:
                        tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
                    if 'id_subtipo_tarea' in kwargs:
                        tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']
                 
                    tarea.id_user_actualizacion = id_user_actualizacion  
                    tarea.fecha_actualizacion = datetime.now()
                    print("Tarea actualizada:", tarea.id)
                    usuarios=[]
                    grupos=[]
                    if 'grupo' in kwargs:
                        #elimino los grupos existentes para esa tarea 
                        grupo_tarea=db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_tarea)

                        for grupo in grupo_tarea:
                            grupo.eliminado=True
                            grupo.fecha_actualizacion=datetime.now()
                            grupo.id_user_actualizacion=id_user_actualizacion

                        for group in kwargs['grupo']:
                            #asocio el grupo a la tarea
                            nuevoID=uuid.uuid4()
                            tareaxgrupo = db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_tarea, TareaXGrupo.id_grupo==group['id_grupo']).first()
                            if tareaxgrupo is None:
                                nuevo_tarea_grupo = TareaXGrupo(
                                    id=nuevoID,
                                    id_grupo=group['id_grupo'],
                                    id_tarea=id_tarea,
                                    id_user_actualizacion= id_user_actualizacion,
                                    fecha_asignacion=datetime.now(),
                                    fecha_actualizacion=datetime.now()
                                )
                                db.session.add(nuevo_tarea_grupo)
                            else:
                                print("Reactiva grupo")
                                if tareaxgrupo.eliminado==True:
                                    tareaxgrupo.eliminado=False
                                    tareaxgrupo.fecha_actualizacion=datetime.now()
                                    tareaxgrupo.fecha_actualizacion=datetime.now()
                                    tareaxgrupo.id_user_actualizacion=id_user_actualizacion   

                            grupo = {
                                "id": existe_grupo.id,
                                "nombre": existe_grupo.nombre,
                                "asignado": 'True',
                                "fecha_asisgnacion": datetime.now()
                            }
                            grupos.append(grupo)


                    if 'usuario' in kwargs:
                        #elimino los usuarios existentes para esa tarea
                        usuarios_tarea=db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_tarea)
                        if usuarios_tarea:
                            for usuario in usuarios_tarea:
                                usuario.eliminado=True
                                usuario.fecha_actualizacion=datetime.now()

                        #asocio el usuario a la tarea
                        for user in kwargs['usuario']:
                            print("Asigna Usuario:", user['id_usuario'])
                            existe_usuario = db.session.query(Usuario).filter(Usuario.id == user['id_usuario']).first()
                            if existe_usuario is None:
                                raise Exception("Error en el ingreso de usuarios. Usuario no existente")
                            
                            if existe_usuario.eliminado==True:
                                raise Exception("Error en el ingreso de usuarios. Usuario eliminado: " + existe_usuario.apellido + ' - id: ' + str(existe_usuario.id))

                            nuevoID=uuid.uuid4()
                            asigna_usuario = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_tarea, TareaAsignadaUsuario.id_usuario==user['id_usuario']).first()
                            if asigna_usuario is None:
                                nuevo_asigna_usuario = TareaAsignadaUsuario(
                                    id=nuevoID,
                                    id_tarea=id_tarea,
                                    id_usuario=user['id_usuario'],
                                    id_user_actualizacion= id_user_actualizacion,
                                    fecha_asignacion=datetime.now(),
                                    fecha_actualizacion=datetime.now()
                                )
                                db.session.add(nuevo_asigna_usuario)
                            else:
                                #si el usuario ya tuvo la tarea reasigno el usuario
                                if asigna_usuario.eliminado==True:
                                    asigna_usuario.eliminado=False
                                    asigna_usuario.fecha_actualizacion=datetime.now()
                                    asigna_usuario.fecha_actualizacion=datetime.now()
                                    asigna_usuario.id_user_actualizacion=id_user_actualizacion

                            usuario = {
                                "id": existe_usuario.id,
                                "nombre": existe_usuario.nombre,
                                "apellido": existe_usuario.apellido,
                                "asignado": 'True',
                                "fecha_asignacion": datetime.now()
                            }
                            usuarios.append(usuario)
                    tarea_ok = {
                            "id": tarea.id
                        }    

                    tarea_procesada.append(tarea_ok)
   

    ###################Formatear el resultado####################
    result = {
        "tareas_error": tarea_error,
        "tareas_ok": tarea_procesada
    }

    db.session.commit()
    return result

@cache.memoize(timeout=3600)
def get_all_tipo_tarea(page=1, per_page=10):
    #print("get_tipo_tareas - ", page, "-", per_page)
    
    todo = db.session.query(TipoTarea).all()
    total= len(todo)
    res = db.session.query(TipoTarea).order_by(TipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_tarea(username=None, id='', codigo_humano='', nombre='', id_user_actualizacion='', base=False):
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
           
    nuevoID=uuid.uuid4()

    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
        base=base,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_tipo_tarea)
    db.session.commit()
    return nuevo_tipo_tarea


def update_tipo_tarea(username=None, tipo_tarea_id='', **kwargs):

    

    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")

    tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == tipo_tarea_id).first()
    
    if tipo_tarea is None:
        raise Exception("Tipo de tarea no encontrado")
    
    if 'codigo_humano' in kwargs:
        tipo_tarea.codigo_humano = kwargs['codigo_humano']
    if 'nombre' in kwargs:
        tipo_tarea.nombre = kwargs['nombre']
    if 'base' in kwargs:
        tipo_tarea.base = kwargs['base'] 
    else:
        tipo_tarea.base = False

    tipo_tarea.id_user_actualizacion = id_user_actualizacion
    tipo_tarea.fecha_actualizacion = datetime.now()
    db.session.commit()
    return tipo_tarea


def delete_tipo_tarea(username=None, id=None):

    
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id, TipoTarea.eliminado==False).first()
    if tipo_tarea is not None:
        tipo_tarea.eliminado=True
        tipo_tarea.fecha_actualizacion=datetime.now()
        tipo_tarea.id_user_actualizacion=id_user_actualizacion
        db.session.commit()
        return tipo_tarea
    else:
        return None
    
#########################SUBTIPO TAREA############################################
def get_all_subtipo_tarea(page=1, per_page=10, id_tipo_tarea=None, eliminado=None):
    #print("get_tipo_tareas - ", page, "-", per_page)
    

    query = db.session.query(SubtipoTarea)
    if id_tipo_tarea is not None:
        query = query.filter(SubtipoTarea.id_tipo==id_tipo_tarea)
    if eliminado is not None:
        query = query.filter(SubtipoTarea.eliminado==eliminado)

    total= len(query.all())

    res = query.order_by(SubtipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total    

def insert_subtipo_tarea(username=None, id_tipo='', nombre='', id_user_actualizacion='', base=False):
    

    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    
    if id_tipo is not None:
        tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id_tipo, TipoTarea.eliminado==False).first()
        if tipo_tarea is None:
            raise Exception("Tipo de tarea no encontrado")


    nuevoID=uuid.uuid4()
    nuevo_subtipo_tarea = SubtipoTarea(
        id=nuevoID,
        id_tipo=id_tipo,
        nombre=nombre,
        base=base,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_subtipo_tarea)
    db.session.commit()
    return nuevo_subtipo_tarea

def update_subtipo_tarea(username=None, subtipo_id='', **kwargs):

    

    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")

    subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == subtipo_id).first()
    
    if subtipo_tarea is None:
        raise Exception("Subtipo de tarea no encontrado")
    
    if 'nombre' in kwargs:
        subtipo_tarea.nombre = kwargs['nombre']
        
    if 'base' in kwargs:
        subtipo_tarea.base = kwargs['base']
    else:
        subtipo_tarea.base = False   

    subtipo_tarea.id_user_actualizacion = id_user_actualizacion    
    subtipo_tarea.fecha_actualizacion = datetime.now()
    db.session.commit()
    return subtipo_tarea

def delete_subtipo_tarea(username=None, id=None):
    

    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id, SubtipoTarea.eliminado==False).first()
    if subtipo_tarea is not None:
        subtipo_tarea.eliminado=True
        subtipo_tarea.id_user_actualizacion=id_user_actualizacion
        subtipo_tarea.fecha_actualizacion=datetime.now()
        db.session.commit()
        return subtipo_tarea
    else:
        #print("Subtipo de tarea no encontrado")
        return None
    
##########################TAREAS #############################################
def insert_usuario_tarea(id_tarea='', id_usuario='',id_user_actualizacion='', notas=""):
    msg=''
    
    tareas = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()
    if tareas is None:
        #print("Tarea no encontrada")
        msg = "Tarea no encontrada"
        asigna_usuario= None
        return asigna_usuario, msg
    
    tarea_asignada = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea==id_tarea, TareaAsignadaUsuario.id_usuario==id_usuario).first()
    
    if tarea_asignada is not None:
        #print("Usuario ya asignado a la tarea")
        msg = "Usuario ya asignado a la tarea"
        asigna_usuario= None
        return asigna_usuario, msg
    
    nuevoID=uuid.uuid4()
    asigna_usuario = TareaAsignadaUsuario(
        id=nuevoID,
        id_tarea=id_tarea,
        id_usuario=id_usuario,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(asigna_usuario)
    db.session.commit()
    return asigna_usuario, msg

def get_tarea_historia_usr_by_id(id):
    
    query = (
    db.session.query(
        Tarea.id.label("id_tarea"),
        Tarea.titulo,
        TareaAsignadaUsuario.id_usuario,
        Usuario.apellido,
        Usuario.username,
        TareaAsignadaUsuario.eliminado,
        func.coalesce(
            cast(Auditoria_TareaAsignadaUsuario.datos_anteriores[("eliminado")].astext, Boolean),
            False
        ).label("eliminado_anterior"),
        func.coalesce(
            cast(Auditoria_TareaAsignadaUsuario.datos_nuevos[("eliminado")].astext, Boolean),
            False
        ).label("eliminado_nueva"),
        cast(
            Auditoria_TareaAsignadaUsuario.datos_anteriores[("fecha_actualizacion")].astext,
            TIMESTAMP
        ).label("fecha_actualizacion_anterior"),
        cast(
            Auditoria_TareaAsignadaUsuario.datos_nuevos[("fecha_actualizacion")].astext,
            TIMESTAMP
        ).label("fecha_actualizacion"),
    )
    .outerjoin(
        TareaAsignadaUsuario,
        Tarea.id == TareaAsignadaUsuario.id_tarea
    )
    .outerjoin(
        Auditoria_TareaAsignadaUsuario,
        Auditoria_TareaAsignadaUsuario.id_registro == TareaAsignadaUsuario.id
    )
    .outerjoin(
        Usuario,
        TareaAsignadaUsuario.id_usuario == Usuario.id
    )
    .filter(Tarea.id == id)  # Se utiliza la variable aquí
    .order_by(Usuario.apellido, Auditoria_TareaAsignadaUsuario.fecha_actualizacion.desc())
    )

# Ejecutar la consulta
    result = query.all()
    print (result)
    return result


def get_tarea_by_id(id):
    
    
    res = db.session.query(Tarea).filter(Tarea.id == id).first()
    
    results = []
   
    if res is not None:
        res_usuarios = db.session.query(Usuario.id, Usuario.nombre, Usuario.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                  ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== res.id).order_by(TareaAsignadaUsuario.eliminado).all()
        
        res_grupos = db.session.query(Grupo.id, Grupo.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                  ).join(TareaXGrupo, Grupo.id==TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea== res.id).order_by(TareaXGrupo.eliminado).all()

        
        res_notas = db.session.query(Nota).filter(Nota.id_tarea== res.id, Nota.eliminado==False).order_by(desc(Nota.fecha_creacion)).all()     

            
        if res_usuarios is not None:
            usuarios=[]
            grupos=[]
            notas=[]
            reasignada_usuario=False
            reasignada_grupo=False
            grupos_usr=[]
            for row in res_usuarios:
                usuario_grupo = db.session.query(UsuarioGrupo.id_grupo, Grupo.nombre).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario==row.id, UsuarioGrupo.eliminado==False).all()
                if usuario_grupo is not None:
                    for usr_gr in usuario_grupo:
                        grupo_usr = {
                           "id_grupo": usr_gr.id_grupo,
                           "nombre": usr_gr.nombre
                        }
                        grupos_usr.append(grupo_usr)    

                usuario = {
                    "id_usuario": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido,
                    "asignada": not(row.reasignada),
                    "fecha_asignacion": row.fecha_asignacion,
                    "grupos_usr": grupos_usr
                }
                if row.reasignada:
                    reasignada_usuario=True
                usuarios.append(usuario)

        if res_grupos is not None:
            for row in res_grupos:
                grupo = {
                    "id_grupo": row.id,
                    "nombre": row.nombre,
                    "asignada": not(row.reasignada),
                    "fecha_asignacion": row.fecha_asignacion
                }
                if row.reasignada:
                    reasignada_grupo=True
                grupos.append(grupo)

        if res_notas is not None:
            for row in res_notas:
                nota = {
                    "id": row.id,
                    "nota": row.nota,
                    "id_tipo_nota": row.id_tipo_nota,
                    "tipo_nota": row.tipo_nota,
                    "titulo": row.titulo,
                    "fecha_creacion": row.fecha_creacion,
                    "id_user_creacion": row.id_user_creacion,
                    "user_creacion": row.user_creacion,
                    "id_user_actualizacion": row.id_user_actualizacion
                }
                notas.append(nota)         


        ###################Formatear el resultado####################
        result = {
            "id": res.id,
            "titulo": res.titulo,
            "fecha_inicio": res.fecha_inicio,
            "fecha_fin": res.fecha_fin,
            "plazo": res.plazo,
            #"prioridad": res.prioridad,
            #"estado": res.estado,
            "prioridad": {'id': res.prioridad, 'descripcion': nombre_prioridad(res.prioridad)},
            "estado": {'id': res.estado, 'descripcion': nombre_estado(res.estado)},
            "id_tipo_tarea": res.id_tipo_tarea,
            "id_subtipo_tarea": res.id_subtipo_tarea,
            "tipo_tarea": res.tipo_tarea,
            "subtipo_tarea": res.subtipo_tarea,
            "id_expediente": res.id_expediente,
            "expediente": res.expediente,
            "caratula_expediente": res.caratula_expediente,
            "id_actuacion": res.id_actuacion,
            "actuacion": res.actuacion,
            "cuerpo": res.cuerpo,
            "eliminable": res.eliminable,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "fecha_creacion": res.fecha_creacion,
            "grupo": grupos,
            "usuario": usuarios,
            "notas": notas,
            "id_user_actualizacion": res.id_user_actualizacion,
            "user_actualizacion": res.user_actualizacion,
            "reasignada_usuario": reasignada_usuario,
            "reasignada_grupo": reasignada_grupo
        }

        results.append(result)
   
    else:
        #print("Tarea no encontrada")
        return None
    
    return results 

def get_tarea_grupo(username=None, page=1, per_page=10):
    
    
    if username is not None:
        id_user = verifica_username(username)
        if id_user is None:
            raise Exception("Usuario no encontrado")
    #id_user = 'f9799cd5-aad3-4339-ac6e-62544e3e64f1'
    # Obtener los grupos del usuario
    query_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id_user, UsuarioGrupo.eliminado==False).all()
    ids_grupos = [row.id_grupo for row in query_grupo]

    # Si el usuario no pertenece a ningún grupo, filtrar por tareas asignadas al usuario
    if not ids_grupos:
        usuario_alias = aliased(Usuario)
        print("Usuario no pertenece a ningún grupo")
        query = (
            db.session.query(
                Tarea,
                usuario_alias.id.label("usuario_id"),
                usuario_alias.nombre.label("usuario_nombre"),
                usuario_alias.apellido.label("usuario_apellido"),
                Nota.id.label("nota_id"),
                Nota.nota.label("nota"),
                Nota.id_tipo_nota.label("nota_tipo_id"),
                Nota.tipo_nota.label("nota_tipo"),
                Nota.titulo.label("nota_titulo"),
                Nota.fecha_creacion.label("nota_fecha_creacion"),
                Nota.id_user_creacion.label("nota_user_creacion"),
                Nota.id_user_actualizacion.label("nota_user_actualizacion"),
                TareaAsignadaUsuario.fecha_asignacion.label("fecha_asignacion"),
                TareaAsignadaUsuario.eliminado.label("asignada_usuario")
            )
            .join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea)
            .join(usuario_alias, TareaAsignadaUsuario.id_usuario == usuario_alias.id)
            .outerjoin(Nota, (Tarea.id == Nota.id_tarea) & (Nota.eliminado == False))  # Notas opcionales
            .filter(TareaAsignadaUsuario.id_usuario==id_user)
            .order_by(desc(Tarea.fecha_creacion))
        )
        for row in query:
            print(row)

        total_query = (
            db.session.query(func.count(Tarea.id))
            .join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea)
            .filter(TareaAsignadaUsuario.id_usuario==id_user)
        )
        total = total_query.scalar()

        # Paginación
        res_tareas = query.offset((page - 1) * per_page).limit(per_page).all()

    else:
        # Si el usuario pertenece a grupos, filtrar por tareas asociadas a esos grupos
        usuario_alias = aliased(Usuario)
        grupo_alias = aliased(Grupo)

        query = (
            db.session.query(
                Tarea,
                grupo_alias.id.label("grupo_id"),
                grupo_alias.nombre.label("grupo_nombre"),
                usuario_alias.id.label("usuario_id"),
                usuario_alias.nombre.label("usuario_nombre"),
                usuario_alias.apellido.label("usuario_apellido"),
                Nota.id.label("nota_id"),
                Nota.nota.label("nota"),
                Nota.id_tipo_nota.label("nota_tipo_id"),
                Nota.tipo_nota.label("nota_tipo"),
                Nota.titulo.label("nota_titulo"),
                Nota.fecha_creacion.label("nota_fecha_creacion"),
                Nota.id_user_creacion.label("nota_user_creacion"),
                Nota.id_user_actualizacion.label("nota_user_actualizacion"),
                TareaXGrupo.eliminado.label("asignada_grupo"),
                TareaAsignadaUsuario.eliminado.label("asignada_usuario")
            )
            .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
            .join(grupo_alias, TareaXGrupo.id_grupo == grupo_alias.id)
            .join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea)
            .join(usuario_alias, TareaAsignadaUsuario.id_usuario == usuario_alias.id)
            .outerjoin(Nota, (Tarea.id == Nota.id_tarea) & (Nota.eliminado == False))  # Notas opcionales
            .filter(TareaXGrupo.id_grupo.in_(ids_grupos))
            .order_by(desc(Tarea.fecha_creacion))
        )

        for row in query:
            print(row)
            print("asignada_grupo:", row.asignada_grupo)
            print("asignada_usuario:", row.asignada_usuario)
            print("-------------------------------------------------")

        # Calcular el total de tareas
        total_query = (
            db.session.query(func.count(Tarea.id))
            .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
            .filter(TareaXGrupo.id_grupo.in_(ids_grupos))
        )
        total = total_query.scalar()

        # Paginación
        res_tareas = query.offset((page - 1) * per_page).limit(per_page).all()

    # Formatear el resultado
    results = []
    tareas_agrupadas = {}
    
    for (
        tarea,
        grupo_id, grupo_nombre,
        usuario_id, usuario_nombre, usuario_apellido, 
        nota_id, nota, nota_tipo_id, nota_tipo, nota_titulo, nota_fecha_creacion, nota_user_creacion, nota_user_actualizacion,
        asignada_usuario, asignada_grupo
    ) in res_tareas:
        # Agrupar información de la tarea
        if tarea.id not in tareas_agrupadas:
            tareas_agrupadas[tarea.id] = {
                "id": tarea.id,
                "titulo": tarea.titulo,
                "fecha_inicio": tarea.fecha_inicio,
                "fecha_fin": tarea.fecha_fin,
                "plazo": tarea.plazo,
                "prioridad": tarea.prioridad,
                "estado": tarea.estado,
                "id_tipo_tarea": tarea.id_tipo_tarea,
                "id_subtipo_tarea": tarea.id_subtipo_tarea,
                "tipo_tarea": tarea.tipo_tarea,
                "subtipo_tarea": tarea.subtipo_tarea,
                "id_expediente": tarea.id_expediente,
                "expediente": tarea.expediente,
                "caratula_expediente": tarea.caratula_expediente,
                "id_actuacion": tarea.id_actuacion,
                "actuacion": tarea.actuacion,
                "cuerpo": tarea.cuerpo,
                "eliminable": tarea.eliminable,
                "eliminado": tarea.eliminado,
                "fecha_eliminacion": tarea.fecha_eliminacion,
                "fecha_actualizacion": tarea.fecha_actualizacion,
                "fecha_creacion": tarea.fecha_creacion,
                "id_user_actualizacion": tarea.id_user_actualizacion,
                "user_actualizacion": tarea.user_actualizacion,
                "grupos": [],
                "usuarios": [],
                "notas": [],
                "reasignada_usuario": False,
                "reasignada_grupo": False
            }
        
        # Añadir información de grupos
        if grupo_id and grupo_nombre:
            tareas_agrupadas[tarea.id]["grupos"].append(
                {"id": grupo_id, "nombre": grupo_nombre, "asignada": not asignada_grupo}
            )
        
        # Añadir información de usuarios
        if usuario_id and usuario_nombre:
            tareas_agrupadas[tarea.id]["usuarios"].append(
                {"id": usuario_id, "nombre": usuario_nombre, "apellido": usuario_apellido, "asignada": not asignada_usuario}
            )

        # Añadir información de notas
        if nota_id and nota:
            tareas_agrupadas[tarea.id]["notas"].append(
                {
                   "id": nota_id,
                    "nota": nota,
                    "id_tipo_nota": nota_tipo_id,
                    "tipo_nota": nota_tipo,
                    "titulo": nota_titulo,
                    "fecha_creacion": nota_fecha_creacion,
                    "id_user_creacion": nota_user_creacion,
                    "id_user_actualizacion": nota_user_actualizacion
                }
            )

    # Convertir tareas agrupadas en lista final
    results = list(tareas_agrupadas.values())
    
    return results, total

    

    """ result = {
            "id": tarea.id,
            "titulo": tarea.titulo,
            "fecha_inicio": tarea.fecha_inicio,
            "fecha_fin": tarea.fecha_fin,
            "plazo": tarea.plazo,
            "prioridad": tarea.prioridad,
            "estado": tarea.estado,
            "id_tipo_tarea": tarea.id_tipo_tarea,
            "id_subtipo_tarea": tarea.id_subtipo_tarea,
            "tipo_tarea": tarea.tipo_tarea,
            "subtipo_tarea": tarea.subtipo_tarea,
            "id_expediente": tarea.id_expediente,
            "expediente": tarea.expediente,
            "caratula_expediente": tarea.caratula_expediente,
            "id_actuacion": tarea.id_actuacion,
            "actuacion": tarea.actuacion,
            "cuerpo": tarea.cuerpo,
            "eliminable": tarea.eliminable,
            "eliminado": tarea.eliminado,
            "fecha_eliminacion": tarea.fecha_eliminacion,
            "fecha_actualizacion": tarea.fecha_actualizacion,
            "fecha_creacion": tarea.fecha_creacion,
            "grupos": grupos,
            "usuarios": usuarios,
            "id_user_actualizacion": tarea.id_user_actualizacion,
            "user_actualizacion": tarea.user_actualizacion
         }
        results.append(result) """




def get_tarea_grupo_by_id(username=None, page=1, per_page=10):
    
    
    results = []

    if username is not None:
        id_user = verifica_username(username)
        if id_user is None:
            raise Exception("Usuario no encontrado")
        
    query_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario==id_user).all()    
        
    if not query_grupo:  # Si no pertenece a ningún grupo
        print("Usuario no pertenece a ningún grupo")
        reasignada_grupo=False
        query = (
            db.session.query(Tarea)
            .join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea)
            .filter(TareaAsignadaUsuario.id_usuario == id_user)
            .order_by(desc(Tarea.fecha_creacion))
        )
    else:
    # Recopilamos todos los IDs de grupos en una lista
        ids_grupos = [row.id_grupo for row in query_grupo]
        print("IDs de grupos:", ids_grupos)
        
        # Consulta para obtener las tareas de los grupos
        query = (
            db.session.query(Tarea)
            .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
            .filter(TareaXGrupo.id_grupo.in_(ids_grupos))  # Filtrar por múltiples grupos
            #.distinct()
            .order_by(desc(Tarea.fecha_creacion))
        )

    total= len(query.all())
    print("total de tareas:", total)
    res_tareas = query.offset((page-1)*per_page).limit(per_page).all()

    results = []
    usuario_alias = aliased(Usuario)
    grupo_alias = aliased(Grupo)

    for res in res_tareas:
        grupos=[]
        usuarios=[]
        notas=[]
        reasignada_usuario=False
        reasignada_grupo=False
        res_grupos = db.session.query(grupo_alias.id, grupo_alias.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                   ).join(TareaXGrupo, grupo_alias.id == TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea == res.id).order_by(TareaXGrupo.eliminado).all()
        #print(str(res_grupos))

        for row in res_grupos:
            grupo = {
                "id": row.id,
                "nombre": row.nombre,
                "asignada": not row.reasignada,
                "fecha_asignacion": row.fecha_asignacion
            }
            if row.reasignada:
                reasignada_grupo = True
            grupos.append(grupo) 
        
         #Consulto los usuarios asignados a la tarea
        res_usuarios = db.session.query(usuario_alias.id, usuario_alias.nombre, usuario_alias.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                     ).join(TareaAsignadaUsuario, usuario_alias.id == TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea == res.id).order_by(TareaAsignadaUsuario.eliminado).all()
       

        #res_usuarios = db.session.query(Usuario.id, Usuario.nombre, Usuario.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
        #                          ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== res.id).order_by(TareaAsignadaUsuario.eliminado).all()
        
        if res_usuarios is not None:
            for row in res_usuarios:
                usuario = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido,
                    "asignada": not(row.reasignada),
                    "fecha_asignacion": row.fecha_asignacion
                }
                if row.reasignada:
                    reasignada_usuario=True
                usuarios.append(usuario)

        res_notas = db.session.query(Nota).filter(Nota.id_tarea== res.id, Nota.eliminado==False).order_by(desc(Nota.fecha_creacion)).all()     

        if res_notas is not None:
            for row in res_notas:
                nota = {
                    "id": row.id,
                    "nota": row.nota,
                    "id_tipo_nota": row.id_tipo_nota,
                    "tipo_nota": row.tipo_nota,
                    "titulo": row.titulo,
                    "fecha_creacion": row.fecha_creacion, 
                    "id_user_creacion": row.id_user_creacion,
                    "user_creacion": row.user_creacion,
                    "id_user_actualizacion": row.id_user_actualizacion
                }
                notas.append(nota) 
        ###################Formatear el resultado####################

        result = {  
            "id": res.id,
            "titulo": res.titulo,
            "fecha_inicio": res.fecha_inicio,
            "fecha_fin": res.fecha_fin,
            "plazo": res.plazo,
            "prioridad": res.prioridad,
            "estado": res.estado,
            "id_tipo_tarea": res.id_tipo_tarea,
            "tipo_tarea": res.tipo_tarea,
            "id_subtipo_tarea": res.id_subtipo_tarea,
            "subtipo_tarea": res.subtipo_tarea,
            "id_expediente": res.id_expediente,
            "expediente": res.expediente,
            "caratula_expediente": res.caratula_expediente,
            "id_actuacion": res.id_actuacion,
            "actuacion": res.actuacion,
            "cuerpo": res.cuerpo,
            "eliminable": res.eliminable,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "fecha_creacion": res.fecha_creacion,
            "grupos": grupos,
            "usuarios": usuarios,
            "notas": notas,
            "id_user_actualizacion": res.id_user_actualizacion,
            "user_actualizacion": res.user_actualizacion,
            "reasignada_usuario": reasignada_usuario,
            "reasignada_grupo": reasignada_grupo
        }
        results.append(result)
    
    
    return results, total         



# @cache.cached(timeout=500)
def get_all_tarea_detalle(page=1, per_page=10, titulo='', label='', labels=None, id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_usuario_asignado=None, id_grupo=None, grupos=None, id_tarea=None, fecha_desde='01/01/2000',  fecha_hasta=datetime.now().strftime('%d/%m/%Y'), fecha_fin_desde=None, fecha_fin_hasta=None, prioridad=0, estado=0, eliminado=None, tiene_notas=None):

    print("*******************************************************")
    print("get_all_tarea_detalle")
    print("*******************************************************")
    
    query = db.session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
    
    if fecha_fin_desde is not None and fecha_fin_hasta is not None:
        query = query.filter(Tarea.fecha_fin.between(fecha_fin_desde, fecha_fin_hasta))
    # Apply filters based on provided parameters
    if id_tarea is not None:
        query = query.filter(Tarea.id == id_tarea)
    if titulo:
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
    if id_expediente is not None:
        query = query.filter(Tarea.id_expediente == id_expediente)
    if id_actuacion is not None:
        query = query.filter(Tarea.id_actuacion == id_actuacion)
    if id_tipo_tarea is not None:
        query = query.filter(Tarea.id_tipo_tarea == id_tipo_tarea)
    if id_usuario_asignado is not None:
        query = query.join(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_usuario == id_usuario_asignado, TareaAsignadaUsuario.eliminado == False)
    if id_grupo is not None:
        query = query.join(TareaXGrupo).filter(TareaXGrupo.id_grupo == id_grupo)
    if prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)
    if estado > 0:
        query = query.filter(Tarea.estado == estado)
    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)
    if tiene_notas is not None:
        query = query.filter(Tarea.tiene_notas_desnz == tiene_notas)    
    """ if label:
        print("label:", label)
        query = query.join(LabelXTarea, Tarea.id == LabelXTarea.id_tarea
                ).join(Label, Label.id == LabelXTarea.id_label
                ).filter(Label.nombre.ilike(f"%{label}%")) """
    if labels:
        print("labels:", labels)
        query = query.join(LabelXTarea, Tarea.id == LabelXTarea.id_tarea
                ).filter(LabelXTarea.id_label.in_(labels), LabelXTarea.activa == True
                ).distinct()
    if grupos:
        print("Grupos a filtrar:", grupos)
        query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
                ).filter(TareaXGrupo.id_grupo.in_(grupos), TareaXGrupo.eliminado == False
                ).distinct()         

    # Get total count of tasks matching the filter
    total = query.count()
    print("Total de tareas:", total)
    
    # Pagination with eager loading for associated users and groups
    res_tareas = query.order_by(desc(Tarea.fecha_creacion)).offset((page - 1) * per_page).limit(per_page).all()
    for tarea in res_tareas:
        logger.info(f"Tarea: {tarea.id} - {tarea.titulo}")

    # Process each task in paginated results
    results = []
    
    # Using aliased subqueries to reduce the number of queries for users and groups
    usuario_alias = aliased(Usuario)
    grupo_alias = aliased(Grupo)

    for res in res_tareas:
        usuarios = []
        grupos = []
        reasignada_usuario = False
        reasignada_grupo = False
        
        # Fetch assigned users for the task
        res_usuarios = db.session.query(usuario_alias.id, usuario_alias.nombre, usuario_alias.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                     ).join(TareaAsignadaUsuario, usuario_alias.id == TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea == res.id).order_by(TareaAsignadaUsuario.eliminado).all()
        #print(str(res_usuarios))
        
        for row in res_usuarios:
            usuario = {
                "id_usuario": row.id,
                "nombre": row.nombre,
                "apellido": row.apellido,
                "asignada": not row.reasignada,
                "fecha_asignacion": row.fecha_asignacion
            }
            if row.reasignada:
                reasignada_usuario = True
            usuarios.append(usuario)

        # Fetch assigned groups for the task
        res_grupos = db.session.query(grupo_alias.id, grupo_alias.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                   ).join(TareaXGrupo, grupo_alias.id == TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea == res.id).order_by(TareaXGrupo.eliminado).all()
        #print(str(res_grupos))

        for row in res_grupos:
            grupo = {
                "id_grupo": row.id,
                "nombre": row.nombre,
                "asignada": not row.reasignada,
                "fecha_asignacion": row.fecha_asignacion
            }
            if row.reasignada:
                reasignada_grupo = True
            grupos.append(grupo)            
        
        # Prepare result dictionary
        result = {
            "id": res.id,
            "titulo": res.titulo,
            "fecha_inicio": res.fecha_inicio,
            "fecha_fin": res.fecha_fin,
            "plazo": res.plazo,
            #"prioridad": res.prioridad,
            #"estado": res.estado,
            "prioridad": {'id': res.prioridad, 'descripcion': nombre_prioridad(res.prioridad)},
            "estado": {'id': res.estado, 'descripcion': nombre_estado(res.estado)},
            "id_tipo_tarea": res.id_tipo_tarea,
            "tipo_tarea": res.tipo_tarea,
            "id_subtipo_tarea": res.id_subtipo_tarea,
            "subtipo_tarea": res.subtipo_tarea,
            "id_expediente": res.id_expediente,
            "expediente": res.expediente,
            "caratula_expediente": res.caratula_expediente,
            "id_actuacion": res.id_actuacion,
            "actuacion": res.actuacion,
            "cuerpo": res.cuerpo,
            "eliminable": res.eliminable,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "fecha_creacion": res.fecha_creacion,
            "tiene_notas": res.tiene_notas_desnz,
            "grupo": grupos,
            "usuario": usuarios,
            "notas": [],  # Keeping notes as an empty list, as in original code
            "id_user_actualizacion": res.id_user_actualizacion,
            "user_actualizacion": res.user_actualizacion,
            "reasignada_usuario": reasignada_usuario,
            "reasignada_grupo": reasignada_grupo
        }
        results.append(result)

    return results, total



def get_all_tarea(page=1, per_page=10, titulo='', id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_tarea=None, id_usuario_asignado=None, id_grupo=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), prioridad=0, estado=0, eliminado=None, tiene_notas=None):
    #fecha_hasta = fecha_hasta + " 23:59:59"
    
    
    
    query = db.session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
   
    if titulo is not '':
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
   
    if id_expediente is not None:
        query = query.filter(Tarea.id_expediente == id_expediente)
    
    if id_actuacion is not None:
        query = query.filter(Tarea.id_actuacion == id_actuacion)

    if id_tipo_tarea is not None:
        query = query.filter(Tarea.id_tipo_tarea== id_tipo_tarea)

    if id_tarea is not None:
        query = query.filter(Tarea.id == id_tarea)    

    if id_usuario_asignado is not None:
        #print ("id_usuario_asignado:", id_usuario_asignado)
        usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario_asignado, Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario no encontrado")
        query = query.join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario == id_usuario_asignado)

    if id_grupo is not None:
        grupo = db.session.query(Grupo).filter(Grupo.id == id_grupo, Grupo.eliminado==False).first()
        if grupo is None:
            raise Exception("Grupo no encontrado")
        query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id_grupo)
       
    if prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)

    if estado > 0:
        query = query.filter(Tarea.estado == estado)

    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)

    if tiene_notas is not None:
        query = query.filter(Tarea.tiene_notas_desnz == tiene_notas)    

    print ("Tiene notas:", tiene_notas)
    total = query.count()
    print("Total de tareas:", total)

    result = query.order_by(Tarea.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    results = []
    if result is not None:
        reasignada_usr=False
        reasignada_grupo=False
        for reg in result:
            notas=[]
            if id_usuario_asignado is not None:
                tarea_asignada_usr = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == reg.id, TareaAsignadaUsuario.id_usuario == id_usuario_asignado).first()
                if tarea_asignada_usr is not None:
                    reasignada_usr = (tarea_asignada_usr.eliminado)
            else:
                tarea_asignada_usr = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == reg.id, TareaAsignadaUsuario.eliminado==True).first()       
                if tarea_asignada_usr is not None:
                    reasignada_usr = True

            if id_grupo is not None:
                tarea_asignada_grupo = db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == reg.id, TareaXGrupo.id_grupo == id_grupo).first()
                if tarea_asignada_grupo is not None:
                    reasignada_grupo = (tarea_asignada_grupo.eliminado)   
            else:
                tarea_asignada_grupo = db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == reg.id, TareaXGrupo.eliminado==True).first()
                if tarea_asignada_grupo is not None:
                    reasignada_grupo = True
            #print("#"*50)
            #print("Id tarea:", reg.id)
            
            res_notas = db.session.query(Nota).filter(Nota.id_tarea== reg.id, Nota.eliminado==False).order_by(desc(Nota.fecha_creacion)).all()     
            
            if res_notas is not None:
                #print("Total de notas: ", len(res_notas))
                #print("#"*50)
                for row in res_notas:
                    nota = {
                        "id": row.id,
                        "nota": row.nota,
                        "id_tipo_nota": row.id_tipo_nota,
                        "tipo_nota": row.tipo_nota,
                        "titulo": row.titulo,
                        "fecha_creacion": row.fecha_creacion, 
                        "id_user_creacion": row.id_user_creacion,
                        "user_creacion": row.user_creacion,
                        "id_user_actualizacion": row.id_user_actualizacion,
                        "eliminado": row.eliminado
                    }
                    notas.append(nota)  

            result = {
                "caratula_expediente": reg.caratula_expediente,
                "cuerpo": reg.cuerpo,
                "eliminable": reg,
                "eliminado": reg.eliminado,
                "estado": reg.estado,
                "fecha_actualizacion": reg.fecha_actualizacion,
                "fecha_creacion": reg.fecha_creacion,
                "fecha_eliminacion": reg.fecha_eliminacion,
                "fecha_fin": reg.fecha_fin,
                "fecha_inicio": reg.fecha_inicio,
                "id": reg.id,
                "id_actuacion": reg.id_actuacion,
                "actuacion": reg.actuacion,
                "id_expediente":reg.id_expediente,
                "expediente": reg.expediente,
                "id_subtipo_tarea": reg.id_subtipo_tarea,
                "subtipo_tarea": reg.subtipo_tarea,
                "id_tipo_tarea": reg.id_tipo_tarea,
                "tipo_tarea": reg.tipo_tarea,
                "id_user_actualizacion": reg.id_user_actualizacion,
                "user_actualizacion": reg.user_actualizacion,
                "plazo": reg.plazo,
                "prioridad": reg.prioridad,
                "titulo": reg.titulo,
                "reasignada_usr": reasignada_usr,
                "reasignada_grupo": reasignada_grupo,
                "notas": notas,
                "tiene_notas": reg.tiene_notas_desnz
            }
            results.append(result)

    return results, total

def usuarios_tarea(tarea_id=""):
    
    print("Usuarios por tarea:", tarea_id)    
    usuarios = db.session.query(Usuario.nombre.label('nombre'),
                        Usuario.apellido.label('apellido'),
                        Usuario.id.label('id'),
                        Usuario.id_persona_ext.label('id_persona_ext'),
                        Usuario.id_user_actualizacion.label('id_user_actualizacion'),
                        Usuario.fecha_actualizacion.label('fecha_actualizacion'))\
                        .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                        .join(Tarea, TareaAsignadaUsuario.id_tarea == Tarea.id)\
                        .filter(Tarea.id == tarea_id, TareaAsignadaUsuario.eliminado==False)\
                        .all()
    print("Usuarios por tarea:", usuarios)
    return usuarios

def delete_tarea(username=None, id_tarea=None):
    

    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")

    tarea = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()
    if tarea is not None:
        if tarea.eliminable==False:
              #print("Tarea no eliminable")
              raise Exception("Tarea no eliminable")
              
        tarea.eliminado=True
        tarea.fecha_eliminacion=datetime.now()
        tarea.id_user_actualizacion=id_user_actualizacion
        tarea.fecha_actualizacion=datetime.now()
        db.session.commit()
        return tarea
    
    else:
        #print("Tarea no encontrada")
        return None
    



