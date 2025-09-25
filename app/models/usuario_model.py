import uuid
from datetime import datetime
import common.utils as utils
import common.logger_config as logger_config
from db.alchemy_db import db
from models.alch_model import Usuario, UsuarioGrupo, UsuarioRol, Grupo, Dominio, TareaAsignadaUsuario, Tarea, RolExt
from collections import defaultdict
from common.cache import *

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_usuario_by_id(id):
    
    res = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False, Usuario.suspendido==False).first()
    
    results = []
    tareas=[]
    grupos=[]
 

    if res is not None:
        #Traigo los grupos del usuario
        res_grupos = db.session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido
                                  ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id, UsuarioGrupo.eliminado==False).all()
        
        #Traigo los grupos hijos
        res_tareas = db.session.query(TareaAsignadaUsuario.id_usuario, TareaAsignadaUsuario.eliminado.label("asignada_usr_eliminado"), Tarea.id, Tarea.titulo, Tarea.id_tipo_tarea, Tarea.eliminado, Tarea.fecha_inicio, Tarea.fecha_fin
                                  ).join(Tarea, Tarea.id==TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario== res.id).all()
        

        if res_tareas is not None:
            for row in res_tareas:
                tarea = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "id_tipo_tarea": row.id_tipo_tarea,
                        "eliminado": row.eliminado,
                        "reasignada": row.asignada_usr_eliminado,
                        "fecha_inicio": row.fecha_inicio,
                        "fecha_fin":row.fecha_fin
                    }
                tareas.append(tarea)

        if res_grupos is not None:
            for row in res_grupos:
                grupo = {
                        "id_grupo": row.id,
                        "nombre": row.nombre,
                        "eliminado": row.eliminado,
                        "suspendido": row.suspendido
                     

                }
                grupos.append(grupo)


        ###################Formatear el resultado####################
        result = {
            "id": res.id,
            "nombre": res.nombre,
            "apellido": res.apellido,
            "dni": res.dni,
            "username": res.username,
            "email": res.email,
            "id_ext": res.id_ext,
            "id_user_actualizacion": res.id_user_actualizacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "eliminado": res.eliminado,
            "suspendido": res.suspendido,
            "grupo": grupos,
            "tareas": tareas
        }

        results.append(result)
   
    else:
        return None
    
    return results 

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_usuarios(page=1, per_page=10, nombre="", apellido="", id_grupo=None, dni="", username="", eliminado=None, suspendido=None):
    
    print("eliminado: ", eliminado)
    print("suspendido: ", suspendido)
    print("nombre: ", nombre)
    print("apellido: ", apellido)
    print("dni: ", dni)
    print("username: ", username)
    print("id_grupo: ", id_grupo)

    query = db.session.query(Usuario)
    if id_grupo:
        query = query.filter(Grupo.id == id_grupo)

    if nombre and nombre != "":
        query = query.filter(Usuario.nombre.ilike(f"%{nombre}%"))

    if apellido and apellido != "":
        query = query.filter(Usuario.apellido.ilike(f"%{apellido}%"))

    if dni and dni != "":
        query = query.filter(Usuario.dni.ilike(f"%{dni}%"))

    if username and username != "":
        query = query.filter(Usuario.username.ilike(f"%{username}%"))    

    if eliminado is not None:
        query = query.filter(Usuario.eliminado == eliminado)

    if suspendido is not None:
        query = query.filter(Usuario.suspendido == suspendido)

    total= len(query.all())
    query = query.order_by(Usuario.apellido).offset((page - 1) * per_page).limit(per_page).all()
    return query, total


