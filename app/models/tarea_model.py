import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime, timedelta
from ..common.functions import controla_fecha

from flask import current_app

from .alch_model import Tarea, TipoTarea, Usuario, TareaAsignadaUsuario, Grupo, TareaXGrupo, Inhabilidad, SubtipoTarea, ExpedienteExt, ActuacionExt

def es_habil(fecha):
    if fecha.weekday() >= 5:
        return True    
    
def calcular_fecha_vencimiento(fecha, plazo):
    fecha_vencimiento = fecha
    dias_agregados = 0
    while dias_agregados < plazo:
        fecha_vencimiento = fecha_vencimiento + timedelta(days=1)
        if not es_habil(fecha_vencimiento):
            dias_agregados = dias_agregados + 1

    return fecha_vencimiento


def insert_tarea(id_grupo=None, prioridad=0, estado=0, id_actuacion=None, titulo='', cuerpo='', id_expediente=None, caratula_expediente='', id_tipo_tarea=None, id_subtipo_tarea=None, eliminable=False, fecha_eliminacion=None, id_usuario_asignado=None, id_user_actualizacion=None, fecha_inicio=None, fecha_fin=None, plazo=0, usuario=None, grupo=None):
    session: scoped_session = current_app.session
    ##############Validaciones################
    if id_expediente is not None:
        expediente = session.query(ExpedienteExt).filter(ExpedienteExt.id == id_expediente).first()
        if expediente is None:
            raise Exception("Expediente no encontrado")
    if id_actuacion is not None:
        actuacion = session.query(ActuacionExt).filter(ActuacionExt.id == id_actuacion).first()
        if actuacion is None:
            raise Exception("Actuacion no encontrada")    
    if id_tipo_tarea is not None:
        tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea, TipoTarea.eliminado==False).first()
        if tipo_tarea is None:
            raise Exception("Tipo de tarea no encontrado")
        nombre_tipo=tipo_tarea.nombre
        if id_subtipo_tarea is not None:
            subtipo_tarea = session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.eliminado==False).first()
            if subtipo_tarea is None:
                raise Exception("Subtipo de tarea no encontrado")
            nombre_subtipo = subtipo_tarea.nombre
            subtipo_tarea = session.query(SubtipoTarea).filter(SubtipoTarea.id == id_subtipo_tarea, SubtipoTarea.id_tipo == id_tipo_tarea).first()
            if subtipo_tarea is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
    else:
        if id_subtipo_tarea is not None:
            raise Exception("Debe ingresar el tipo de tarea")
            
    if id_user_actualizacion is not None:
        qryusuario = session.query(Usuario).filter(Usuario.id == id_user_actualizacion).first()
        if qryusuario is None:
            raise Exception("Usuario de actualizacion no encontrado")   
         
    ####################Calculo de plazo##################
    print("###############Calculo de plazo################")
    con_plazo=False
    if fecha_inicio is None:
        fecha_inicio = datetime.now().date()
    print("fecha_inicio:",fecha_inicio)
    if plazo>0:
        print("Calculo de plazo - ", plazo)
        #plazo=10
        #Tarea.fecha_creacion.between(fecha_desde, fecha_hasta
        #Inhabilidad.fecha_desde <= fecha_inicio, Inhabilidad.fecha_hasta >= fecha_inicio  
        query_inhabilidad = session.query(Inhabilidad).all()
        if len(query_inhabilidad)>0:                                    
            query_inhabilidad = session.query(Inhabilidad).filter(Inhabilidad.fecha_desde <= fecha_inicio, Inhabilidad.fecha_hasta >= fecha_inicio).all()
            if query_inhabilidad is not None:
                for row in query_inhabilidad:
                    plazo=plazo+1

        #fecha_fin = fecha_inicio + timedelta(days=plazo)
        fecha_fin = calcular_fecha_vencimiento(fecha_inicio, plazo)
        print("fecha_fin:",fecha_fin)

    
    #fecha_inicio = controla_fecha(fecha_inicio)
    #fecha_fin = controla_fecha(fecha_fin)   
    print("fecha_inicio:",fecha_inicio)
    tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea).first()
    if tipo_tarea is None:
       msg = "Tipo de tarea no encontrado"
       return None, msg

    nuevoID_tarea=uuid.uuid4()

    nueva_tarea = Tarea(
        id=nuevoID_tarea,
        prioridad=prioridad,
        estado=estado,
        id_actuacion=id_actuacion,
        titulo=titulo,
        cuerpo=cuerpo,
        id_expediente=id_expediente,
        caratula_expediente=caratula_expediente,
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

    session.add(nueva_tarea)
    print("#"*50)
    print("Arma grupos")
    if grupo is not None:
        for group in grupo:
            id_grupo=group['id_grupo']
            existe_grupo = session.query(Grupo).filter(Grupo.id == id_grupo, Grupo.eliminado==False).first()
            if existe_grupo is None:
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)
            
            if existe_grupo.suspendido==True:
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre)

            
            nuevoID_tareaxgrupo=uuid.uuid4()
            tareaxgrupo= TareaXGrupo(
                id=nuevoID_tareaxgrupo,
                id_grupo=id_grupo,
                id_tarea=nuevoID_tarea,
                id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            ) 
            session.add(tareaxgrupo)  

    if usuario is not None:
        for user in usuario:
            id_usuario = user['id_usuario']
            existe_usuario = session.query(Usuario).filter(Usuario.id == id_usuario, Usuario.eliminado==False).first()
            if existe_usuario is None:
                raise Exception("Error en el ingreso de Usuario. Usuario no existente")
            
            if existe_usuario.eliminado==True:
                raise Exception("Error en el ingreso de Usuarios. Usuario eliminado: " + existe_usuario.apelllido)

            
            if existe_usuario is not None:
                nuevoID=uuid.uuid4()
                asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=nuevoID_tarea,
                    id_usuario=user['id_usuario'],
                    id_user_actualizacion=id_user_actualizacion,
                    fecha_actualizacion=datetime.now()
                )
                session.add(asigna_usuario)
    
       
    session.commit()
    return nueva_tarea

