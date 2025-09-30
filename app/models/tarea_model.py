
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy import desc
from sqlalchemy import func, cast
from sqlalchemy.types import Boolean, TIMESTAMP
import uuid
from db.alchemy_db import db
from common.cache import *
from models.alch_model import Tarea, TipoTarea, TipoTareaDominio, LabelXTarea, Usuario, Nota, TareaAsignadaUsuario, Grupo, TareaXGrupo, UsuarioGrupo, Inhabilidad, SubtipoTarea, ExpedienteExt, ActuacionExt, URL
from models.alch_model import Auditoria_TareaAsignadaUsuario, Organismo, Dominio 
import common.functions as functions
import common.utils as utils
import common.logger_config as logger_config
import decorators.cache_error_wrapper as cache_error_wrapper
import common.cache as cache_common
import json
from datetime import date, time, datetime, timedelta


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
    logger_config.logger.info("calcula fecha vencimiento:" + str(fecha) + "-" + str(plazo))
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
    
    logger_config.logger.info("dias_vencimiento:" + str(dias_vencimiento) + "-" + str(fecha_vencimiento))
    return dias_vencimiento

def tareas_a_vencer(username=None, dias_aviso=None, grupos_usr=None):
    total = 0
    if username is not None:
        id_user = utils.get_username_id(username)

        if id_user is not None:
            utils.verifica_usr_id(id_user)
        else:
            raise Exception("Debe ingresar username o id_user_actualizacion")
    
    if dias_aviso is None:
        dias_aviso = 365  # Por defecto, 365 días de aviso

    # Consulta base con filtros comunes
    fecha_actual =datetime.combine(date.today(), time.min)  
    query = (db.session.query(Tarea)
            .filter(Tarea.fecha_fin >= fecha_actual,  # Solo tareas activas
                    Tarea.eliminado == False,
                    Tarea.estado != 3)).order_by(Tarea.fecha_fin)
    for tarea in query.all():
        print("Tarea:", tarea.id, "Fecha de inicio:", tarea.fecha_inicio, "Fecha fin:", tarea.fecha_fin)

    if grupos_usr is not None and grupos_usr=='true' or grupos_usr==True:
        logger_config.logger.info("tareas_a_vencer asignadas a los grupos del usuario")
        # Tareas asignadas a todos los grupos del usuario
        tareas = (query
                .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
                .join(Grupo, TareaXGrupo.id_grupo == Grupo.id)
                .join(UsuarioGrupo, Grupo.id == UsuarioGrupo.id_grupo)
                .filter(UsuarioGrupo.id_usuario == id_user,
                        UsuarioGrupo.eliminado == False).order_by(Tarea.fecha_fin).order_by(Tarea.fecha_fin)
                .all())
    else:
        # Tareas asignadas directamente al usuario
        logger_config.logger.info("tareas_a_vencer asignadas al usuario")
        logger_config.logger.info("id_user:" + str(id_user))
        tareas = (query
                .join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea)
                .filter(TareaAsignadaUsuario.id_usuario == id_user,
                        TareaAsignadaUsuario.eliminado == False).order_by(Tarea.fecha_fin)
                .all())    

    if tareas is not None:
        for tarea in tareas:
            print("Tarea:", tarea.id, "Fecha de inicio:", tarea.fecha_inicio, "Fecha fin:", tarea.fecha_fin)
        total = len(tareas)
        logger_config.logger.info("Cantidad de tareas_a_vencer:" + str(total))    

    #tareas_vencer = [tarea for tarea in tareas if calcular_dias_vencimiento(tarea.fecha_fin) <= dias_aviso]
    #calculo tareas por vencer
    tareas_vencer = []
    for tarea in tareas:
        dias_vencimiento = calcular_dias_vencimiento(tarea.fecha_fin)
        print("Fecha fin:", tarea.fecha_fin , "Dias vencimiento:", dias_vencimiento, "Dias aviso:", dias_aviso)
        if dias_vencimiento <= dias_aviso:
            """ tarea.dias_vencimiento = dias_vencimiento
            tarea.nombre_estado = nombre_estado(tarea.estado)
            tarea.nombre_prioridad = nombre_prioridad(tarea.prioridad) """
            tareas_vencer.append(tarea)
    
    
    total = len(tareas_vencer)
    return tareas_vencer, total


