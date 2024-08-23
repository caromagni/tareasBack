# coding: utf-8
import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime
from ..common.functions import controla_fecha

from flask import current_app

from .alch_model import Tarea, TipoTarea, Usuario, TareaAsignadaUsuario, Grupo, TareaXGrupo


def insert_tarea(id_grupo=None, prioridad=0, id_actuacion=None, titulo='', cuerpo='', id_expediente=None, caratula_expediente='', id_tipo_tarea=None, eliminable=False, fecha_eliminacion=None, id_usuario_asignado=None, id_user_actualizacion=None, fecha_inicio=None, fecha_fin=None, plazo=0):

    
    session: scoped_session = current_app.session

    #fecha_inicio = controla_fecha(fecha_inicio)
    #fecha_fin = controla_fecha(fecha_fin)   
    print("fecha_inicio:",fecha_inicio)
    tipo_tarea = session.query(TipoTarea).filter(TipoTarea.id == id_tipo_tarea).first()
    if tipo_tarea is None:
       msg = "Tipo de tarea no encontrado"
       return None, msg

    nuevoID_tarea=uuid.uuid4()

    if id_grupo is not None:
        grupo = session.query(Grupo).filter(Grupo.id == id_grupo).first()
        if grupo is None:
            msg = "Grupo no encontrado"
            id_grupo=None
        else:    
            nuevoID_tareaxgrupo=uuid.uuid4()
            tareaxgrupo= TareaXGrupo(
                id=nuevoID_tareaxgrupo,
                id_grupo=id_grupo,
                id_tarea=nuevoID_tarea,
                id_user_actualizacion=id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )    

    
    print("nuevoID:",nuevoID_tarea)
    nueva_tarea = Tarea(
        id=nuevoID_tarea,
        id_grupo=id_grupo,
        prioridad=prioridad,
        id_actuacion=id_actuacion,
        titulo=titulo,
        cuerpo=cuerpo,
        id_expediente=id_expediente,
        caratula_expediente=caratula_expediente,
        id_tipo_tarea=id_tipo_tarea,
        eliminable=eliminable,
        id_usuario_asignado=id_usuario_asignado,
        id_user_actualizacion=id_user_actualizacion,
        fecha_eliminacion=fecha_eliminacion,
        fecha_actualizacion=datetime.now(),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fecha_creacion=datetime.now(),
        plazo=plazo
    )


    session.add(nueva_tarea)
    session.commit()
    print("Tarea ingresada:",nueva_tarea)
    return nueva_tarea


def get_all_tipo_tarea(page=1, per_page=10):
    print("get_tipo_tareas - ", page, "-", per_page)
    session: scoped_session = current_app.session
    todo = session.query(TipoTarea).all()
    total= len(todo)
    res = session.query(TipoTarea).order_by(TipoTarea.nombre).offset((page-1)*per_page).limit(per_page).all()
    return res, total

def insert_tipo_tarea(id='', codigo_humano='', nombre='', id_user_actualizacion=''):
    session: scoped_session = current_app.session
    nuevoID=uuid.uuid4()
    nuevo_tipo_tarea = TipoTarea(
        id=nuevoID,
        codigo_humano=codigo_humano,
        nombre=nombre,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now()
    )

    session.add(nuevo_tipo_tarea)
    session.commit()
    return nuevo_tipo_tarea

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
            "id_tipo_tarea": res.id_tipo_tarea,
            "tipo_tarea": res.tipo_tarea,
            "id_expediente": res.id_expediente,
            "expediente": res.expediente,
            "id_actuacion": res.id_actuacion,
            "actuacion": res.actuacion,
            "cuerpo": res.cuerpo,
            "eliminable": res.eliminable,
            "eliminado": res.eliminado,
            "fecha_eliminacion": res.fecha_eliminacion,
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

def get_all_tarea(page=1, per_page=10, titulo='', id_expediente=None, id_tipo_tarea=None, id_usuario_asignado=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now()):
    session: scoped_session = current_app.session
    query = session.query(Tarea).filter(Tarea.fecha_creacion.between(fecha_desde, fecha_hasta))
    if titulo != '':
        query = query.filter(Tarea.titulo.ilike(f'%{titulo}%'))
    if id_expediente is not None:
        query = query.filter(Tarea.id_expediente == id_expediente)
    if id_usuario_asignado is not None:
        query = query.filter(Tarea.id_usuario_asignado == id_usuario_asignado)
    if id_tipo_tarea is not None:
        query = query.filter(Tarea.id_tipo_tarea== id_tipo_tarea)

    total= query.count() 

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
              return None
        
        tarea.eliminado=True
        tarea.fecha_eliminacion=datetime.now()
        tarea.fecha_actualizacion=datetime.now()
        session.commit()
        return tarea
    
    else:
        print("Tarea no encontrada")
        return None
    