def update_tarea(id='', **kwargs):
    ################################
    controla_tipo=False
    session: scoped_session = current_app.session
    tarea = session.query(Tarea).filter(Tarea.id == id, Tarea.eliminado==False).first()
   
    if tarea is None:
        return None
    
    if 'caratula_expte' in kwargs:
        tarea.caratula_expte = kwargs['caratula_expte'].upper()
    if 'cuerpo' in kwargs:
        tarea.cuerpo = kwargs['cuerpo']
    if 'eliminable' in kwargs:
        tarea.eliminable = kwargs['eliminable']
    if 'id_actuacion' in kwargs:
        actuacion = session.query(ActuacionExt).filter(ActuacionExt.id == kwargs['id_actuacion']).first()
        if actuacion is None:
            raise Exception("Actuacion no encontrada")
        tarea.id_actuacion = kwargs['id_actuacion']
    if 'id_expediente' in kwargs:
        expediente = session.query(ExpedienteExt).filter(ExpedienteExt.id == kwargs['id_expediente']).first()
        if expediente is None:
            raise Exception("Expediente no encontrado")
        tarea.id_expediente = kwargs['id_expediente']    
    #Validacion de tipo y subtipo de tarea
    if 'id_tipo_tarea' in kwargs:
        tipo = session.query(TipoTarea).filter(TipoTarea.id == kwargs['id_tipo_tarea'], TipoTarea.eliminado==False).first()
        if tipo is  None:
            raise Exception("Tipo de tarea no encontrado:" + kwargs['id_tipo_tarea'])
        
        nombre_tipo=tipo.nombre
        if 'id_subtipo_tarea' in kwargs:
            subtipo = session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            nombre_subtipo = subtipo.nombre
            print("nombre_subtipo:",nombre_subtipo)
            subtipo = session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.id_tipo == kwargs['id_tipo_tarea']).first()
            if subtipo is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' y el subtipo de tarea '" + nombre_subtipo +"' no se corresponden")
           
            tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
            tarea.id_subtipo_tarea = kwargs['id_subtipo_tarea']
        #no se ingreso subtipo de tarea, verifico con el subtipo actual
        else:
            subtipo = session.query(SubtipoTarea).filter(SubtipoTarea.id == tarea.id_subtipo_tarea, SubtipoTarea.id_tipo==kwargs['id_tipo_tarea']).first()
            if subtipo is None:
                raise Exception("El tipo de tarea '" + nombre_tipo + "' no se corresponde al subtipo de tarea actual")

            tarea.id_tipo_tarea = kwargs['id_tipo_tarea']
    else:
        #no se ingreso tipo de tarea , verifico con el tipo actual         
        if 'id_subtipo_tarea' in kwargs:
            subtipo = session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs['id_subtipo_tarea'], SubtipoTarea.eliminado==False).first()
            if subtipo is None:
                raise Exception("Subtipo de tarea no encontrado")
            #verifico que el subtipo de tarea corresponda al tipo de tarea actual
            nombre_subtipo = subtipo.nombre
            subtipo = session.query(SubtipoTarea).filter(SubtipoTarea.id == kwargs["id_subtipo_tarea"], SubtipoTarea.id_tipo==tarea.id_tipo_tarea).first()
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
    if 'id_user_actualizacion' in kwargs:
        usuario = session.query(Usuario).filter(Usuario.id == kwargs['id_user_actualizacion'], Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado")
        tarea.id_user_actualizacion = kwargs['id_user_actualizacion']  
        
    tarea.fecha_actualizacion = datetime.now()
    usuarios=[]
    grupos=[]
    if 'grupo' in kwargs:
        #elimino los grupos existentes para ese usuario
        grupos_usuarios=session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id)
        grupos_usuarios.delete()

        """ for grupo in grupos_usuarios:
            grupo.eliminado=True
            grupo.fecha_actualizacion=datetime.now() """

        #controlo que el grupo exista y lo asocio al usuario
        for group in kwargs['grupo']:
            existe_grupo = session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)

            if existe_grupo.suspendido==True:
                raise Exception("Error en el ingreso de grupos. Grupo suspendido: " + existe_grupo.nombre)

            nuevoID=uuid.uuid4()
            tareaxgrupo = session.query(TareaXGrupo).filter(TareaXGrupo.id_tarea == id, TareaXGrupo.id_grupo==group['id_grupo']).first()
            if tareaxgrupo is None:
                nuevo_tarea_grupo = TareaXGrupo(
                    id=nuevoID,
                    id_grupo=group['id_grupo'],
                    id_tarea=id,
                    id_user_actualizacion= kwargs['id_user_actualizacion'],
                    fecha_actualizacion=datetime.now()
                )
                session.add(nuevo_tarea_grupo)
            grupo = {
                "id": existe_grupo.id,
                "nombre": existe_grupo.nombre
            }
            grupos.append(grupo)   

    if 'usuario' in kwargs:
        #elimino los usuarios existentes para esa tarea
        usuarios_tarea=session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id)
        usuarios_tarea.delete()

        """ for usuario in usuarios_tarea:
            usuario.eliminado=True
            usuario.fecha_actualizacion=datetime.now() """

        #controlo que el usuario exista y lo asocio a la tarea
        for user in kwargs['usuario']:
            existe_usuario = session.query(Usuario).filter(Usuario.id == user['id_usuario']).first()
            if existe_usuario is None:
                raise Exception("Error en el ingreso de usuarios. Usuario no existente")
            
            if existe_usuario.eliminado==True:
                raise Exception("Error en el ingreso de usuarios. Usuario eliminado: " + existe_usuario.nombre)

            nuevoID=uuid.uuid4()
            asigna_usuario = session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea == id, TareaAsignadaUsuario.id_usuario==user['id_usuario']).first()
            if asigna_usuario is None:
                nuevo_asigna_usuario = TareaAsignadaUsuario(
                    id=nuevoID,
                    id_tarea=id,
                    id_usuario=user['id_usuario'],
                    id_user_actualizacion= kwargs['id_user_actualizacion'],
                    fecha_actualizacion=datetime.now()
                )
                session.add(nuevo_asigna_usuario)

            usuario = {
                "id": existe_usuario.id,
                "nombre": existe_usuario.nombre,
                "apellido": existe_usuario.apellido
            }
            usuarios.append(usuario)

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
        "id_actuacion": tarea.id_actuacion,
        "actuacion": tarea.actuacion,
        "cuerpo": tarea.cuerpo,
        "eliminable": tarea.eliminable,
        "eliminado": tarea.eliminado,
        "fecha_eliminacion": tarea.fecha_eliminacion,
        "fecha_actualizacion": tarea.fecha_actualizacion,
        "fecha_creacion": tarea.fecha_creacion,
        "id_grupo": tarea.id_grupo,
        "grupos": grupos,
        "usuarios": usuarios
    }

    session.commit()
    return result