def insert_tarea(dominio=None, organismo=None, usr_header=None, id_grupo=None, prioridad=0, estado=1, id_actuacion=None, titulo='', cuerpo='', id_expediente=None, caratula_expediente='', nro_expte='', nombre_actuacion='', id_tipo_tarea=None, id_subtipo_tarea=None, eliminable=True, fecha_eliminacion=None, id_user_actualizacion=None, fecha_inicio=None, fecha_fin=None, plazo=0, usuario=None, grupo=None, username=None, url=None, url_descripcion=None, urls=None):
    
    print("##############Validaciones Insert de Tarea################")
    id_grupo=None
    id_usuario_asignado=None
    
    print("Usuario que crea la tarea: ", username)

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)
    else:
        if username is not None:
            logger_config.logger.info("verifying username: " + username)
            id_user_actualizacion = utils.get_username_id(username)
        else:
            logger_config.logger.error("Error en el ingreso de Usuario. Usuario no existente")
            raise Exception("Error en el ingreso de Usuario. Usuario no existente")  
          

    if id_expediente is not None:
        if not(functions.es_uuid(id_expediente)):
            raise Exception("El id del expediente debe ser un UUID: " + id_expediente)
        
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == id_expediente).first()

        if expediente is None:
            #Cuando viene del portal o de expedientes, se ingresa el id_ext
            logger_config.logger.info("Expediente no encontrado - Busca id_ext")
            expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id_ext == id_expediente).first()
            if expediente is None:
                logger_config.logger.info("Expediente no encontrado - Inserta expediente")
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
                logger_config.logger.info("Expediente encontrado - Update del expediente")
                if caratula_expediente is not None and caratula_expediente.strip() != "":
                    expediente.caratula = caratula_expediente
                if nro_expte is not None and nro_expte.strip() != "":    
                    expediente.nro_expte=nro_expte
                expediente.fecha_actualizacion = datetime.now()
                id_expediente = expediente.id

    if id_actuacion is not None:
        if not(functions.es_uuid(id_actuacion)):
            raise Exception("El id de la actuacion debe ser un UUID: " + id_actuacion)
        
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == id_actuacion).first()
        
        if actuacion is None:
            actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id_ext == id_actuacion).first()
            if actuacion is None:
                logger_config.logger.info("Actuacion no encontrada - Inserta actuacion")
                nuevoID_actuacion=uuid.uuid4()
                insert_actuacion = ActuacionExt(id=nuevoID_actuacion,
                                                id_ext=id_actuacion,
                                                nombre=nombre_actuacion,
                                                #id_tipo_actuacion=id_tipo_tarea,
                                                id_user_actualizacion=id_user_actualizacion,
                                                fecha_actualizacion=datetime.now())
                db.session.add(insert_actuacion)
                id_actuacion = nuevoID_actuacion
                logger_config.logger.info("actuacion insertada")
            else:
                logger_config.logger.info("Actuacion encontrada - Update de actuacion")
                if nombre_actuacion is not None and nombre_actuacion.strip() != "":
                    actuacion.nombre = nombre_actuacion
                    actuacion.id_user_actualizacion = id_user_actualizacion
                    actuacion.fecha_actualizacion = datetime.now()
                id_actuacion = actuacion.id

    if id_subtipo_tarea is not None:
        if not(functions.es_uuid(id_subtipo_tarea)):
            raise Exception("El id del subtipo de tarea debe ser un UUID: " + id_subtipo_tarea)
    logger_config.logger.info("CHEQUEA TIPO DE TAREA Y SUBTIPO DE TAREA")
    if id_tipo_tarea is not None:
        if not(functions.es_uuid(id_tipo_tarea)):
            raise Exception("El id del tipo de tarea debe ser un UUID: " + id_tipo_tarea)
        
        query_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea, TipoTarea.eliminado==False).first()
        if query_tipo_tarea is None:
            #Busco por id_ext
            print("id de tarea no encontrado - busco por id_ext")
            query_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id_ext == id_tipo_tarea, TipoTarea.eliminado==False).first()
            if query_tipo_tarea is None:
                logger_config.logger.error("Tipo de tarea no encontrado:%s" + id_tipo_tarea)
                print("Tipo de tarea no encontrado por id_ext - lo inserto")
                #raise Exception("Tipo de tarea no encontrado")
               
                #############################################################################################
                #######BORRAR - SOLO PARA PRUEBAS - SI NO EXISTE EL TIPO DE TAREA, CORRER FULL SYNC##########
                #############################################################################################
                 #agrego el tipo de tarea si no existe
                nuevoID_tipo_tarea=uuid.uuid4()
                nuevo_tipo_tarea = TipoTarea(id=nuevoID_tipo_tarea,
                                               id_ext=id_tipo_tarea,
                                               nombre=titulo,
                                               codigo_humano=titulo.lower().replace(" ", "_"),
                                               nivel='expte',
                                               origen_externo=True,
                                               fecha_actualizacion=datetime.now(),
                                               id_user_actualizacion=id_user_actualizacion)
                db.session.add(nuevo_tipo_tarea)
                
                #Agrego el dominio en TipoTareaDominio
                nuevo_tipo_tarea_dominio = TipoTareaDominio(id=uuid.uuid4(),
                                                             id_tipo_tarea=nuevoID_tipo_tarea,
                                                             id_dominio_ext=dominio,
                                                             id_organismo_ext=organismo,
                                                             fecha_actualizacion=datetime.now(),
                                                             id_user_actualizacion=id_user_actualizacion)
                db.session.add(nuevo_tipo_tarea_dominio)

                logger_config.logger.info("tipo de tarea insertada")
                db.session.commit()
            else:
                print("Tipo de tarea encontrado por id_ext", query_tipo_tarea.id)
            

        nombre_tipo=query_tipo_tarea.nombre
        id_tipo_tarea = query_tipo_tarea.id
        if id_subtipo_tarea is not None:
            subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.eliminado==False).first()
            if subtipo_tarea is None:
                logger_config.logger.error("Subtipo de tarea no encontrado")
                raise Exception("Subtipo de tarea no encontrado")
            nombre_subtipo = subtipo_tarea.nombre
            subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.id_tipo == id_tipo_tarea).first()
            if subtipo_tarea is None:
                logger_config.logger.error("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
    else:
        if id_subtipo_tarea is not None:
            logger_config.logger.error("Debe ingresar el tipo de tarea")
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
        
        
    fecha_inicio = functions.controla_fecha(fecha_inicio)
    if fecha_inicio < datetime.now().date():
        raise Exception("La fecha de inicio no puede ser menor a la fecha actual")

    if fecha_fin is not None:
        fecha_fin = functions.controla_fecha(fecha_fin)
        if fecha_fin < fecha_inicio:
            raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin")
        if fecha_fin < datetime.now().date():
            raise Exception("La fecha de fin no puede ser menor la fecha actual")


    if plazo>0:
        query_inhabilidad = db.session.query(Inhabilidad).all()
        if len(query_inhabilidad)>0:  
            #fecha_inicio = fecha_inicio + " 23:59:59"     
            query_inhabilidad = db.session.query(Inhabilidad).filter(Inhabilidad.fecha_desde <= fecha_inicio, Inhabilidad.fecha_hasta >= fecha_inicio).all()
            if query_inhabilidad is not None:
                for row in query_inhabilidad:
                    plazo=plazo+1
        fecha_fin = calcular_fecha_vencimiento(fecha_inicio, plazo)


    print("DATES FORMATS TO BE INSERTED")
    print("fecha_inicio:", fecha_inicio)
    print("fecha_fin:", fecha_fin)
    print("fecha_creacion:", datetime.now())
    nuevoID_tarea=uuid.uuid4()
    print("DATE DEBUG")
    print("datetime.now():", datetime.now())
    print("fecha_inicio:", fecha_inicio)
    print("fecha_fin:", fecha_fin)
    if not eliminable:
        eliminable = True 

    nueva_tarea = Tarea(
        id=nuevoID_tarea,
        prioridad=prioridad,
        estado=estado,
        id_actuacion=id_actuacion,
        titulo=titulo,
        cuerpo=cuerpo,
        id_expediente=id_expediente,
        caratula_expediente=caratula_expediente if caratula_expediente is not None and caratula_expediente.strip() != "" else None,
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

    #Inserto las urls
    if urls is not None and len(urls)>0:
        for url_item in urls:
            url=url_item.get('url', None)
            url_descripcion=url_item.get('descripcion', None)
            if url is not None and url.strip() != "":
                nuevo_url = URL(
                    id=uuid.uuid4(),
                    id_tarea=nuevoID_tarea,
                    url=url,
                    descripcion=url_descripcion if url_descripcion is not None and url_descripcion.strip() != "" else None,
                    fecha_actualizacion=datetime.now(),
                    id_user_actualizacion=id_user_actualizacion
                )

                db.session.add(nuevo_url)
    """ if url is not None and url.strip() != "":
      
        nuevo_url = URL(
            id=uuid.uuid4(),
            id_tarea=nuevoID_tarea,
            url=url,
            descripcion=url_descripcion if url_descripcion is not None and url_descripcion.strip() != "" else None,
            fecha_actualizacion=datetime.now(),
            id_user_actualizacion=id_user_actualizacion
        )

        db.session.add(nuevo_url) """

    usuariosxdefault = []

    if grupo is not None:
        for group in grupo:
            id_grupo=group['id_grupo']
            if not(functions.es_uuid(id_grupo)):
                raise Exception("El id del grupo debe ser un UUID: " + id_grupo)
            
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == id_grupo, Grupo.eliminado==False).first()
            if existe_grupo is None:
                # Busco el id_organismo 
                existe_grupo = db.session.query(Grupo).filter(Grupo.id_organismo_ext == id_grupo, Grupo.eliminado==False, Grupo.base==True).first()
                if existe_grupo is None:
                    logger_config.logger.error("Grupo y organismo no encontrado")
                    raise Exception("Error en el ingreso de grupos. Grupo no existente")
                else:
                    id_grupo=existe_grupo.id
                    logger_config.logger.info("Grupo encontrado por id_organismo") 

            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))
            
            if existe_grupo.suspendido==True:
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            usuario_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id_user_actualizacion, UsuarioGrupo.id_grupo == id_grupo, UsuarioGrupo.eliminado==False).first()
            if usuario_grupo is None:
                logger_config.logger.error("Error en el ingreso de Usuario. El usuario que crea la tarea no pertenece al grupo ingresado")
                raise Exception("Error en el ingreso de Usuario. El usuario que crea la tarea no pertenece al grupo ingresado")
            
            id_usuario_asignado = existe_grupo.id_user_asignado_default
            usuariosxdefault.append(id_usuario_asignado)
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
        logger_config.logger.error("Debe ingresar al menos un grupo")
        raise Exception ("Debe ingresar al menos un grupo")
        
    #Asigna el grupo del usuario que crea la tarea por defecto
 
    if usuario is not None:
        for user in usuario:
            id_usuario = user['id_usuario']
            if not(functions.es_uuid(id_usuario)):
                raise Exception("El id del usuario debe ser un UUID: " + id_usuario)
            existe_usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario, Usuario.eliminado==False).first()
            if existe_usuario is None:
                logger_config.logger.error("Error en el ingreso de Usuario. Usuario no existente")
                raise Exception("Error en el ingreso de Usuario. Usuario no existente")
            
            if existe_usuario.eliminado==True:
                logger_config.logger.error("Error en el ingreso de Usuario. Usuario eliminado")
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
        

    #Asignno la tarea a los usuarios por defecto de cada grupo ingresado
    if len(usuariosxdefault)> 0:
        for id_usuario_asignado in usuariosxdefault:    
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

def undelete_tarea(id_t='', usr_header=None, **kwargs):
    ################################

    if id_t is None:
        raise Exception("Debe ingresar el id de la tarea a modificar")
    if not(functions.es_uuid(id_t)):
        raise Exception("El id de la tarea debe ser un UUID: " + id_t)
    
    tarea = db.session.query(Tarea).filter(Tarea.id == id_t, Tarea.eliminado==True).first()

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
        else:
            raise Exception("Debe ingresar username o id_user_actualizacion")

    if tarea is None:
        raise Exception("Tarea no encontrada o no eliminada")
    
    tarea.eliminado = False
    #tarea.fecha_eliminacion = None
    tarea.id_user_actualizacion = id_user_actualizacion
    tarea.fecha_actualizacion = datetime.now()
    
    db.session.commit()
    return tarea