@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_usuarios_detalle(page=1, per_page=10, nombre="", apellido="", id_grupo=None, dni="", username="", eliminado=None, suspendido=None):
    
    print("eliminado: ", eliminado)
    print("suspendido: ", suspendido)
    print("nombre: ", nombre)
    print("apellido: ", apellido)
    print("dni: ", dni)
    print("username: ", username)
    print("id_grupo: ", id_grupo)

    query = db.session.query(Usuario)

    # Aplicar filtros dinámicamente
    if id_grupo:
        query = query.filter(Grupo.id == id_grupo)

    if nombre and nombre != "":
        query = query.filter(Usuario.nombre.ilike(f"%{nombre}%"))

    if apellido and apellido != "":
        query = query.filter(Usuario.apellido.ilike(f"%{apellido}%"))

    if dni and dni != "":
        query = query.filter(Usuario.dni.ilike(f"%{dni}%"))

    if username and username != "":
        query = query.filter(Usuario.username.ilike(f"%{username}%"))
        print("Total de usuarios: ", len(query.all()))

    if eliminado is not None:
        query = query.filter(Usuario.eliminado == eliminado)

    if suspendido is not None:
        query = query.filter(Usuario.suspendido == suspendido)

    total= len(query.all())

    # Ordenamiento y paginación
    query = query.order_by(Usuario.apellido).offset((page - 1) * per_page).limit(per_page)

    # Ejecutar la consulta paginada
    paginated_results = query.all()
    print("get all usuarios detalle first results: ", paginated_results)
    if paginated_results is not None:
        results = []
        
        for res in paginated_results:
            #Traigo los grupos del usuario
            grupos=[]
            
            res_grupos = db.session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido
                                    ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id, UsuarioGrupo.eliminado==False
                                    ).order_by(Grupo.nombre).all()
            
            #Traigo las tareas asignadas al usuario
            if res_grupos is not None:
                for row in res_grupos:
                    grupo = {
                        "id_grupo": row.id,
                        "nombre": row.nombre,
                        "eliminado": row.eliminado,
                        "suspendido": row.suspendido
                      

                    }
                    grupos.append(grupo)
            #Traigo las tareas del usuario
            tareas=[]
            res_tareas = db.session.query(TareaAsignadaUsuario.id_usuario, TareaAsignadaUsuario.eliminado.label("asignada_usr_eliminado"), Tarea.id, Tarea.titulo, Tarea.id_tipo_tarea, Tarea.eliminado, Tarea.fecha_inicio, Tarea.fecha_fin).join(Tarea, Tarea.id==TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario== res.id).all()
            if res_tareas is not None:
                for row in res_tareas:
                    tarea = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "id_tipo_tarea": row.id_tipo_tarea,
                        "eliminado": row.eliminado,
                        "reasignada": row.asignada_usr_eliminado,
                        "fecha_inicio": row.fecha_inicio,
                        "fecha_fin":row.fecha_fin
                    }
                    tareas.append(tarea)   

            ###################Formatear el resultado####################
            result = {
                "id": res.id,
                "nombre": res.nombre,
                "apellido": res.apellido,
                "id_ext": res.id_ext,
                "id_user_actualizacion": res.id_user_actualizacion,
                "fecha_actualizacion": res.fecha_actualizacion,
                "eliminado": res.eliminado,
                "suspendido": res.suspendido,
                "dni": res.dni,
                "username": res.username,
                "email": res.email,
                "grupo": grupos,
                "tareas": tareas
            }
            results.append(result)

   
    else:
        return None
    
    return results, total 
        
 
@cache.memoize(CACHE_TIMEOUT_LONG)
def get_grupos_by_usuario(id):
    
    res = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if res is None:
        
        raise Exception("Usuario no encontrado")
    
    res = db.session.query(Usuario.id.label("id_usuario"),
                  Usuario.nombre.label("nombre"),
                  Usuario.apellido.label("apellido"),
                  Grupo.id.label("id_grupo"),
                  Grupo.nombre.label("nombre_grupo"),
                  Grupo.eliminado.label("eliminado"),
                  Grupo.suspendido.label("suspendido"),
                  Grupo.descripcion.label("descripcion"),  
                  Grupo.fecha_creacion.label("fecha_creacion"),
                  Grupo.fecha_hasta.label("fecha_hasta"),
                  Grupo.fecha_actualizacion.label("fecha_actualizacion"),
                  Grupo.id_user_actualizacion.label("id_user_actualizacion"),
                  ).join(UsuarioGrupo, Usuario.id == UsuarioGrupo.id_usuario
                  ).join(Grupo, UsuarioGrupo.id_grupo == Grupo.id
                  ).filter(Usuario.id == id, UsuarioGrupo.eliminado==False
                  ).order_by(Grupo.nombre).all()                                    
    return res