def get_all_tipo_tarea(page=1, per_page=10):
    print("get_tipo_tareas - ", page, "-", per_page)
    session: scoped_session = current_app.session
    todo = session.query(TipoTarea).all()
    total= len(todo)
    res = session.query(TipoTarea).order_by(TipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_tarea(id='', codigo_humano='', nombre='', id_user_actualizacion='', base=False):
    session: scoped_session = current_app.session
    if id_user_actualizacion is not None:
        usuario = session.query(Usuario).filter(Usuario.id == id_user_actualizacion, Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado")
    
    
    nuevoID=uuid.uuid4()

    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
        base=base,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    session.add(nuevo_tipo_tarea)
    session.commit()
    return nuevo_tipo_tarea


def update_tipo_tarea(tipo_tarea_id='', **kwargs):

    session: scoped_session = current_app.session
    tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == tipo_tarea_id).first()
    
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

    if 'id_user_actualizacion' in kwargs:
        tipo_tarea.id_user_actualizacion = kwargs['id_user_actualizacion']

    tipo_tarea.fecha_actualizacion = datetime.now()
    session.commit()
    return tipo_tarea


def delete_tipo_tarea(id):
    session: scoped_session = current_app.session
    tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == id, TipoTarea.eliminado==False).first()
    if tipo_tarea is not None:
        tipo_tarea.eliminado=True
        tipo_tarea.fecha_actualizacion=datetime.now()
        session.commit()
        return tipo_tarea
    else:
        print("Tipo de tarea no encontrado")
        return None