def update_tarea(id_t='', usr_header=None, **kwargs):
    ################################

    if id_t is None:
        raise Exception("Debe ingresar el id de la tarea a modificar")
    if not(functions.es_uuid(id_t)):
        raise Exception("El id de la tarea debe ser un UUID: " + id_t)
    
    tarea = db.session.query(Tarea).filter(Tarea.id == id_t, Tarea.eliminado==False).first()

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                utils.verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
            
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")

    if tarea is None:
        return None
    if 'cuerpo' in kwargs:
        tarea.cuerpo = kwargs['cuerpo']
    if 'eliminable' in kwargs:
        tarea.eliminable = kwargs['eliminable']
    else:
        tarea.eliminable = True    
    if 'id_actuacion' in kwargs:
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == kwargs['id_actuacion']).first()
        if actuacion is None:
            actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id_ext == kwargs['id_actuacion']).first()
            if actuacion is None:
                raise Exception("Actuacion no encontrada")
            if 'nombre_actuacion' in kwargs:
                actuacion.nombre = kwargs['nombre_actuacion']

        tarea.id_actuacion = kwargs['id_actuacion']
        
    if 'id_expediente' in kwargs:
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == kwargs['id_expediente']).first()
        
        if expediente is None:
            expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id_ext == kwargs['id_expediente']).first()
            if expediente is None:
                raise Exception("Expediente no encontrado")

        # Siempre asigno el id una vez encontrado
        id_expediente = expediente.id

        if 'caratula_expediente' in kwargs:
            expediente.caratula = kwargs['caratula_expediente']  
        if 'nro_expte' in kwargs:
            expediente.nro_expte = kwargs['nro_expte']

        tarea.id_expediente = id_expediente

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
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.id_tipo == kwargs['id_tipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
           
            tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
            tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']
        #no se ingreso subtipo de tarea, verifico con el subtipo actual
        else:
            #Modifico tipo tarea, borro el subtipo que tenía antes
            if tarea.subtipo_tarea is not None:
                #verifico que el subtipo de tarea actual corresponda al tipo de tarea ingresado
                #subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == tarea.id_subtipo_tarea, SubtipoTarea.id_tipo==kwargs['id_tipo_tarea'], SubtipoTarea.eliminado==False).first()
                #if subtipo is None:
                #    raise Exception("El tipo de tarea '" + nombre_tipo + "' no se corresponde al subtipo de tarea actual")
                tarea.id_subtipo_tarea = None
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
        plazo = kwargs['plazo']
        tarea.plazo = kwargs['plazo']
    if 'prioridad' in kwargs:
        tarea.prioridad = kwargs['prioridad']
    if 'estado' in kwargs:
        tarea.estado = kwargs['estado']    
    if 'titulo' in kwargs:
        tarea.titulo = kwargs['titulo'].upper() 
    ####CONTROLES DE FECHAS DE INICIO Y FIN SI SE INGRESA UNA DE LAS DOS , O LAS DOS ###########    
    if 'fecha_inicio' in kwargs:
        fecha_inicio = functions.controla_fecha(kwargs['fecha_inicio'])
        #fecha_inicio = datetime.strptime(kwargs['fecha_inicio'], "%d/%m/%Y").replace(hour=0, minute=0, second=0, microsecond=0)
        #fecha_inicio = datetime.strptime(kwargs['fecha_inicio'], "%d/%m/%Y").date()
        if fecha_inicio < datetime.now().date():
            raise Exception("La fecha de inicio no puede ser menor a la fecha actual")  
        tarea.fecha_inicio = fecha_inicio
    else:
        fecha_inicio = None

    if 'fecha_fin' in kwargs:
        fecha_fin = functions.controla_fecha(kwargs['fecha_fin'])
        #fecha_fin = datetime.strptime(kwargs['fecha_fin'], "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
        #fecha_fin = datetime.strptime(kwargs['fecha_fin'], "%d/%m/%Y").date()
        if fecha_fin < datetime.now().date():
            raise Exception("La fecha de fin no puede ser menor a la fecha actual")
        tarea.fecha_fin = fecha_fin     
    else:
        fecha_fin = None       
    
    if fecha_inicio is not None and fecha_fin is not None:
        if fecha_inicio > fecha_fin:
            raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin")
        else:
            tarea.fecha_inicio = fecha_inicio
            tarea.fecha_fin = fecha_fin
    if fecha_inicio is not None and fecha_fin is None:        
        #Si no se ingreso fecha fin, calculo la fecha fin
        if 'plazo' in kwargs and kwargs['plazo'] > 0:
            tarea.fecha_fin = calcular_fecha_vencimiento(fecha_inicio, kwargs['plazo'])
        else:
            #compara con la fecha fin actual
            print("Compara con la fecha fin actual")
            if fecha_inicio > tarea.fecha_fin.date():
                raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin actual")
    if fecha_inicio is None and fecha_fin is not None:
        #Si no se ingreso fecha inicio, calculo la fecha inicio
        if 'plazo' in kwargs and kwargs['plazo'] > 0:
            tarea.fecha_fin = calcular_fecha_vencimiento(fecha_fin, -kwargs['plazo'])
        else:
            if tarea.fecha_inicio.date() > fecha_fin:
                raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin actual")


    tarea.id_user_actualizacion = id_user_actualizacion  
    tarea.fecha_actualizacion = datetime.now()

    #Inserto las urls
    if 'urls' in kwargs and kwargs['urls'] is not None and len(kwargs['urls'])>0:
        for url_item in kwargs['urls']:
            url=url_item.get('url', None)
            url_descripcion=url_item.get('descripcion', None)
            if url is not None and url.strip() != "":
                nuevo_url = URL(
                    id=uuid.uuid4(),
                    id_tarea=id_t,
                    url=url,
                    descripcion=url_descripcion if url_descripcion is not None and url_descripcion.strip() != "" else None,
                    fecha_actualizacion=datetime.now(),
                    id_user_actualizacion=id_user_actualizacion
                )

                db.session.add(nuevo_url)

    
    usuarios=[]
    grupos=[]
    if 'grupo' in kwargs:
        #elimino los grupos existentes para esa tarea 
        grupo_tarea=db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_t)

        for grupo in grupo_tarea:
            print("Encuentra grupo y lo borra:", grupo.id_grupo)
            grupo.eliminado=True
            grupo.fecha_actualizacion=datetime.now()
            grupo.id_user_actualizacion=id_user_actualizacion

        #controlo que el grupo exista y lo asocio a la tarea
        for group in kwargs['grupo']:
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                logger_config.logger.error("Grupo no encontrado")
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                logger_config.logger.error("Grupo eliminado")
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            if existe_grupo.suspendido==True:
                logger_config.logger.error("Grupo suspendido")
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            nuevoID=uuid.uuid4()
            tareaxgrupo = db.session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id_t, TareaXGrupo.id_grupo==group['id_grupo']).first()
            if tareaxgrupo is not None:
                tareaxgrupo.eliminado=True
                tareaxgrupo.fecha_actualizacion=datetime.now()
                tareaxgrupo.fecha_actualizacion=datetime.now()
                tareaxgrupo.id_user_actualizacion=id_user_actualizacion
            
            nuevo_tarea_grupo = TareaXGrupo(
                id=nuevoID,
                id_grupo=group['id_grupo'],
                id_tarea=id_t,
                id_user_actualizacion= id_user_actualizacion,
                fecha_asignacion=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
            
            db.session.add(nuevo_tarea_grupo)
            """ if tareaxgrupo is None:
                nuevo_tarea_grupo = TareaXGrupo(
                    id=nuevoID,
                    id_grupo=group['id_grupo'],
                    id_tarea=id_t,
                    id_user_actualizacion= id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now()
                )
                
                db.session.add(nuevo_tarea_grupo)
            else:
                #print("Reactiva grupo")
                if tareaxgrupo.eliminado==True:
                    tareaxgrupo.eliminado=False
                    tareaxgrupo.fecha_actualizacion=datetime.now()
                    tareaxgrupo.fecha_actualizacion=datetime.now()
                    tareaxgrupo.id_user_actualizacion=id_user_actualizacion  """  

    res_grupos = db.session.query(Grupo.id, Grupo.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                  ).join(TareaXGrupo, Grupo.id==TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea== id_t).order_by(TareaXGrupo.eliminado).all()


    if res_grupos is not None:
        for row in res_grupos:
            grupo = {
                "id_grupo": row.id,
                "nombre": row.nombre,
                "asignada": not(row.reasignada),
                "fecha_asignacion": row.fecha_asignacion
            }
            
            grupos.append(grupo)        

    if 'usuario' in kwargs:
        #elimino los usuarios existentes para esa tarea
        usuarios_tarea=db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_t)
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
            asigna_usuario = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id_t, TareaAsignadaUsuario.id_usuario==user['id_usuario']).first()
            if asigna_usuario is None:
                nuevo_asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=id_t,
                    id_usuario=user['id_usuario'],
                    id_user_actualizacion= id_user_actualizacion,
                    fecha_asignacion=datetime.now(),
                    fecha_actualizacion=datetime.now(),
                    eliminado = False
                )
                db.session.add(nuevo_asigna_usuario)
            else:
                #si el usuario ya tuvo la tarea reasigno el usuario
                if asigna_usuario.eliminado==True:
                    asigna_usuario.eliminado=False
                    asigna_usuario.fecha_actualizacion=datetime.now()
                    asigna_usuario.fecha_actualizacion=datetime.now()
                    asigna_usuario.id_user_actualizacion=id_user_actualizacion

    res_usuarios = db.session.query(Usuario.id, Usuario.nombre, Usuario.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                  ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== id_t).order_by(TareaAsignadaUsuario.eliminado).all()                
                                  
    if res_usuarios is not None:
        for row in res_usuarios:
            usuario = {
                "id_usuario": row.id,
                "nombre": row.nombre,
                "apellido": row.apellido,
                "asignada": not(row.reasignada),
                "fecha_asignacion": row.fecha_asignacion
            }
            usuarios.append(usuario)
    url = []
    res_url = db.session.query(URL).filter(URL.id_tarea == tarea.id).all()
    if res_url is not None:
            for row in res_url:
                url.append({
                    "id": row.id,
                    "url": row.url,
                    "descripcion": row.descripcion
                })

    editable_externo = False
    res_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == tarea.id_tipo_tarea).first()
    if res_tipo_tarea is not None:
        if res_tipo_tarea.origen_externo==True and res_tipo_tarea.nivel != 'int':
            editable_externo = True

    ###################Formatear el resultado####################
    prioridad = {"id": tarea.prioridad, "descripcion": nombre_prioridad(tarea.prioridad)}
    estado = {"id": tarea.estado, "descripcion": nombre_estado(tarea.estado)}
    result = {
        "id": tarea.id,
        "titulo": tarea.titulo,
        "fecha_inicio": tarea.fecha_inicio,
        "fecha_fin": tarea.fecha_fin,
        "plazo": tarea.plazo,
        "prioridad": prioridad,
        "estado": estado,
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
        "usuario": usuarios,
        "url": url,
        "editable_externo": editable_externo
    }

    db.session.commit()
    return result

