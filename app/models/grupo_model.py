import uuid
from sqlalchemy.orm import scoped_session, aliased
from datetime import datetime
from sqlalchemy import text

from flask import current_app

from .alch_model import Grupo, HerarquiaGrupoGrupo, UsuarioGrupo, Usuario


""" def get_all_grupos():
    session: scoped_session = current_app.session
    res =session.query(Grupo).offset(0).limit(3).all()
    cant=session.query(Grupo).count()
    return res, cant """

def get_all_grupos(first=1, rows=10): #if no arguments are passed, the default values are used
    session: scoped_session = current_app.session
    total= session.query(Grupo).count()
    result= session.query(Grupo).offset((first-1)*rows).limit(rows).all()
    return result, total

def get_all_herarquia():
    session: scoped_session = current_app.session
    res =session.query(HerarquiaGrupoGrupo).all()
    return res

def get_grupos_herarquia():
    session: scoped_session = current_app.session
    res=session.query(Grupo.id, Grupo.nombre, HerarquiaGrupoGrupo.id_hijo, HerarquiaGrupoGrupo.id_padre)\
        .join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre)\
        .all()
    print(len(res))
    return res

def get_grupos_herarquia_labels():
    GrupoPadre = aliased(Grupo)
    GrupoHijo = aliased(Grupo)
    session: scoped_session = current_app.session
    
    # Realizar la consulta con los joins necesarios
    res = session.query(
            Grupo.id.label("id"),
            Grupo.id_user_actualizacion.label("user_actualizacion"),
            Grupo.fecha_actualizacion.label("fecha_actualizacion"),
            Grupo.nombre.label("nombre"),
            HerarquiaGrupoGrupo.id.label("herarquia_grupo_grupo_id"),
            HerarquiaGrupoGrupo.id_padre.label("id_padre"),
            GrupoPadre.nombre.label("nombre_padre"),
            HerarquiaGrupoGrupo.id_hijo.label("id_hijo"),
            GrupoHijo.nombre.label("nombre_hijo"),
            HerarquiaGrupoGrupo.id_user_actualizacion.label("tareas_herarquia_grupo_grupo_id_user_actualizacion"),
            HerarquiaGrupoGrupo.fecha_actualizacion.label("tareas_herarquia_grupo_grupo_fecha_actualizacion")
        ).join(
            HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre
        ).join(
        GrupoPadre, HerarquiaGrupoGrupo.id_padre == GrupoPadre.id
    ).join(
        GrupoHijo, HerarquiaGrupoGrupo.id_hijo == GrupoHijo.id
    ).all()
    
    return res                                                                 

def update_grupo(id='', nombre='', descripcion='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    grupos = session.query(Grupo).filter(Grupo.id == id).first()
   
    if grupos is None:
        return None

    if descripcion != '':
        grupos.descripcion = descripcion    

    update_data = {}
    if nombre != '':
        update_data[Grupo.nombre] = nombre
    if descripcion != '':
        update_data[Grupo.descripcion] = descripcion

    update_data[Grupo.id_user_actualizacion] = id_user_actualizacion
    update_data[Grupo.fecha_actualizacion] = datetime.now()          

    print("Grupo encontrado:",grupos)
   # session.query(Grupo).filter(Grupo.id == id).update({Grupo.nombre: nombre,
   #     Grupo.id_user_actualizacion: id_user_actualizacion,
   #     Grupo.fecha_actualizacion: datetime.now()})
   
    session.query(Grupo).filter(Grupo.id == id).update(update_data)

    session.commit()
    return grupos

def insert_grupo(id='', nombre='', descripcion='', id_user_actualizacion='', id_padre=''):
    session: scoped_session = current_app.session
    nuevoID_grupo=uuid.uuid4()
    nuevoID=uuid.uuid4()
    print(nuevoID)
    nuevo_grupo = Grupo(
        id=nuevoID_grupo,
        nombre=nombre,
        descripcion=descripcion,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )
    session.add(nuevo_grupo)

    if id_padre is not '':        
        nueva_herarquia = HerarquiaGrupoGrupo(
            id=nuevoID,
            id_padre=id_padre,
            id_hijo=nuevoID_grupo,
            id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )
        session.add(nueva_herarquia)
    
    session.commit()
    
    return nuevo_grupo


def get_usuarios_by_grupo(id):
    session: scoped_session = current_app.session
    res = session.query(Grupo.id.label("id_grupo"),
                  Grupo.nombre.label("nombre_grupo"),
                  Usuario.nombre.label("nombre"),
                  Usuario.apellido.label("apellido"),
                  Usuario.id.label("id_usuario")                  
                  ).join(UsuarioGrupo, Grupo.id == UsuarioGrupo.id_grupo
                  ).join(Usuario, UsuarioGrupo.id_usuario == Usuario.id
                  ).filter(Grupo.id == id).all()                                    
    print("Encontrados:",len(res))
    return res


def get_grupos_recursivo():
    session: scoped_session = current_app.session
    query = text("""
                WITH RECURSIVE GroupTree AS ( SELECT  hgg1.id_padre, hgg1.id_hijo, 
                hgg1.id_hijo::text AS path, 1 AS level FROM tareas.herarquia_grupo_grupo hgg1
                WHERE hgg1.id_padre IS NULL
                OR NOT EXISTS ( SELECT 1 FROM tareas.herarquia_grupo_grupo hgg2
                WHERE hgg2.id_hijo = hgg1.id_padre)  
                UNION ALL
                SELECT hgg.id_padre, hgg.id_hijo, gt.path || ' -> ' || hgg.id_hijo::text AS path,
                gt.level + 1 AS level
                FROM tareas.herarquia_grupo_grupo hgg
                INNER JOIN GroupTree gt ON gt.id_hijo = hgg.id_padre)
                SELECT gt.id_padre, gp_padre.nombre AS nombre_padre, gt.id_hijo, gp_hijo.nombre AS nombre_hijo,
                gt.path, gt.level FROM GroupTree gt LEFT JOIN tareas.grupo gp_padre ON gt.id_padre = gp_padre.id
                LEFT JOIN tareas.grupo gp_hijo ON gt.id_hijo = gp_hijo.id ORDER BY gt.path""")
    
    res = session.execute(query).fetchall()
    return res
    