#########################SUBTIPO TAREA############################################
def get_all_subtipo_tarea(page=1, per_page=10, id_tipo_tarea=None, eliminado=None):
    print("get_tipo_tareas - ", page, "-", per_page)
    session: scoped_session = current_app.session

    query = session.query(SubtipoTarea)
    if id_tipo_tarea is not None:
        query = query.filter(SubtipoTarea.id_tipo==id_tipo_tarea)
    if eliminado is not None:
        query = query.filter(SubtipoTarea.eliminado==eliminado)

    total= len(query.all())

    res = query.order_by(SubtipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total    

def insert_subtipo_tarea(id_tipo='', nombre='', id_user_actualizacion='', base=False):
    session: scoped_session = current_app.session
    if id_user_actualizacion is not None:
        usuario = session.query(Usuario).filter(Usuario.id == id_user_actualizacion, Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado")
    if id_tipo is not None:
        tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == id_tipo, TipoTarea.eliminado==False).first()
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

    session.add(nuevo_subtipo_tarea)
    session.commit()
    return nuevo_subtipo_tarea

def update_subtipo_tarea(subtipo_id='', **kwargs):

    session: scoped_session = current_app.session
    subtipo_tarea = session.query(SubtipoTarea).filter(SubtipoTarea.id == subtipo_id).first()
    
    if subtipo_tarea is None:
        raise Exception("Subtipo de tarea no encontrado")
    
    if 'nombre' in kwargs:
        subtipo_tarea.nombre = kwargs['nombre']
    if 'id_user_actualizacion' in kwargs:
        subtipo_tarea.id_user_actualizacion = kwargs['id_user_actualizacion']
    if 'base' in kwargs:
        subtipo_tarea.base = kwargs['base']
    else:
        subtipo_tarea.base = False    

    subtipo_tarea.fecha_actualizacion = datetime.now()
    session.commit()
    return subtipo_tarea

def delete_subtipo_tarea(id):
    session: scoped_session = current_app.session
    subtipo_tarea = session.query(SubtipoTarea).filter(SubtipoTarea.id == id, SubtipoTarea.eliminado==False).first()
    if subtipo_tarea is not None:
        subtipo_tarea.eliminado=True
        subtipo_tarea.fecha_actualizacion=datetime.now()
        session.commit()
        return subtipo_tarea
    else:
        print("Subtipo de tarea no encontrado")
        return None
    
##########################TAREAS #############################################
def insert_usuario_tarea(id_tarea='', id_usuario='',id_user_actualizacion='', notas=""):
    msg=''
    session: scoped_session = current_app.session
    tareas = session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()
    if tareas is None:
        print("Tarea no encontrada")
        msg = "Tarea no encontrada"
        asigna_usuario= None
        return asigna_usuario, msg
    
    tarea_asignada = session.query(TareaAsignadaUsuario).filter(TareaAsignadaUsuario.id_tarea==id_tarea, TareaAsignadaUsuario.id_usuario==id_usuario).first()
    
    if tarea_asignada is not None:
        print("Usuario ya asignado a la tarea")
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

    session.add(asigna_usuario)
    session.commit()
    return asigna_usuario, msg

def get_tarea_by_id(id):
    session: scoped_session = current_app.session
    
    res = session.query(Tarea).filter(Tarea.id == id).first()
    
    results = []
    usuarios=[]
    grupos=[]
 

    if res is not None:
        #Consulto los usuarios asignados a la tarea
        print("Tarea encontrada:", res)
        res_usuarios = session.query(Usuario.id, Usuario.nombre, Usuario.apellido
                                  ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== res.id).all()
        
        #Consulto los grupos asignados a la tarea
        res_grupos = session.query(Grupo.id, Grupo.nombre
                                  ).join(TareaXGrupo, Grupo.id==TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea== res.id).all()

        

        if res_usuarios is not None:
            for row in res_usuarios:
                usuario = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido
                }
                usuarios.append(usuario)

        if res_grupos is not None:
            for row in res_grupos:
                grupo = {
                    "id": row.id,
                    "nombre": row.nombre
                }
                grupos.append(grupo)


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
            "id_subtipo_tarea": res.id_subtipo_tarea,
            "tipo_tarea": res.tipo_tarea,
            "subtipo_tarea": res.subtipo_tarea,
            "id_expediente": res.id_expediente,
            "expediente": res.expediente,
            "id_actuacion": res.id_actuacion,
            "actuacion": res.actuacion,
            "cuerpo": res.cuerpo,
            "eliminable": res.eliminable,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "fecha_creacion": res.fecha_creacion,
            "id_grupo": res.id_grupo,
            "grupo": res.grupo,
            "grupos": grupos,
            "usuarios": usuarios
        }

        results.append(result)
   
    else:
        print("Tarea no encontrada")
        return None
    
    return results 

