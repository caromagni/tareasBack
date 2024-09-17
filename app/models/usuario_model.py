import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Usuario, UsuarioGrupo, Grupo, TareaAsignadaUsuario, Tarea


def get_usuario_by_id(id):
    session: scoped_session = current_app.session
    
    res = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False, Usuario.suspendido==False).first()
    
    results = []
    tareas=[]
    grupos=[]
 

    if res is not None:
        #Traigo los grupos del usuario
        res_grupos = session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido, Grupo.codigo_nomenclador
                                  ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id).all()
        
        #Traigo los grupos hijos
        res_tareas = session.query(TareaAsignadaUsuario.id_usuario, Tarea.id, Tarea.titulo, Tarea.id_tipo_tarea, Tarea.eliminado
                                  ).join(Tarea, Tarea.id==TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario== res.id).all()
        

        if res_tareas is not None:
            for row in res_tareas:
                tarea = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "id_tipo_tarea": row.id_tipo_tarea,
                        "eliminado": row.eliminado
                    }
                tareas.append(tarea)

        if res_grupos is not None:
            for row in res_grupos:
                grupo = {
                        "id": row.id,
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
            "id_persona_ext": res.id_persona_ext,
            "id_user_actualizacion": res.id_user_actualizacion,
            "fecha_actualizacion": res.fecha_actualizacion,
            "eliminado": res.eliminado,
            "suspendido": res.suspendido,
            "grupos": grupos,
            "tareas": tareas
        }

        results.append(result)
   
    else:
        return None
    
    return results 

def get_all_usuarios(page=1, per_page=10, nombre="", apellido="", id_grupo=None, dni="", username=""):
    session: scoped_session = current_app.session

    query = session.query(Usuario)
    if id_grupo:
        query = query.filter(Grupo.id == id_grupo)

    if nombre != "":
        query = query.filter(Usuario.nombre.ilike(f"%{nombre}%"))

    if apellido != "":
        query = query.filter(Usuario.apellido.ilike(f"%{apellido}%"))

    if dni != "":
        query = query.filter(Usuario.dni.ilike(f"%{dni}%"))

    if username != "":
        query = query.filter(Usuario.username.ilike(f"%{username}%"))    

    total= len(query.all())
    query = query.order_by(Usuario.apellido).offset((page - 1) * per_page).limit(per_page).all()
    return query, total


def get_all_usuarios_detalle(page=1, per_page=10, nombre="", apellido="", id_grupo=None, dni="", username=""):
    session: scoped_session = current_app.session

    query = session.query(Usuario)

    # Aplicar filtros dinámicamente
    if id_grupo:
        query = query.filter(Grupo.id == id_grupo)

    if len(nombre) > 0:
        query = query.filter(Usuario.nombre.ilike(f"%{nombre}%"))

    if len(apellido) > 0:
        query = query.filter(Usuario.apellido.ilike(f"%{apellido}%"))

    if len(dni) > 0:

        query = query.filter(Usuario.dni.ilike(f"%{dni}%"))

    if username != "":
        query = query.filter(Usuario.username.ilike(f"%{username}%"))


    total= len(query.all())

    # Ordenamiento y paginación
    query = query.order_by(Usuario.apellido).offset((page - 1) * per_page).limit(per_page)

    # Ejecutar la consulta paginada
    paginated_results = query.all()

    if paginated_results is not None:
        results = []
        for res in paginated_results:
            tareas=[]
            grupos=[]
            #Traigo los grupos del usuario
            res_grupos = session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre, Grupo.eliminado, Grupo.suspendido, Grupo.codigo_nomenclador
                                    ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id).all()
            
            #Traigo las tareas asignadas al usuario
            res_tareas = session.query(TareaAsignadaUsuario.id_usuario, Tarea.id, Tarea.titulo, Tarea.id_tipo_tarea, Tarea.eliminado
                                    ).join(Tarea, Tarea.id==TareaAsignadaUsuario.id_tarea).filter(TareaAsignadaUsuario.id_usuario== res.id).all()
            

            if res_tareas is not None:
                print("Tiene tareas-", len(res_tareas))
                for row in res_tareas:
                    tarea = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "id_tipo_tarea": row.id_tipo_tarea,
                        "eliminado": row.eliminado
                    }
                    tareas.append(tarea)

            if res_grupos is not None:
                print("Tiene grupos-", len(res_grupos))
                for row in res_grupos:
                    grupo = {
                        "id": row.id,
                        "nombre": row.nombre,
                        "eliminado": row.eliminado,
                        "suspendido": row.suspendido,
                        "codigo_nomenclador": row.codigo_nomenclador

                    }
                    grupos.append(grupo)
                print("grupos:", grupos)    


            ###################Formatear el resultado####################
            result = {
                "id": res.id,
                "nombre": res.nombre,
                "apellido": res.apellido,
                "id_persona_ext": res.id_persona_ext,
                "id_user_actualizacion": res.id_user_actualizacion,
                "fecha_actualizacion": res.fecha_actualizacion,
                "eliminado": res.eliminado,
                "suspendido": res.suspendido,
                "dni": res.dni,
                "username": res.username,
                "email": res.email,
                "grupos": grupos,
                "tareas": tareas
            }
            print("result:", result)
            results.append(result)

   
    else:
        return None
    
    return results, total 
        

