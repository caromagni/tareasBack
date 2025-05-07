import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime
from common.utils import *
from common.logger_config import logger
from flask import current_app
from alchemy_db import db
from models.alch_model import Usuario, UsuarioGrupo, Grupo, TareaAsignadaUsuario, Tarea, Rol


def get_usuario_by_id(id):
    
    
    res = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False, Usuario.suspendido==False).first()
    
    results = []
    tareas=[]
    grupos=[]
 

    if res is not None:
        #Traigo los grupos del usuario
        res_grupos = db.session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido, Grupo.codigo_nomenclador
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
                        "suspendido": row.suspendido,
                        "codigo_nomenclador": row.codigo_nomenclador

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
    
    if paginated_results is not None:
        results = []
        
        for res in paginated_results:
            #Traigo los grupos del usuario
            tareas=[]
            grupos=[]
            
            res_grupos = db.session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido, Grupo.codigo_nomenclador
                                    ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id, UsuarioGrupo.eliminado==False
                                    ).order_by(Grupo.nombre).all()
            
            #Traigo las tareas asignadas al usuario
            if res_grupos is not None:
                for row in res_grupos:
                    grupo = {
                        "id_grupo": row.id,
                        "nombre": row.nombre,
                        "eliminado": row.eliminado,
                        "suspendido": row.suspendido,
                        "codigo_nomenclador": row.codigo_nomenclador

                    }
                    grupos.append(grupo)
               

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
                "grupo": grupos
                #"tareas": tareas
            }
            results.append(result)

   
    else:
        return None
    
    return results, total 
        
 
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
                  Grupo.codigo_nomenclador.label("codigo_nomenclador"),
                  Grupo.fecha_creacion.label("fecha_creacion"),
                  Grupo.fecha_hasta.label("fecha_hasta"),
                  Grupo.fecha_actualizacion.label("fecha_actualizacion"),
                  Grupo.id_user_actualizacion.label("id_user_actualizacion"),
                  ).join(UsuarioGrupo, Usuario.id == UsuarioGrupo.id_usuario
                  ).join(Grupo, UsuarioGrupo.id_grupo == Grupo.id
                  ).filter(Usuario.id == id, UsuarioGrupo.eliminado==False).all()                                    
    return res


def insert_usuario(user_actualizacion=None, id='', nombre='', apellido='', id_ext=None, id_grupo=None, id_user_actualizacion=None, grupo=None, dni='', email='', username=''):
    

    if user_actualizacion is not None:
        id_user_actualizacion = get_username_id(user_actualizacion)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        logger.error("Usuario no ingresado")
        raise Exception("Usuario no ingresado")

    qry_username = db.session.query(Usuario).filter(Usuario.username == username).first()
    if qry_username is not None:
        logger.error("Ya existe un usuario con el username ingresado")
        raise Exception("Ya existe un usuario con el username ingresado")
    qry_email = db.session.query(Usuario).filter(Usuario.email == email).first()
    if qry_email is not None:
        logger.error("Ya existe un usuario con el email ingresado")
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
                logger.error("Error en el ingreso de grupos. Grupo no existente")   
                raise Exception("Error en el ingreso de grupos. Grupo no existente")

            if existe_grupo.eliminado==True:
                logger.error("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)
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
    
    logger.info("Update usuario")
    if username is not None:
        id_user_actualizacion = get_username_id(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        logger.error("Usuario no ingresado")
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
                logger.error("Error en el ingreso de grupos. Grupo no existente")
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                logger.error("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)
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

def get_rol_usuario(username=None):
    if username is not None:
        id_user_actualizacion = get_username_id(username)
        if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
        
    res = db.session.query(Rol.email, Rol.rol).filter(Rol.email == username).distinct().all()
    print("username:",username)
    print("rol:",res)
    return res
    
def delete_usuario(username=None, id=None):
    
    if username is not None:
        id_user_actualizacion = get_username_id(username)

    if username is None:
        id_user_actualizacion='4411e1e8-800b-439b-8b2d-9f88bafd3c29'

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        logger.error("Id de usuario no ingresado")
        #raise Exception("Usuario no ingresado"
    
    usuario = db.session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
        return None
    
    usuario.eliminado = True
    usuario.fecha_actualizacion = datetime.now()
    usuario.id_user_actualizacion = id_user_actualizacion
    db.session.commit()
    return usuario