def update_lote_tareas_v2(usr_header=None, **kwargs):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)
        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                if not(functions.es_uuid(kwargs['id_user_actualizacion'])):
                    raise Exception("El id_user_actualizacion debe ser un UUID: " + kwargs['id_user_actualizacion'])
                utils.verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if 'upd_tarea' in kwargs:
        upd_tarea = kwargs['upd_tarea']
        datos = []
        datos_error = []
        for tareas_update in upd_tarea:
           if not(functions.es_uuid(tareas_update['id_tarea'])):
               raise Exception("El id de la tarea debe ser un UUID: " + tareas_update['id_tarea'])
           resp = update_tarea(tareas_update['id_tarea'], username, **tareas_update)
           if resp is None:
                datos_error.append("Tarea no procesada:"+tareas_update['id_tarea'])
               
           datos.append(resp)

    result = {
        "tareas_error": datos_error,
        "tareas_ok": datos
    }

    return result

# def update_lote_tareas_v22(username=None, **kwargs):
    
#     if username is not None:
#         id_user_actualizacion = utils.get_username_id(username)
#         if id_user_actualizacion is not None:
#             utils.verifica_usr_id(id_user_actualizacion)
#         else:
#             if 'id_user_actualizacion' in kwargs:
#                 utils.verifica_usr_id(kwargs['id_user_actualizacion'])
#                 id_user_actualizacion = kwargs['id_user_actualizacion']
              
#             else:
#                 raise Exception("Debe ingresar username o id_user_actualizacion")
            
#     if 'upd_tarea' in kwargs:
#         upd_tarea = kwargs['upd_tarea']
#         datos = []
#         datos_error = []
#         for tareas_update in upd_tarea:
#            resp = update_tarea(tareas_update['id_tarea'], username, **tareas_update)
#            if resp is None:
#                 datos_error.append("Tarea no procesada:"+tareas_update['id_tarea'])
               
#            datos.append(resp)

#     result = {
#         "tareas_error": datos_error,
#         "tareas_ok": datos
#     }

#     return result

def update_lote_tareas(usr_header=None, **kwargs):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)
        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
        else:
            if 'id_user_actualizacion' in kwargs:
                if not(functions.es_uuid(kwargs['id_user_actualizacion'])):
                    raise Exception("El id_user_actualizacion debe ser un UUID")
                utils.verifica_usr_id(kwargs['id_user_actualizacion'])
                id_user_actualizacion = kwargs['id_user_actualizacion']
              
            else:
                raise Exception("Debe ingresar username o id_user_actualizacion")
            
    if 'id_actuacion' in kwargs:
        if not(functions.es_uuid(kwargs['id_actuacion'])):
            raise Exception("El id_actuacion debe ser un UUID")
        actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == kwargs['id_actuacion']).first()
        if actuacion is None:
            raise Exception("Actuacion no encontrada")
        
    if 'id_expediente' in kwargs:
        if not(functions.es_uuid(kwargs['id_expediente'])):
            raise Exception("El id_expediente debe ser un UUID")
        expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == kwargs['id_expediente']).first()
        if expediente is None:
            raise Exception("Expediente no encontrado")
        
    if 'id_tipo_tarea' in kwargs:
        if not(functions.es_uuid(kwargs['id_tipo_tarea'])):
            raise Exception("El id_tipo_tarea debe ser un UUID")
        tipo = db.session.query(TipoTarea).filter(TipoTarea.id == kwargs['id_tipo_tarea'], TipoTarea.eliminado==False).first()
        if tipo is  None:
            raise Exception("Tipo de tarea no encontrado")
                     
        if 'id_subtipo_tarea' in kwargs:
            if not(functions.es_uuid(kwargs['id_subtipo_tarea'])):
                raise Exception("El id_subtipo_tarea debe ser un UUID")
            subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            else:
                subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.id_tipo == kwargs['id_tipo_tarea']).first()
                if subtipo is None:
                    raise Exception("El tipo de tarea y el subtipo de tarea no se corresponden")
    if 'grupo' in kwargs:
        for group in kwargs['grupo']:
            if not(functions.es_uuid(group['id_grupo'])):
                raise Exception("El id_grupo debe ser un UUID:" + group['id_grupo'])
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                logger_config.logger.error("Grupo no encontrado")
                raise Exception("Error en el ingreso de grupos. Grupo no existente: ") + group['id_grupo']
            
            if existe_grupo.eliminado==True:
                logger_config.logger.error("Grupo eliminado")
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))

            if existe_grupo.suspendido==True:
                logger_config.logger.error("Grupo suspendido")
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre + '-id:' + str(existe_grupo.id))
    if 'usuario' in kwargs:
        for user in kwargs['usuario']:
            if not(functions.es_uuid(user['id_usuario'])):
                raise Exception("El id_usuario debe ser un UUID: " + user['id_usuario'])
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
                if not(functions.es_uuid(tareas_update['id'])):
                    raise Exception("El id de la tarea debe ser un UUID: " + tareas_update['id'])
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
                    if 'cuerpo' in kwargs:
                        tarea.cuerpo = kwargs['cuerpo']
                    if 'eliminable' in kwargs:
                        tarea.eliminable = kwargs['eliminable']
                    if 'id_actuacion' in kwargs:
                        tarea.id_actuacion = kwargs['id_actuacion']
                    if 'id_expediente' in kwargs:
                        tarea.id_expediente = kwargs['id_expediente'] 
                    if 'plazo' in kwargs:
                        tarea.plazo = kwargs['plazo']
                    if 'prioridad' in kwargs:
                        tarea.prioridad = kwargs['prioridad']
                    if 'estado' in kwargs:
                        tarea.estado = kwargs['estado']    
                    if 'titulo' in kwargs:
                        tarea.titulo = kwargs['titulo']
                    #Validacion de tipo y subtipo de tarea
                    if 'id_tipo_tarea' in kwargs:
                        tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
                    if 'id_subtipo_tarea' in kwargs:
                        tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']
                    if 'fecha_inicio' in kwargs:
                        fecha_inicio = functions.controla_fecha(kwargs['fecha_inicio'])
                        fecha_inicio = datetime.strptime(kwargs['fecha_inicio'], "%d/%m/%Y").date()
                        if fecha_inicio < datetime.now().date():
                            raise Exception("La fecha de inicio no puede ser menor a la fecha actual")  
                        tarea.fecha_inicio = fecha_inicio    
                    if 'fecha_fin' in kwargs:
                        fecha_fin = functions.controla_fecha(kwargs['fecha_fin'])
                        fecha_fin = datetime.strptime(kwargs['fecha_fin'], "%d/%m/%Y").date()
                        if fecha_fin < datetime.now().date():
                            raise Exception("La fecha de fin no puede ser menor  a la fecha actual")
                        tarea.fecha_fin = fecha_fin

                 
                    tarea.id_user_actualizacion = id_user_actualizacion  
                    tarea.fecha_actualizacion = datetime.now()
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