def get_grupos_by_usuario(id):
    session: scoped_session = current_app.session
    res = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if res is None:
        raise Exception("Usuario no encontrado")
    
    res = session.query(Usuario.id.label("id_usuario"),
                  Usuario.nombre.label("nombre"),
                  Usuario.apellido.label("apellido"),
                  Grupo.id.label("id_grupo"),
                  Grupo.nombre.label("nombre_grupo"),
                  Grupo.codigo_nomenclador.label("codigo_nomenclador")
                  ).join(UsuarioGrupo, Usuario.id == UsuarioGrupo.id_usuario
                  ).join(Grupo, UsuarioGrupo.id_grupo == Grupo.id
                  ).filter(Usuario.id == id, UsuarioGrupo.eliminado==False).all()                                    

    return res


def insert_usuario(id='', nombre='', apellido='', id_persona_ext=None, id_grupo=None, id_user_actualizacion=None, grupo=None, dni='', email='', username=''):
    session: scoped_session = current_app.session
    nuevoID_usuario=uuid.uuid4()
    print("nuevo_usuario:",nuevoID_usuario)
    nuevo_usuario = Usuario(
        id=nuevoID_usuario,
        nombre=nombre,
        apellido=apellido,
        dni = dni,
        username = username.upper(),
        email = email.lower(),
        id_persona_ext=id_persona_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    session.add(nuevo_usuario)
    if grupo is not None:
        for group in grupo:
            existe_grupo = session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                raise Exception("Error en el ingreso de grupos. Grupo no existente")

            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)

            nuevoID=uuid.uuid4()
            nuevo_usuario_grupo = UsuarioGrupo(
                id=nuevoID,
                id_grupo=group['id_grupo'],
                id_usuario=nuevoID_usuario,
                id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )
            session.add(nuevo_usuario_grupo)

    session.commit()

    return nuevo_usuario


def update_usuario(id='', **kwargs):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
   
    if usuario is None:
        return None
    
    print("Usuario encontrado:",usuario)

    update_data = {}
    if 'nombre' in kwargs:
        usuario.nombre = kwargs['nombre']
    if 'apellido' in kwargs:
        usuario.apellido = kwargs['apellido']
    if 'username' in kwargs:
        usuario.username = kwargs['username'].upper()
    if 'dni' in kwargs:
        usuario.dni = kwargs['dni']
    if 'email' in kwargs:
        usuario.email = kwargs['email'].lower()           
    if 'id_persona_ext' in kwargs:
        usuario.id_persona_ext = kwargs['id_persona_ext']
    if 'id_user_actualizacion' in kwargs:
        usuario.id_user_actualizacion = kwargs['id_user_actualizacion']
    if 'suspendido' in kwargs:
        usuario.suspendido = kwargs['suspendido']
    usuario.fecha_actualizacion = datetime.now()

    if 'grupo' in kwargs:
        #elimino los grupos existentes para ese usuario
        grupos_usuarios=session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id)
        for grupo in grupos_usuarios:
            grupo.eliminado=True
            grupo.fecha_actualizacion=datetime.now()

        #controlo que el grupo exista y lo asocio al usuario
        for group in kwargs['grupo']:
            existe_grupo = session.query(Grupo).filter(Grupo.id == group['id_grupo']).first()
            if existe_grupo is None:
                raise Exception("Error en el ingreso de grupos. Grupo no existente")
            
            if existe_grupo.eliminado==True:
                raise Exception("Error en el ingreso de grupos. Grupo eliminado: " + existe_grupo.nombre)

            nuevoID=uuid.uuid4()
            usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.id_grupo==group['id_grupo'], UsuarioGrupo.eliminado==False).first()
            if usuario_grupo is None:
                nuevo_usuario_grupo = UsuarioGrupo(
                    id=nuevoID,
                    id_grupo=group['id_grupo'],
                    id_usuario=id,
                    id_user_actualizacion= kwargs['id_user_actualizacion'],
                    fecha_actualizacion=datetime.now()
                )
                session.add(nuevo_usuario_grupo)

    if 'id_grupo' in kwargs:      
        nuevoID=uuid.uuid4()
        usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_usuario == id, UsuarioGrupo.id_grupo==kwargs['id_grupo']).first()
        if usuario_grupo is None:
            nuevo_usuario_grupo = UsuarioGrupo(
                id=nuevoID,
                id_grupo=kwargs['id_grupo'],
                id_usuario=id,
                id_user_actualizacion= kwargs['id_user_actualizacion'],
                fecha_actualizacion=datetime.now()
            )
            session.add(nuevo_usuario_grupo)

    session.commit()
    return usuario

def delete_usuario(id):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id, Usuario.eliminado==False).first()
    if usuario is None:
        return None
    
    usuario.eliminado = True
    usuario.fecha_actualizacion = datetime.now()
    session.commit()
    return usuario