def get_all_tarea_detalle(page=1, per_page=10, titulo='', id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_usuario_asignado=None, id_grupo=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), prioridad=0, estado=0, eliminado=None):
    print("estado:", estado)
    print("tipo de dato:", type(estado))
    print("prioridad:", prioridad)
    print("tipo de dato:", type(prioridad))
    session: scoped_session = current_app.session
    query = session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
    if titulo != '':
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))

    if id_expediente is not None:
        query = query.filter(Tarea.id_expediente == id_expediente)
    
    if id_actuacion is not None:
        query = query.filter(Tarea.id_actuacion == id_actuacion)

    if id_tipo_tarea is not None:
        query = query.filter(Tarea.id_tipo_tarea== id_tipo_tarea)

    #if id_usuario_asignado is not None:
    #    query = query.join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario == id_usuario_asignado)

    #if id_grupo is not None:
    #    query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id_grupo)

    if prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)

    if estado > 0:
        query = query.filter(Tarea.estado == estado)    

    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)

    #muestra datos
    print("Query:", query.all())
    total= len(query.all())

    res_tareas = query.order_by(Tarea.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    results = []
    
    for res in res_tareas:
        usuarios=[]
        grupos=[]
        #Consulto los usuarios asignados a la tarea
        print("Tarea encontrada:", res)
        res_usuarios = session.query(Usuario.id, Usuario.nombre, Usuario.apellido
                                  ).join(TareaAsignadaUsuario, Usuario.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_tarea== res.id).all()
        print("Usuarios:", res_usuarios)
        print("Id tarea:", res.id)
        
        if res_usuarios is not None:
            for row in res_usuarios:
                usuario = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido
                }
                usuarios.append(usuario)

        res_grupos = session.query(Grupo.id, Grupo.nombre
                                  ).join(TareaXGrupo, Grupo.id==TareaXGrupo.id_grupo).filter(TareaXGrupo.id_tarea== res.id).all()


        if res_grupos is not None:
            for row in res_grupos:
                grupo = {
                    "id": row.id,
                    "nombre": row.nombre
                }
                grupos.append(grupo)            
        

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
            "usuarios": usuarios
        }
        results.append(result)
    
    
    return results, total         