#@cache.cached(CACHE_TIMEOUT_LONG)
def get_all_tipo_tarea(page=1, per_page=10, nivel=None, origen_externo=None, suspendido=None, eliminado=None, nombre=None, id_dominio=None, id_organismo=None, dominio=None, organismo=None, clasificacion_ext=None):

    query = db.session.query(TipoTarea.base,
                            TipoTarea.id,
                            TipoTarea.codigo_humano,
                            TipoTarea.clasificacion_ext,
                            TipoTarea.nombre,
                            TipoTarea.nivel,
                            TipoTarea.origen_externo,
                            TipoTarea.suspendido,
                            TipoTarea.eliminado,
                            TipoTarea.id_ext,
                            TipoTarea.id_user_actualizacion,
                            TipoTarea.fecha_actualizacion,
                            TipoTareaDominio.id_dominio_ext.label('id_dominio'),
                            TipoTareaDominio.id_organismo_ext.label('id_organismo')
                            ).outerjoin(TipoTareaDominio, TipoTarea.id == TipoTareaDominio.id_tipo_tarea
                            ).filter(TipoTarea.eliminado == False).order_by(TipoTarea.nombre)
     
    if id_dominio is not None:
        if(not(functions.es_uuid(id_dominio))):
                raise Exception("El id_dominio debe ser un UUID")
        
        query = query.filter(TipoTareaDominio.id_dominio_ext == id_dominio)

    if id_organismo is not None:
        if(not(functions.es_uuid(id_organismo))):
            raise Exception("El id_organismo debe ser un UUID")

        query = query.filter(TipoTareaDominio.id_organismo_ext == id_organismo)

    #query = db.session.query(TipoTarea).order_by(TipoTarea.nombre)
    if nivel is not None:
        query = query.filter(TipoTarea.nivel == nivel)
    if origen_externo is not None:
        query = query.filter(TipoTarea.origen_externo == origen_externo)
    if suspendido is not None:
        query = query.filter(TipoTarea.suspendido == suspendido)
    if eliminado is not None:
        query = query.filter(TipoTarea.eliminado == eliminado)
    if nombre:
        query = query.filter(TipoTarea.nombre.ilike(f"%{nombre}%"))

    if clasificacion_ext is not None:
        query = query.filter(TipoTarea.clasificacion_ext.ilike(f"%{clasificacion_ext}%"))


    total= query.count()
    res = query.order_by(TipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    #res = db.session.query(TipoTarea).order_by(TipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    
    if res is not None:
        tipo_list = []
        #Busco los subtipo de tarea asociados a cada tipo de tarea
        for tipo in res:
            query_subtipo = db.session.query(SubtipoTarea).filter(SubtipoTarea.id_tipo == tipo.id, SubtipoTarea.eliminado==False).order_by(SubtipoTarea.nombre).all()
            #Agrego los subtipos al array subtipos
            subtipo_list = []
            if query_subtipo is not None:
                for subtipo in query_subtipo:
                    subtipo = {
                        "id": subtipo.id,
                        "id_ext": subtipo.id_ext,
                        "nombre": subtipo.nombre,
                        "nombre_corto": subtipo.nombre_corto,
                        "base": subtipo.base,
                        "origen_externo": subtipo.origen_externo,
                        "suspendido": subtipo.suspendido,
                        "eliminado": subtipo.eliminado
                      
                    }
                    subtipo_list.append(subtipo)

            #Formateo el resultado
            tipo_tarea = {
                "id": tipo.id,
                "codigo_humano": tipo.codigo_humano,
                "clasificacion_ext": tipo.clasificacion_ext,
                "nombre": tipo.nombre,
                "base": tipo.base,
                "origen_externo": tipo.origen_externo,
                "subtipo_tarea": subtipo_list,
                "id_user_actualizacion": tipo.id_user_actualizacion,
                #"user_actualizacion": tipo.user_actualizacion,
                "fecha_actualizacion": tipo.fecha_actualizacion,
                "suspendido": tipo.suspendido,
                "eliminado": tipo.eliminado,
                "nivel": tipo.nivel,
                "id_ext": tipo.id_ext,
                "id_dominio": tipo.id_dominio,
                "id_organismo": tipo.id_organismo
            }
            tipo_list.append(tipo_tarea)

    #paginacion del resultado

    return tipo_list, total

def insert_tipo_tarea(usr_header=None, dominio=None, organismo=None, id='', codigo_humano='', nombre='', id_user_actualizacion='', base=False, suspendido=False, eliminado=False, id_organismo=None, nivel=None):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
           
    if id_organismo is None:
       
       id_organismo = organismo
    else:
        if not(functions.es_uuid(id_organismo)):
            raise Exception("El id_organismo debe ser un UUID")
        
        query_organismo = db.session.query(Organismo).filter(Organismo.id_organismo_ext == id_organismo, Organismo.eliminado==False).first()
        if query_organismo is None:
            raise Exception("Organismo no encontrado")
        if dominio is None:
            dominio = query_organismo.id_dominio_ext

        id_organismo = query_organismo.id_organismo_ext
        
        query_dominio = db.session.query(Dominio).filter(Dominio.id_dominio_ext == dominio, Dominio.eliminado==False).first()
        
        if query_dominio is None:
            raise Exception("Dominio no encontrado")
        if query_organismo.id_dominio_ext != query_dominio.id_dominio_ext:
            raise Exception("El organismo ingresado no corresponde al dominio actual")
        


    nuevoID=uuid.uuid4()

    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
        nivel='int',
        base= base,
        origen_externo=False,
        suspendido=suspendido,
        eliminado=eliminado,
        #id_dominio=dominio,
        #id_organismo=id_organismo_tipo,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_tipo_tarea)

    nuevo_tipo_tarea_dominio = TipoTareaDominio(
        id=uuid.uuid4(),
        id_tipo_tarea=nuevoID,
        id_dominio_ext=dominio,
        id_organismo_ext=id_organismo,
        eliminado=False,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_tipo_tarea_dominio)

    db.session.commit()

    query_tipo_tarea = db.session.query(TipoTarea.id, TipoTarea.codigo_humano, TipoTarea.nombre, TipoTarea.nivel, TipoTarea.base, TipoTarea.origen_externo, TipoTarea.suspendido, TipoTarea.eliminado, TipoTarea.id_ext, TipoTarea.id_user_actualizacion, TipoTarea.fecha_actualizacion,
                                        TipoTareaDominio.id_dominio_ext.label("id_dominio"), TipoTareaDominio.id_organismo_ext.label("id_organismo")).join(TipoTareaDominio).filter(TipoTareaDominio.id_tipo_tarea==TipoTarea.id, TipoTarea.id == nuevoID).first()

    return query_tipo_tarea


def update_tipo_tarea(usr_header=None, id_tipo_tarea='', **kwargs):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")

    tipo_tarea = db.session.query(TipoTarea).filter(
        TipoTarea.id == id_tipo_tarea,
        TipoTarea.eliminado == False
        ).first()

    if not tipo_tarea:
        raise Exception("Tipo de tarea no encontrado")

    # Validar que organismo y dominio se correspondan
    # Determinar valores finales de dominio y organismo (ingresados o actuales)
    if 'id_dominio' in kwargs:
        if not(functions.es_uuid(kwargs['id_dominio'])):
            raise Exception("El id_dominio debe ser un UUID")
    if 'id_organismo' in kwargs:
        if not(functions.es_uuid(kwargs['id_organismo'])):
            raise Exception("El id_organismo debe ser un UUID")

    id_dominio_final = kwargs.get('id_dominio', tipo_tarea.id_dominio_ext)
    id_organismo_final = kwargs.get('id_organismo', tipo_tarea.id_organismo_ext)

    # Validar dominio si existe
    dominio = None
    if 'id_dominio' in kwargs:
        dominio = db.session.query(Dominio).filter(
            Dominio.id_dominio_ext == kwargs['id_dominio'],
            Dominio.eliminado == False
        ).first()
        if dominio is None:
            raise Exception("Dominio no encontrado")

    # Validar organismo si existe
    organismo = None
    id_dominio_final = None
    id_organismo_final = None
    if 'id_organismo' in kwargs:
        organismo = db.session.query(Organismo).filter(
            Organismo.id_organismo_ext == kwargs['id_organismo'],
            Organismo.eliminado == False
        ).first()
        if organismo is None:
            raise Exception("Organismo no encontrado")
        id_organismo_final = kwargs['id_organismo']

    # Validar relación solo si tenemos ambos
    if dominio and organismo:
        if organismo.id_dominio_ext != dominio.id_dominio_ext:
            raise Exception("Dominio y Organismo no corresponden")

    # Asignar cambios
    if 'id_dominio' in kwargs:
        id_dominio_final = kwargs['id_dominio']
        query_tipo_tarea_dominio = db.session.query(TipoTareaDominio).filter( 
            TipoTareaDominio.id_tipo_tarea == id_tipo_tarea,
            TipoTareaDominio.id_dominio_ext == kwargs['id_dominio'],
            TipoTareaDominio.eliminado == False
        ).first()
        if query_tipo_tarea_dominio is None:
            # Si no existe la relación, crearla
            nuevo_tipo_tareaxdominio = TipoTareaDominio(
                id=uuid.uuid4(),
                id_tipo_tarea=id_tipo_tarea,
                id_dominio_ext=kwargs['id_dominio'],
                id_organismo_ext=id_organismo_final,
                eliminado=False,
                id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )
            db.session.add(nuevo_tipo_tareaxdominio)
        #tipo_tarea.id_dominio = kwargs['id_dominio']

    if 'id_organismo' in kwargs:
        #tipo_tarea.id_organismo = kwargs['id_organismo']
        if id_dominio_final is None:
            query_organismo = db.session.query(Organismo).filter(
                Organismo.id_organismo_ext == kwargs['id_organismo'],
                Organismo.eliminado == False
            ).first()
            if query_organismo:
                query_dominio = db.session.query(Dominio).filter(
                    Dominio.id_dominio_ext == query_organismo.id_dominio_ext,
                    Dominio.eliminado == False
                ).first()
                if query_dominio is not None:
                    id_dominio_final = query_dominio.id_dominio_ext
                    #tipo_tarea.id_dominio = query_dominio.id
                query_tipo_tarea_dominio = db.session.query(TipoTareaDominio).filter( 
                        TipoTareaDominio.id_tipo_tarea == id_tipo_tarea,
                        TipoTareaDominio.id_dominio_ext == kwargs['id_dominio'],
                        TipoTareaDominio.eliminado == False
                    ).first()
                if query_tipo_tarea_dominio is None:
                    # Si no existe la relación, crearla
                    nuevo_tipo_tareaxdominio = TipoTareaDominio(
                        id=uuid.uuid4(),
                        id_tipo_tarea=id_tipo_tarea,
                        id_dominio_ext=kwargs['id_dominio'],
                        id_organismo_ext=id_organismo_final,
                        eliminado=False,
                        id_user_actualizacion=id_user_actualizacion,
                        fecha_actualizacion=datetime.now()
                    )
                    db.session.add(nuevo_tipo_tareaxdominio)    

    if tipo_tarea.suspendido == True:
        if 'suspendido' in kwargs:
            tipo_tarea.suspendido = kwargs['suspendido']
        else:
            raise Exception("Tipo de tarea suspendido, no se puede modificar")    

    if 'codigo_humano' in kwargs:
        tipo_tarea.codigo_humano = kwargs['codigo_humano']
    if 'nombre' in kwargs:
        tipo_tarea.nombre = kwargs['nombre']
    if 'nivel' in kwargs:
        tipo_tarea.nivel = kwargs['nivel']
    if 'id_ext' in kwargs:
        tipo_tarea.id_ext = kwargs['id_ext'] 
    if 'suspendido' in kwargs:
        tipo_tarea.suspendido = kwargs['suspendido'] 
    if 'eliminado' in kwargs:
        tipo_tarea.eliminado = kwargs['eliminado']            
    if 'base' in kwargs:
        tipo_tarea.base =kwargs['base']
    tipo_tarea.origen_externo = False
    tipo_tarea.id_user_actualizacion = id_user_actualizacion
    tipo_tarea.fecha_actualizacion = datetime.now()
    db.session.commit()

    query_tipo_tarea = db.session.query(TipoTarea.id, TipoTarea.codigo_humano, TipoTarea.nombre, TipoTarea.nivel, TipoTarea.base, TipoTarea.origen_externo, TipoTarea.suspendido, TipoTarea.eliminado, TipoTarea.id_ext, TipoTarea.id_user_actualizacion, TipoTarea.fecha_actualizacion,
                                        TipoTareaDominio.id_dominio_ext, TipoTareaDominio.id_organismo_ext).join(TipoTareaDominio).filter(TipoTareaDominio.id_tipo_tarea==TipoTarea.id, TipoTarea.id == id_tipo_tarea).first()

    return query_tipo_tarea
    #return tipo_tarea


def delete_tipo_tarea(username=None, id=None):
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
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
def get_all_subtipo_tarea(page=1, per_page=10, id_tipo_tarea=None, eliminado=None, suspendido=None):

    query = db.session.query(SubtipoTarea)
    if id_tipo_tarea is not None:
        if not(functions.es_uuid(id_tipo_tarea)):
            raise Exception("El id_tipo_tarea debe ser un UUID: " + id_tipo_tarea)
        query = query.filter(SubtipoTarea.id_tipo==id_tipo_tarea)
    if eliminado is not None:
        query = query.filter(SubtipoTarea.eliminado==eliminado)
    if suspendido is not None:
        query = query.filter(SubtipoTarea.suspendido==suspendido)    

    total= len(query.all())

    res = query.order_by(SubtipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total    

def insert_subtipo_tarea(usr_header=None, id_tipo='', nombre='', nombre_corto='', id_user_actualizacion='', eliminado=False, suspendido=False):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

    if id_user_actualizacion is not None:
        if not(functions.es_uuid(id_user_actualizacion)):
            raise Exception("El id_user_actualizacion debe ser un UUID: " + id_user_actualizacion)
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    
    if id_tipo is not None:
        if not(functions.es_uuid(id_tipo)):
            raise Exception("El id_tipo debe ser un UUID: " + id_tipo)
        tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == id_tipo, TipoTarea.eliminado==False).first()
        if tipo_tarea is None:
            raise Exception("Tipo de tarea no encontrado")

    if eliminado is not None:
        eliminado = eliminado

    if suspendido is not None:
        suspendido = suspendido

    nuevoID=uuid.uuid4()
    nuevo_subtipo_tarea = SubtipoTarea(
        id=nuevoID,
        id_tipo=id_tipo,
        nombre=nombre,
        nombre_corto=nombre_corto,
        base=False,
        origen_externo=False,
        eliminado=eliminado,
        suspendido=suspendido,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    db.session.add(nuevo_subtipo_tarea)
    db.session.commit()
    return nuevo_subtipo_tarea

def update_subtipo_tarea(usr_header=None, subtipo_id='', **kwargs):

    if usr_header is not None:
        id_user_actualizacion = utils.get_username_id(usr_header)

    if id_user_actualizacion is not None:
        if not(functions.es_uuid(id_user_actualizacion)):
            raise Exception("El id_user_actualizacion debe ser un UUID: " + id_user_actualizacion)
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    if subtipo_id is not None:
        if not(functions.es_uuid(subtipo_id)):
            raise Exception("El id_subtipo_tarea debe ser un UUID: " + subtipo_id)

    if subtipo_id is None:
        raise Exception("Debe ingresar el id del subtipo de tarea a actualizar")    

    subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == subtipo_id).first()
    
    if subtipo_tarea is None:
        raise Exception("Subtipo de tarea no encontrado")
    
    if 'nombre' in kwargs:
        subtipo_tarea.nombre = kwargs['nombre']

    if 'nombre_corto' in kwargs:
        subtipo_tarea.nombre_corto = kwargs['nombre_corto']    

    if 'eliminado' in kwargs:
        subtipo_tarea.eliminado = kwargs['eliminado']
    else:
        subtipo_tarea.eliminado = False

    if 'suspendido' in kwargs:
        subtipo_tarea.suspendido = kwargs['suspendido']
    else:
        subtipo_tarea.suspendido = False    
            
        
    subtipo_tarea.base = False
    subtipo_tarea.origen_externo = False
    subtipo_tarea.id_user_actualizacion = id_user_actualizacion    
    subtipo_tarea.fecha_actualizacion = datetime.now()
    db.session.commit()
    return subtipo_tarea

def delete_subtipo_tarea(username=None, id=None):
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        if not(functions.es_uuid(id_user_actualizacion)):
            raise Exception("El id_user_actualizacion debe ser un UUID: " + id_user_actualizacion)
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    if id is not None:
        if not(functions.es_uuid(id)):
            raise Exception("El id_subtipo_tarea debe ser un UUID: " + id)
    if id is None:
        raise Exception("Debe ingresar el id del subtipo de tarea a eliminar")
        
    subtipo_tarea = db.session.query(SubtipoTarea).filter(SubtipoTarea.id == id, SubtipoTarea.eliminado==False).first()
    if subtipo_tarea is not None:
        subtipo_tarea.eliminado=True
        subtipo_tarea.id_user_actualizacion=id_user_actualizacion
        subtipo_tarea.fecha_actualizacion=datetime.now()
        db.session.commit()
        return subtipo_tarea
    else:
        return None
    
##########################TAREAS #############################################
def insert_usuario_tarea(id_tarea='', id_usuario='',id_user_actualizacion='', notas=""):
    
    msg=''
    
    if id_tarea is None:
        raise Exception("Debe ingresar el id de la tarea a asignar")
    if id_tarea is not None:
        if not(functions.es_uuid(id_tarea)):
            raise Exception("El id de la tarea debe ser un UUID: " + id_tarea)

    tareas = db.session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()
    if tareas is None:
        msg = "Tarea no encontrada"
        asigna_usuario= None
        return asigna_usuario, msg
    
    tarea_asignada = db.session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea==id_tarea, TareaAsignadaUsuario.id_usuario==id_usuario).first()
    
    if tarea_asignada is not None:
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
    
    if id is None:
        raise Exception("Debe ingresar el id de la tarea a consultar")
    if id is not None:
        if not(functions.es_uuid(id)):
            raise Exception("El id de la tarea debe ser un UUID: " + id)
        
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
    return result