def insert_usuario(user_actualizacion=None, id='', nombre='', apellido='', id_ext=None, id_grupo=None, id_user_actualizacion=None, grupo=None, dni='', email='', username=''):
    

    if user_actualizacion is not None:
        id_user_actualizacion = utils.get_username_id(user_actualizacion)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Usuario no ingresado")
        raise Exception("Usuario no ingresado")

    qry_username = db.session.query(Usuario).filter(Usuario.username == username).first()
    if qry_username is not None:
        logger_config.logger.error("Ya existe un usuario con el username ingresado")
        raise Exception("Ya existe un usuario con el username ingresado")
    qry_email = db.session.query(Usuario).filter(Usuario.email == email).first()
    if qry_email is not None:
        logger_config.logger.error("Ya existe un usuario con el email ingresado")
        raise Exception("Ya existe un usuario con el email ingresado")
    
    nuevoID_usuario=uuid.uuid4()
    nuevo_usuario = Usuario(
        id=nuevoID_usuario,
        nombre=nombre,
        apellido=apellido,
        dni = dni,
        username = username,
        email = email.lower(),
        id_ext=id_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    db.session.add(nuevo_usuario)
    if grupo is not None:
        for group in grupo:
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                logger_config.logger.error("Error en el ingreso de grupos. Grupo no existente")   
                raise Exception("Error en el ingreso de grupos. Grupo no existente")

            if existe_grupo.eliminado==True:
                logger_config.logger.error("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)

            nuevoID=uuid.uuid4()
            nuevo_usuario_grupo = UsuarioGrupo(
                id=nuevoID,
                id_grupo=group['id_grupo'],
                id_usuario=nuevoID_usuario,
                id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )
            db.session.add(nuevo_usuario_grupo)

    db.session.commit()

    return nuevo_usuario


def update_usuario(id='',username=None, **kwargs):
    
    logger_config.logger.info("Update usuario")
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Usuario no ingresado")
        raise Exception("Usuario no ingresado")
    
    usuario = db.session.query(Usuario).filter(Usuario.id == id).first()

    if usuario is None:
        return None
    
    update_data = {}
    if 'nombre' in kwargs:
        usuario.nombre = kwargs['nombre']
    if 'apellido' in kwargs:
        usuario.apellido = kwargs['apellido']
    if 'dni' in kwargs:
        usuario.dni = kwargs['dni']
    if 'email' in kwargs:
        qry_username = db.session.query(Usuario).filter(Usuario.email == kwargs['email']).first()
        if qry_username is not None:
            raise Exception("Ya existe un usuario con el email ingresado")
        
        usuario.username = kwargs['email'].lower()
        usuario.email = kwargs['email'].lower()  

    if 'id_ext' in kwargs:
        usuario.id_ext = kwargs['id_ext']
        usuario.id_user_actualizacion = id_user_actualizacion
    if 'suspendido' in kwargs:
        usuario.suspendido = kwargs['suspendido']
    if 'eliminado' in kwargs:
        usuario.eliminado = kwargs['eliminado']    
    usuario.fecha_actualizacion = datetime.now()

    if 'grupo' in kwargs:
        #elimino los grupos existentes para ese usuario
        grupos_usuarios=db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id)
        for grupo in grupos_usuarios:
            grupo.eliminado=True
            grupo.fecha_actualizacion=datetime.now() 
            

        #controlo que el grupo exista y lo asocio al usuario
        for group in kwargs['grupo']:
            existe_grupo = db.session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                logger_config.logger.error("Error en el ingreso de grupos. Grupo no existente")
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                logger_config.logger.error("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)

            grupos_usuarios=db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo == group['id_grupo'], UsuarioGrupo.id_usuario==id).first()
            
            if grupos_usuarios is not None:
                    grupos_usuarios.eliminado=False
                    grupos_usuarios.fecha_actualizacion=datetime.now()
                    grupos_usuarios.id_user_actualizacion=id_user_actualizacion
            else:
                    #asocio el grupo al usuario
                    nuevoID=uuid.uuid4()
                    nuevo_usuario_grupo = UsuarioGrupo(
                            id=nuevoID,
                            id_grupo=group['id_grupo'],
                            id_usuario=id,
                            id_user_actualizacion= id_user_actualizacion,
                            fecha_actualizacion=datetime.now()
                        )
                    db.session.add(nuevo_usuario_grupo)

            #si el usuario es el asignado por defecto para tareas, lo actualizo en el grupo
            if 'asignado_default' in group:
                if group['asignado_default'] == True:
                    grupos_usuarios.id_user_asignado_default = id
                    grupos_usuarios.fecha_actualizacion = datetime.now() 
                    grupos_usuarios.id_user_actualizacion = id_user_actualizacion

    db.session.commit()
    return usuario

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_rol_usuario(username=None):
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)
        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Usuario no ingresado")
        raise Exception("Usuario no ingresado")        
        
    #res = db.session.query(RolExt.email, RolExt.rol).filter(RolExt.email == username).distinct().all()
    """ res = db.session.query(RolExt.email, RolExt.rol, RolExt.id, RolExt.descripcion_ext,
                            UsuarioRol.id_dominio_ext, UsuarioRol.id_grupo, Grupo.nombre.label("nombre_grupo")
                            ).join(UsuarioRol, UsuarioRol.id_rol_ext == RolExt.id
                            ).join(Grupo, Grupo.id == UsuarioRol.id_grupo
                            ).filter(RolExt.email == username
                            ).order_by(RolExt.email, RolExt.rol, RolExt.descripcion_ext).all() """
    res = db.session.query(RolExt.email, RolExt.rol,  
                            UsuarioRol.id_dominio_ext, UsuarioRol.id_grupo, 
                            Grupo.nombre.label("nombre_grupo"),
                            Dominio.descripcion.label("dominio")
                            ).join(UsuarioRol, UsuarioRol.id_rol_ext == RolExt.id
                            ).join(Grupo, Grupo.id == UsuarioRol.id_grupo
                            ).join(Dominio, Dominio.id_dominio_ext == Grupo.id_dominio_ext       
                            ).filter(RolExt.email == username
                            ).group_by(RolExt.email, RolExt.rol, UsuarioRol.id_dominio_ext,
                                       UsuarioRol.id_grupo, Grupo.nombre, Dominio.descripcion
                            ).order_by(RolExt.email, Grupo.nombre, RolExt.rol).all()
    print("encontrados: ", len(res))

    #agrupado = defaultdict(lambda: {"email": "", "rol": "", "usuario_cu": []})
    agrupado = defaultdict(lambda: {"email": "", "id_dominio_ext": "", "dominio": "", "id_grupo": "", "nombre_grupo": "", "rol_usuario": []})
    #agrupado = []
    """ for r in res:
        key = (r.email, r.rol)
        agrupado[key]["email"] = r.email
        agrupado[key]["rol"] = r.rol
        agrupado[key]["usuario_cu"].append({
            "id_dominio_ext": r.id_dominio_ext,
            "id_grupo": r.id_grupo,
            "nombre_grupo": r.nombre_grupo,
            "descripcion_ext": r.descripcion_ext
        }) """

    for r in res:
        key = (r.email, r.id_dominio_ext, r.dominio, r.id_grupo, r.nombre_grupo)
        agrupado[key]["email"] = r.email
        agrupado[key]["id_dominio_ext"] = r.id_dominio_ext
        agrupado[key]["dominio"] = r.dominio
        agrupado[key]["id_grupo"] = r.id_grupo
        agrupado[key]["nombre_grupo"] = r.nombre_grupo
        agrupado[key]["rol_usuario"].append({
            "rol": r.rol
        })    

    # Convertir el resultado en lista para salida tipo JSON
    res = list(agrupado.values())
    print("res: ", res)
    
    
    """ res = db.session.query(RolExt).filter(RolExt.email == username).order_by(RolExt.email, RolExt.rol, RolExt.descripcion_ext).all()
    print("encontrados: ", len(res))
    agrupado = defaultdict(lambda: {"email": "", "rol": "", "usuario_cu": []})

    for r in res:
        key = (r.email, r.rol)
        agrupado[key]["email"] = r.email
        agrupado[key]["rol"] = r.rol
        agrupado[key]["usuario_cu"].append({"descripcion_ext": r.descripcion_ext, "id": r.id})

# Convertir el resultado en lista para salida tipo JSON
    res = list(agrupado.values())
    print("res: ", res) """
    
    return res

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_dominio_usuario(username=None):
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)
        if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Usuario no ingresado")
        raise Exception("Usuario no ingresado")        

    res_dominio = db.session.query(UsuarioGrupo.id_usuario,Dominio.id, Dominio.descripcion
                    ).join(Grupo, Grupo.id == UsuarioGrupo.id_grupo
                    ).join(Dominio, Dominio.id_dominio_ext == Grupo.id_dominio_ext
                    ).filter(UsuarioGrupo.id_usuario == id_user_actualizacion, UsuarioGrupo.eliminado == False, Grupo.eliminado == False, Dominio.eliminado == False
                    ).group_by(UsuarioGrupo.id_usuario, Dominio.id, Dominio.descripcion
                    ).order_by(Dominio.descripcion
                    ).all()
    
    if res_dominio is None:
        raise Exception("El usuario no pertenece a ningún grupo ni dominio")
    
    dominios = []
    for row in res_dominio:
        dominio ={
            "id_dominio": row.id,
            "dominio": row.descripcion
        }
        dominios.append(dominio)

    return dominios

def delete_usuario(username=None, id=None):
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if username is None:
        id_user_actualizacion='4411e1e8-800b-439b-8b2d-9f88bafd3c29'

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Id de usuario no ingresado")
        #raise Exception("Usuario no ingresado"
    
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
        return None
    
    usuario.eliminado = True
    usuario.fecha_actualizacion = datetime.now()
    usuario.id_user_actualizacion = id_user_actualizacion
    db.session.commit()
    return usuario

