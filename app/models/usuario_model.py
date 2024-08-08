import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import Usuario, UsuarioGrupo, Grupo, TareaAsignadaUsuario, Tarea


def get_usuario_by_id(id):
    session: scoped_session = current_app.session
    
    res = session.query(Usuario).filter(Usuario.id == id).first()
    
    results = []
    tareas=[]
    grupos=[]
 

    if res is not None:
        #Traigo los grupos del usuario
        res_grupos = session.query(UsuarioGrupo.id_usuario, Grupo.id, Grupo.nombre
                                  ).join(Grupo, Grupo.id==UsuarioGrupo.id_grupo).filter(UsuarioGrupo.id_usuario== res.id).all()
        
        #Traigo los grupos hijos
        res_tareas = session.query(TareaAsignadaUsuario.id_usuario, Tarea.id, Tarea.titulo
                                  ).join(Tarea, Tarea.id==TareaAsignadaUsuario.id_usuario).filter(TareaAsignadaUsuario.id_usuario== res.id).all()
        

        if res_tareas is not None:
            for row in res_tareas:
                tarea = {
                    "id": row.id,
                    "titulo": row.titulo
                }
                tareas.append(tarea)

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
            "nombre": res.nombre,
            "apellido": res.apellido,
            "grupos": grupos,
            "tareas": tareas
        }

        results.append(result)
   
    else:
        return None
    
    return results 

def get_all_usuarios():
    session: scoped_session = current_app.session
    return session.query(Usuario).all()

def get_grupos_by_usuario(id):
    session: scoped_session = current_app.session
    res = session.query(Usuario.id.label("id_usuario"),
                  Usuario.nombre.label("nombre"),
                  Usuario.apellido.label("apellido"),
                  Grupo.id.label("id_grupo"),
                  Grupo.nombre.label("nombre_grupo")
                  ).join(UsuarioGrupo, Usuario.id == UsuarioGrupo.id_usuario
                  ).join(Grupo, UsuarioGrupo.id_grupo == Grupo.id).filter(Usuario.id == id).all()                                    
    
    return res




def insert_usuario(id='', nombre='', apellido='', id_persona_ext=None, id_grupo=None, id_user_actualizacion=None):
    session: scoped_session = current_app.session
    nuevoID_usuario=uuid.uuid4()
    print("nuevo_usuario:",nuevoID_usuario)
    nuevo_usuario = Usuario(
        id=nuevoID_usuario,
        nombre=nombre,
        apellido=apellido,
        id_persona_ext=id_persona_ext,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    print("nuevo_usuario:",nuevo_usuario)
    session.add(nuevo_usuario)
    
    if id_grupo is not '':        
        nuevoID=uuid.uuid4()
        nuevo_usuario_grupo = UsuarioGrupo(
            id=nuevoID,
            id_grupo=id_grupo,
            id_usuario=nuevoID_usuario,
            #id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )

        session.add(nuevo_usuario_grupo)
    
    session.commit()

    return nuevo_usuario


def update_usuario(id='', **kwargs):
    session: scoped_session = current_app.session
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
   
    if usuario is None:
        return None
    
    print("Usuario encontrado:",usuario)

    update_data = {}
    if 'nombre' in kwargs:
        usuario.nombre = kwargs['nombre']
    if 'apellido' in kwargs:
        usuario.apellido = kwargs['apellido']
    if 'id_persona_ext' in kwargs:
        usuario.id_persona_ext = kwargs['id_persona_ext']
    if 'id_user_actualizacion' in kwargs:
        usuario.id_user_actualizacion = kwargs['id_user_actualizacion']

    usuario.fecha_actualizacion = datetime.now()

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