def get_tarea_by_id(id):

    if id is None:
        raise Exception("Debe ingresar el id de la tarea a consultar")
    
    if id is not None:
        if not(functions.es_uuid(id)):
            raise Exception("El id de la tarea debe ser un UUID: " + id)
    
    res = db.session.query(Tarea).filter(Tarea.id == id).first()
    
    results = []
    id_actuacion_ext=''
    id_expte_ext=''
   
    if res is not None:
        res_usuarios = db.session.query(Usuario.id, Usuario.nombre, Usuario.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                  ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== res.id).order_by(TareaAsignadaUsuario.eliminado).all()
        
        res_grupos = db.session.query(Grupo.id, Grupo.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                  ).join(TareaXGrupo, Grupo.id==TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea== res.id).order_by(TareaXGrupo.eliminado).all()

        
        res_notas = db.session.query(Nota).filter(Nota.id_tarea== res.id, Nota.eliminado==False).order_by(desc(Nota.fecha_creacion)).all()     

        res_expediente = db.session.query(Tarea, ExpedienteExt.id_ext).join(ExpedienteExt, Tarea.id_expediente==ExpedienteExt.id).filter(Tarea.id==res.id).first()
        if res_expediente is not None:
            id_expte_ext = res_expediente.id_ext
        res_actuacion = db.session.query(Tarea, ActuacionExt.id_ext).join(ActuacionExt, Tarea.id_actuacion==ActuacionExt.id).filter(Tarea.id==res.id).first()
        if res_actuacion is not None:
            id_actuacion_ext = res_actuacion.id_ext

        url = []
        res_url = db.session.query(URL).filter(URL.id_tarea == res.id).all()
        if res_url is not None:
            for row in res_url:
                url.append({
                    "id": row.id,
                    "url": row.url,
                    "descripcion": row.descripcion
                })

        editable_externo = False
        res_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == res.id_tipo_tarea).first()
        if res_tipo_tarea is not None:
            if res_tipo_tarea.origen_externo==True and res_tipo_tarea.nivel != 'int':
                editable_externo = True

        usuarios=[]
        grupos=[]
        notas=[]    
        reasignada_usuario=False
        reasignada_grupo=False
        grupos_usr=[]
        if res_usuarios is not None:
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
            "id_actuacion": res.id_actuacion,
            "id_actuacion_ext": id_actuacion_ext,
            "id_expediente": res.id_expediente,
            "id_expediente_ext": id_expte_ext,
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
            "reasignada_grupo": reasignada_grupo,
            "editable_externo": editable_externo,
            "url": url 
        }

        results.append(result)
   
    else:
        return None
    
    return results 

def get_tarea_grupo(username=None, page=1, per_page=10):
        
    if username is not None:
        id_user = utils.get_username_id(username)
        if id_user is None:
            raise Exception("Usuario no encontrado")
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
        url = []
        res_url = db.session.query(URL).filter(URL.id_tarea == tarea.id).all()
        if res_url is not None:
            for row in res_url:
                url.append({
                    "id": row.id,
                    "url": row.url,
                    "descripcion": row.descripcion
                })

        editable_externo = False
        res_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == tarea.id_tipo_tarea).first()
        if res_tipo_tarea is not None:
            if res_tipo_tarea.origen_externo==True and res_tipo_tarea.nivel != 'int':
                editable_externo = True

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
                "reasignada_grupo": False,
                "editable_externo": editable_externo,
                "url": url
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