def get_all_tarea(page=1, per_page=10, titulo='', id_expediente=None, id_actuacion=None, id_tipo_tarea=None, id_usuario_asignado=None, id_grupo=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), prioridad=0, estado=0, eliminado=None):
    session: scoped_session = current_app.session
    query = session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
    if titulo != '':
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
    if id_expediente is not None:
        query = query.filter(Tarea.id_expediente == id_expediente)
    
    if id_actuacion is not None:
        query = query.filter(Tarea.id_actuacion == id_actuacion)

    if id_tipo_tarea is not None:
        query = query.filter(Tarea.id_tipo_tarea== id_tipo_tarea)

    if id_usuario_asignado is not None:
        query = query.join(TareaAsignadaUsuario, Tarea.id == TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario == id_usuario_asignado)

    if id_grupo is not None:
        query = query.join(TareaXGrupo, Tarea.id == TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id_grupo)

    if prioridad > 0:
        query = query.filter(Tarea.prioridad == prioridad)

    if eliminado is not None:
        query = query.filter(Tarea.eliminado == eliminado)

    #muestra datos
    print("Query:", query.all())
    total= len(query.all())

    result = query.order_by(Tarea.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()
    
    return result, total

def usuarios_tarea(tarea_id=""):
    session: scoped_session = current_app.session
    print("Usuarios por tarea:", tarea_id)    
    usuarios = session.query(Usuario.nombre.label('nombre'),
                        Usuario.apellido.label('apellido'),
                        Usuario.id.label('id'),
                        Usuario.id_persona_ext.label('id_persona_ext'),
                        Usuario.id_user_actualizacion.label('id_user_actualizacion'),
                        Usuario.fecha_actualizacion.label('fecha_actualizacion'),
                        Tarea.id_grupo.label('id_grupo'),\
                        Grupo.nombre.label('grupo'))\
                        .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                        .join(Tarea, TareaAsignadaUsuario.id_tarea == Tarea.id)\
                        .join(Grupo, Tarea.id_grupo == Grupo.id)\
                        .filter(TareaAsignadaUsuario.id_tarea == tarea_id)\
                        .all()
    
    return usuarios

def delete_tarea(id_tarea):
    session: scoped_session = current_app.session
    tarea = session.query(Tarea).filter(Tarea.id == id_tarea, Tarea.eliminado==False).first()
    if tarea is not None:
        if tarea.eliminable==False:
              print("Tarea no eliminable")
              raise Exception("Tarea no eliminable")
              
        tarea.eliminado=True
        tarea.fecha_eliminacion=datetime.now()
        tarea.fecha_actualizacion=datetime.now()
        session.commit()
        return tarea
    
    else:
        print("Tarea no encontrada")
        return None
    