def get_tarea_grupo_by_id(username=None, page=1, per_page=10): 
    
    results = []

    if username is not None:
        id_user = utils.get_username_id(username)
        if id_user is None:
            raise Exception("Usuario no encontrado")
        
    query_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario==id_user).all()    
        
    if not query_grupo:  # Si no pertenece a ningún grupo
        #print("Usuario no pertenece a ningún grupo")
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
        #print("IDs de grupos:", ids_grupos)
        
        # Consulta para obtener las tareas de los grupos
        query = (
            db.session.query(Tarea)
            .join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea)
            .filter(TareaXGrupo.id_grupo.in_(ids_grupos))  # Filtrar por múltiples grupos
            #.distinct()
            .order_by(desc(Tarea.fecha_creacion))
        )

    total= len(query.all())
    res_tareas = query.offset((page-1)*per_page).limit(per_page).all()

    results = []
    usuario_alias = aliased(Usuario)
    grupo_alias = aliased(Grupo)

    for res in res_tareas:
        # Solo dejar la tarea en results si se reasignó a otro grupo, si no, omitirla
        if reasignada == 'true':
            if len(res_grupos) > 1:
                print("Ordenando grupos por fecha de asignación", grupos_consulta)
                grupos = []
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

                id_grupo_str = str(grupos[1]["id_grupo"])
                if id_grupo_str in grupos_consulta:
                    print('se reasigno a otro grupo:', id_grupo_str, res)
                    # dejar res en res_tareas (no hacer nada especial)
                else:
                    print("No es igual", id_grupo_str, grupos_consulta)
                    continue  # quitar res de res_tareas, pasa a la siguiente iteración
        grupos=[]
        usuarios=[]
        notas=[]
        reasignada_usuario=False
        reasignada_grupo=False
        res_grupos = db.session.query(grupo_alias.id, grupo_alias.nombre, TareaXGrupo.eliminado.label('reasignada'), TareaXGrupo.fecha_asignacion
                                   ).join(TareaXGrupo, grupo_alias.id == TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea == res.id).order_by(TareaXGrupo.eliminado).all()

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


def get_all_tarea_detalle(username=None, page=1, per_page=10, titulo='', label='', labels=None, id_expediente=None, id_expte_ext=None, id_actuacion=None, id_actuacion_ext=None, id_tipo_tarea=None, id_usuario_asignado=None, grupos=None, id_tarea=None, fecha_desde=None, fecha_hasta=None, fecha_fin_desde=None, fecha_fin_hasta=None, prioridad=0, estado=0, eliminado=None, tiene_notas=None, reasignada_grupo=None, sin_usuario_asignado=None, id_dominio=None):
    
    def make_cache_key():
        # Generate a unique cache key based on the function arguments
        return f"get_all_tarea_detalle:{page}:{per_page}:{titulo}:{label}:{labels}:{id_expediente}:{id_actuacion}:{id_tipo_tarea}:{id_usuario_asignado}:{grupos}:{id_tarea}:{fecha_desde}:{fecha_hasta}:{fecha_fin_desde}:{fecha_fin_hasta}:{prioridad}:{estado}:{eliminado}:{tiene_notas}:{reasignada_grupo}"

    # Use the generated cache key
    cache_key = make_cache_key()
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    #raise Exception("Esta función ha sido reemplazada por get_all_tarea_detalle")
    print("**************************START TIME*****************************")
    print("**************************START TIME*****************************")
    print(page, per_page, titulo, label, labels, id_expediente, id_actuacion, id_tipo_tarea, id_usuario_asignado, grupos, id_tarea, fecha_desde,  fecha_hasta, fecha_fin_desde, fecha_fin_hasta, prioridad, estado, eliminado, tiene_notas)
    
    if fecha_desde is not None:
        fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    else:
        fecha_desde=datetime.strptime("30/01/1900","%d/%m/%Y")

    if fecha_hasta is not None:
        fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')
        #.date()
    else:
        fecha_hasta=datetime.now()
        #.date()
        
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())    

    if fecha_desde > fecha_hasta:
        raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")
    
          
    query = db.session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
    if fecha_fin_desde is not None and fecha_fin_hasta is not None:
        fecha_fin_desde = datetime.strptime(fecha_fin_desde, '%d/%m/%Y').date()
        fecha_fin_hasta = datetime.strptime(fecha_fin_hasta, '%d/%m/%Y')
        fecha_fin_hasta = datetime.combine(fecha_fin_hasta, datetime.max.time())
        #.date()
        query = query.filter(Tarea.fecha_fin.between(fecha_fin_desde, fecha_fin_hasta))
    # Apply filters based on provided parameters
    if id_tarea is not None:
        if not(functions.es_uuid(id_tarea)):
            raise Exception("El id_tarea debe ser un UUID: " + id_tarea)
        query = query.filter(Tarea.id == id_tarea)
    if titulo is not None:
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
    if id_expediente is not None:
        if not(functions.es_uuid(id_expediente)):
            raise Exception("El id del expediente debe ser un UUID: " + id_expediente)
        query = query.filter(Tarea.id_expediente == id_expediente)
    if id_expte_ext is not None:
        if not(functions.es_uuid(id_expte_ext)):
            raise Exception("El id del expediente externo debe ser un UUID: " + id_expte_ext)
        query = query.join(ExpedienteExt, Tarea.id_expediente == ExpedienteExt.id
                ).filter(ExpedienteExt.id_ext == id_expte_ext)
    if id_actuacion is not None:
        if not(functions.es_uuid(id_actuacion)):
            raise Exception("El id de la actuación debe ser un UUID: " + id_actuacion)
        query = query.filter(Tarea.id_actuacion == id_actuacion)
    if id_actuacion_ext is not None:
        if not(functions.es_uuid(id_actuacion_ext)):
            raise Exception("El id de la actuación externa debe ser un UUID: " + id_actuacion_ext)
        query = query.join(ActuacionExt, Tarea.id_actuacion == ActuacionExt.id
                ).filter(ActuacionExt.id_ext == id_actuacion_ext)    
    if id_tipo_tarea is not None:
        if not(functions.es_uuid(id_tipo_tarea)):
            raise Exception("El id del tipo de tarea debe ser un UUID: " + id_tipo_tarea)
        query = query.filter(Tarea.id_tipo_tarea == id_tipo_tarea)
    if id_usuario_asignado is not None:
        if not(functions.es_uuid(id_usuario_asignado)):
            raise Exception("El id del usuario asignado debe ser un UUID: " + id_usuario_asignado)
        logger_config.logger.info(f"ID usuario asignado: {id_usuario_asignado}")
        query = query.join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea
                ).filter(TareaAsignadaUsuario.id_usuario== id_usuario_asignado, TareaAsignadaUsuario.eliminado==False
                )
        logger_config.logger.info(f"Total de tareas para el usr: {query.count()}")
    if prioridad and prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)
    if estado  and estado > 0:
        query = query.filter(Tarea.estado == estado)
    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)
    
            
    if tiene_notas is not None:
        query = query.filter(Tarea.tiene_notas_desnz == tiene_notas)

    if sin_usuario_asignado is not None and (sin_usuario_asignado=='true' or sin_usuario_asignado==True):
        # Tareas que no tienen usuarios asignados o todas las asignaciones están eliminadas
        subquery = db.session.query(TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.eliminado == False).subquery()
        query = query.filter(~Tarea.id.in_(subquery))
        
    if labels:
        # Primero eliminás comillas dobles, simples y luego dividís por coma
        labels = labels.split(",")
        for i in range(len(labels)):
            labels[i] = labels[i].strip()
            if not(functions.es_uuid(labels[i])):
                raise Exception("El id de la etiqueta debe ser un UUID: " + labels[i])
            
        query = query.join(LabelXTarea, Tarea.id == LabelXTarea.id_tarea
                ).filter(LabelXTarea.id_label.in_(labels), LabelXTarea.activa == True
                ).distinct()
    reasignada = 'false'
    if grupos:
        #grupos_consulta = grupos.split(",")
        grupos_consulta = [g.strip() for g in grupos.split(",")]
        arr_dominios = []
        dominio_ref = None  # guardamos el dominio del primer grupo

        for g in grupos_consulta:
            g = g.strip()
            print("Grupo a consultar:", g)

            if not functions.es_uuid(g):
                raise Exception("El id del grupo debe ser un UUID: " + g)

            dominio = db.session.query(Grupo.id_dominio_ext).filter(Grupo.id == g).first()
            if dominio is not None:
                print("Dominio del grupo:", dominio.id_dominio_ext)

                if dominio_ref is None:
                    # Primer grupo → lo usamos como referencia
                    dominio_ref = dominio.id_dominio_ext
                    arr_dominios.append(dominio_ref)
                else:
                    # Para los siguientes, comparamos con el dominio de referencia
                    if dominio.id_dominio_ext != dominio_ref:
                        raise Exception(
                            f"Los grupos deben pertenecer al mismo dominio. "
                            f"Grupo: {g} Dominio: {str(dominio.id_dominio_ext)} (ref: {str(dominio_ref)})"
                        )

                if id_dominio is not None and dominio.id_dominio_ext != uuid.UUID(id_dominio):
                    raise Exception(
                        f"El dominio del grupo no coincide con el dominio de la tarea. "
                        f"Dominio del grupo: {str(dominio.id_dominio_ext)} - Dominio actual: {str(id_dominio)}"
                    )

        # Filtrar tareas asignadas a los grupos del usuario
        if(reasignada_grupo is not None):
            reasignada = reasignada_grupo
            if reasignada=='true':
                query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
                ).filter(TareaXGrupo.id_grupo.in_(grupos_consulta), TareaXGrupo.eliminado == True
                ).distinct()
            # else:
            #     query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
            #     ).filter(TareaXGrupo.id_grupo.in_(grupos_consulta), TareaXGrupo.eliminado == False
            #     ).distinct()
            else:
                query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
                ).filter(TareaXGrupo.id_grupo.in_(grupos_consulta), TareaXGrupo.eliminado == False
                ).distinct()   
        else:
            query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
                ).filter(TareaXGrupo.id_grupo.in_(grupos_consulta), TareaXGrupo.eliminado == False
                ).distinct()     
    else:
        if id_dominio is not None:
            if not(functions.es_uuid(id_dominio)):
                raise Exception("El id del dominio debe ser un UUID: " + id_dominio)
            # Obtener los grupos asociados al dominio
            grupos_dominio = db.session.query(Grupo.id).filter(Grupo.id_dominio_ext == id_dominio).all()
            grupos_dominio_ids = [grupo.id for grupo in grupos_dominio]
            if grupos_dominio_ids:
                query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea
                    ).filter(TareaXGrupo.id_grupo.in_(grupos_dominio_ids), TareaXGrupo.eliminado == False
                    ).distinct()  
               


    # Get total count of tasks matching the filter
    total = query.count()
    
    # Pagination with eager loading for associated users and groups
    res_tareas = query.order_by(desc(Tarea.fecha_creacion)).offset((page - 1) * per_page).limit(per_page).all()
    # print("Total de tareas:", total, reasignada)

    # Process each task in paginated results
    results = []
    id_actuacion_ext = ''
    id_expte_ext = ''
    # Using aliased subqueries to reduce the number of queries for users and groups
    usuario_alias = aliased(Usuario)
    grupo_alias = aliased(Grupo)
    if res_tareas is None:
        # total = 0
        return results, total

    print('Cantidad de tareas en el page:', total)

    for res in res_tareas:

        usuarios = []
        grupos = []
        reasignada_usuario = False
        reasignada_grupo = False
        if res.id_expediente is not None:
            res_expediente = db.session.query(ExpedienteExt).filter(ExpedienteExt.id == res.id_expediente).first()
            if res_expediente is not None:
                id_expte_ext = res_expediente.id_ext

        if res.id_actuacion is not None:
            res_actuacion = db.session.query(ActuacionExt).filter(ActuacionExt.id == res.id_actuacion).first()
            if res_actuacion is not None:
                id_actuacion_ext = res_actuacion.id_ext    

        # Fetch assigned users for the task
        res_usuarios = db.session.query(usuario_alias.id, usuario_alias.nombre, usuario_alias.apellido, TareaAsignadaUsuario.eliminado.label('reasignada'), TareaAsignadaUsuario.fecha_asignacion
                                     ).join(TareaAsignadaUsuario, usuario_alias.id == TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea == res.id).order_by(TareaAsignadaUsuario.eliminado).all()
        
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
                                   ).join(TareaXGrupo, grupo_alias.id == TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea == res.id).order_by(TareaXGrupo.fecha_asignacion.desc()).all()


        if reasignada=='true':
            if len(res_grupos) > 1:
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
                
                 # Id del grupo anterior asignado
                id_grupo_str = str(grupos[1]["id_grupo"])
               
                if id_grupo_str in grupos_consulta:                    
                    print('se reasigno a otro grupo:', id_grupo_str)                    
                else:
                    print("No es igual", id_grupo_str, grupos_consulta)
                    total -= 1
                    continue  # quitar res de res_tareas, pasa a la siguiente iteración

        else:        
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

        url = []
        res_url = db.session.query(URL).filter(URL.id_tarea == res.id).all()
        if res_url is not None:
            for row in res_url:
                url.append({
                    "id": row.id,
                    "url": row.url,
                    "descripcion": row.descripcion
                })
        editable_externo = False
        res_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == res.id_tipo_tarea).first()
        if res_tipo_tarea is not None:
            if res_tipo_tarea.origen_externo==True and res_tipo_tarea.nivel != 'int':
                editable_externo = True
         
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
            "id_expte_ext": id_expte_ext,
            "expediente": res.expediente,
            "caratula_expediente": res.caratula_expediente,
            "id_actuacion": res.id_actuacion,
            "id_actuacion_ext": id_actuacion_ext,
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
            "reasignada_grupo": reasignada_grupo,
            "url": url,  # Assuming URL is a field in Tarea
            "editable_externo": editable_externo
        }
        results.append(result)

    result = (results, total)
    #cache.set(cache_key, result, CACHE_TIMEOUT_LONG)
    return result
    # return results, total



#def get_all_tarea(page=1, per_page=10, titulo='', id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_tarea=None, id_usuario_asignado=None, id_grupo=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), prioridad=0, estado=0, eliminado=None, tiene_notas=None):

def get_all_tarea(page=1, per_page=10, titulo='', id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_usuario_asignado=None, id_tarea=None, fecha_desde=None, fecha_hasta=None, prioridad=0, estado=0, eliminado=None, tiene_notas=None):
    
    if fecha_desde is not None:
        fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    else:
        fecha_desde=datetime.strptime("30/01/1900","%d/%m/%Y")
        
            
    if fecha_hasta is not None:
        fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')
        #.date()
    else:
        fecha_hasta=datetime.now()
        #.date() 
        
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())
   
    if fecha_desde > fecha_hasta:
        raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")
   
    query = db.session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))

    if titulo is not None:
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
   
    if id_expediente is not None:
        if(not(functions.es_uuid(id_expediente))):
            raise Exception("El id del expediente debe ser un UUID")
        query = query.filter(Tarea.id_expediente == id_expediente)
    
    if id_actuacion is not None:
        if(not(functions.es_uuid(id_actuacion))):
            raise Exception("El id de la actuación debe ser un UUID")
        query = query.filter(Tarea.id_actuacion == id_actuacion)

    if id_tipo_tarea is not None:
        if(not(functions.es_uuid(id_tipo_tarea))):
            raise Exception("El id del tipo de tarea debe ser un UUID")
        query = query.filter(Tarea.id_tipo_tarea== id_tipo_tarea)

    if id_tarea is not None:
        if(not(functions.es_uuid(id_tarea))):
            raise Exception("El id de la tarea debe ser un UUID")
        query = query.filter(Tarea.id == id_tarea)

    if id_usuario_asignado is not None:
        if(not(functions.es_uuid(id_usuario_asignado))):
            raise Exception("El id del usuario asignado debe ser un UUID")
        usuario = db.session.query(Usuario).filter(Usuario.id == id_usuario_asignado, Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario no encontrado")
        query = query.join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario == id_usuario_asignado)

    if prioridad and prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)

    if estado and estado > 0:
        query = query.filter(Tarea.estado == estado)

    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)

    if tiene_notas is not None:
        query = query.filter(Tarea.tiene_notas_desnz == tiene_notas)    

    total = query.count()

    result = query.order_by(desc(Tarea.fecha_creacion)).offset((page-1)*per_page).limit(per_page).all()
    
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
            url = []
            res_url = db.session.query(URL).filter(URL.id_tarea == reg.id).all()
            if res_url is not None:
                    for row in res_url:
                        url.append({
                            "id": row.id,
                            "url": row.url,
                            "descripcion": row.descripcion
                        })

            editable_externo = False
            res_tipo_tarea = db.session.query(TipoTarea).filter(TipoTarea.id == reg.id_tipo_tarea).first()
            if res_tipo_tarea is not None:
                if res_tipo_tarea.origen_externo==True and res_tipo_tarea.nivel != 'int':
                    editable_externo = True

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
                "tiene_notas": reg.tiene_notas_desnz,
                "url": url,
                "editable_externo": editable_externo
            }
            results.append(result)

    return results, total


def usuarios_tarea(tarea_id=None):    
    if tarea_id is None:
        raise Exception("Debe ingresar el id de la tarea a consultar")
    if not(functions.es_uuid(tarea_id)):
        raise Exception("El id de la tarea debe ser un UUID")
    
    print("Usuarios por tarea:", tarea_id)    
    usuarios = db.session.query(Usuario.nombre.label('nombre'),
                        Usuario.apellido.label('apellido'),
                        Usuario.id.label('id'),
                        Usuario.id_ext.label('id_ext'),
                        Usuario.id_user_actualizacion.label('id_user_actualizacion'),
                        Usuario.fecha_actualizacion.label('fecha_actualizacion'))\
                        .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                        .join(Tarea, TareaAsignadaUsuario.id_tarea == Tarea.id)\
                        .filter(Tarea.id == tarea_id, TareaAsignadaUsuario.eliminado==False)\
                        .all()
    return usuarios


def delete_tarea(username=None, id_tarea=None):
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")

    if id_tarea is None:
        raise Exception("Debe ingresar el id de la tarea a eliminar")
    if not(functions.es_uuid(id_tarea)):
        raise Exception("El id de la tarea debe ser un UUID")
    
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
        return None
    



