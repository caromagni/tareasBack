import uuid
from sqlalchemy.orm import scoped_session, aliased
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from flask import current_app

from .alch_model import Grupo, HerarquiaGrupoGrupo, UsuarioGrupo, Usuario, Nomenclador


def get_grupo_by_id(id):

    session: scoped_session = current_app.session
    res = session.query(Grupo).filter(Grupo.id == str(id)).first()
    print("Grupo encontrado:", res.nombre)
    results=[]
    hijos=[]
    padres=[]
    usuarios=[]

    if res is not None:
        #Traigo el padre
        res_padre = session.query(HerarquiaGrupoGrupo.id_padre, Grupo.nombre, Grupo.eliminado
                                  ).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_padre).filter(HerarquiaGrupoGrupo.id_hijo == res.id).all()
        
        #Traigo los grupos hijos
        res_hijos = session.query(HerarquiaGrupoGrupo.id_hijo, Grupo.nombre, Grupo.eliminado
                                  ).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_hijo).filter(HerarquiaGrupoGrupo.id_padre == res.id).all()
        
        res_usuario = session.query(UsuarioGrupo.id,
                                    UsuarioGrupo.id_grupo,
                                    UsuarioGrupo.id_usuario,
                                    Usuario.id,
                                    Usuario.nombre,
                                    Usuario.apellido).join(Usuario, Usuario.id == UsuarioGrupo.id_usuario  ).filter(UsuarioGrupo.id_grupo == res.id).all()
        
        if res_hijos is not None:
            print("tiene hijos")
            for row in res_hijos:
                hijo = {
                    "id_hijo": row.id_hijo,
                    "nombre_hijo": row.nombre,
                    "eliminado": row.eliminado
                }
                hijos.append(hijo)

        if res_padre is not None:
            print("tiene padre")
            for row in res_padre:
                padre = {
                    "id_padre": row.id_padre,
                    "nombre_padre": row.nombre,
                    "eliminado": row.eliminado
                }
                padres.append(padre)

        if res_usuario is not None:
            print("tiene usuarios")
            for row in res_usuario:
                usuario = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido
                }
                usuarios.append(usuario)

        ###################Formatear el resultado####################
        results = {
            "id": res.id,
            "nombre": res.nombre,
            "descripcion": res.descripcion,
            "eliminado": res.eliminado,
            "padre": padres,
            "hijos": hijos,
            "usuarios": usuarios,
            "nomenclador": res.nomenclador
        }
        print("Resultado:", results)
        #results.append(result)
   
    
    return results    

    

    

def get_all_grupos(page=1, per_page=10, nombre="", fecha_desde='01/01/2000', fecha_hasta=datetime.now()): #if no arguments are passed, the default values are used
    session: scoped_session = current_app.session
    total= session.query(Grupo).count()
    print("fecha_desde:",fecha_desde)
    print("fecha_hasta:",fecha_hasta)
    if nombre != "":
        #result= session.query(Grupo).filter(Grupo.nombre == nombre, Grupo.fecha_actualizacion.between(fecha_desde, fecha_hasta)).offset((page-1)*per_page).limit(per_page).all()
        result = session.query(Grupo).filter(
            Grupo.nombre.ilike(f"%{nombre}%"),
            Grupo.fecha_actualizacion.between(fecha_desde, fecha_hasta)
        ).order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()
        todo= session.query(Grupo).filter(
            Grupo.nombre.ilike(f"%{nombre}%"),
            Grupo.fecha_actualizacion.between(fecha_desde, fecha_hasta)
        ).all()
        total= len(todo)
    else:
        result= session.query(Grupo).filter(
            Grupo.fecha_actualizacion.between(fecha_desde, fecha_hasta)
        ).order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()
        todo= session.query(Grupo).filter(
            Grupo.fecha_actualizacion.between(fecha_desde, fecha_hasta)).all()
        total= len(todo)
        
        
    #result= session.query(Grupo).offset((page-1)*per_page).limit(per_page).all()
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

""" def update_grupo(id='', nombre='', descripcion='', codigo_nomenclador='', id_user_actualizacion='', id_padre=''):
    session: scoped_session = current_app.session
    grupos = session.query(Grupo).filter(Grupo.id == id).first()
   
    if grupos is None:
        return None

    update_data = {}
    if nombre != '':
        update_data[Grupo.nombre] = nombre
    if descripcion != '':
        update_data[Grupo.descripcion] = descripcion
    if codigo_nomenclador != '':
        update_data[Grupo.codigo_nomenclador] = codigo_nomenclador


    update_data[Grupo.id_user_actualizacion] = id_user_actualizacion
    update_data[Grupo.fecha_actualizacion] = datetime.now()          

    session.query(Grupo).filter(Grupo.id == id).update(update_data)
    
    #Update de id_padre
    if id_padre != '':   
        herarquia = session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo==id).first()      
        if herarquia is not None:
            update_data={}
            update_data[HerarquiaGrupoGrupo.id_padre] = id_padre
            update_data[HerarquiaGrupoGrupo.id_user_actualizacion] = id_user_actualizacion
            update_data[HerarquiaGrupoGrupo.fecha_actualizacion] = datetime.now()
            session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo==id).update(update_data)
            # session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo==id).update(
            #     id_padre=id_padre, 
            #     id_user_actualizacion =id_user_actualizacion,
            #     fecha_actualizacion=datetime.now())


    session.commit()
    return grupos """

def update_grupo(id='', **kwargs):
    session: scoped_session = current_app.session
    grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado==False).first()

    if grupo is None:
        return None

    print("Grupo encontrado:", grupo)

    if 'nombre' in kwargs:
        grupo.nombre = kwargs['nombre']
    if 'descripcion' in kwargs:
        grupo.descripcion = kwargs['descripcion']
    if 'codigo_nomenclador' in kwargs:
        grupo.codigo_nomenclador = kwargs['codigo_nomenclador']  
    if 'id_user_actualizacion' in kwargs:
        grupo.id_user_actualizacion = kwargs['id_user_actualizacion']

    # Siempre actualizar la fecha de actualización
    grupo.fecha_actualizacion = datetime.now()
    
    if 'id_padre' in kwargs:
        herarquia = session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo==id).first()      
        if herarquia is None:
            nueva_herarquia = HerarquiaGrupoGrupo(
                id=uuid.uuid4(),
                id_padre=kwargs['id_padre'],
                id_hijo=id,
                id_user_actualizacion=kwargs['id_user_actualizacion'],
                fecha_actualizacion=datetime.now()
            )
            session.add(nueva_herarquia)
        else:
            herarquia.id_padre = kwargs['id_padre']
            herarquia.id_user_actualizacion = kwargs['id_user_actualizacion']
            herarquia.fecha_actualizacion = datetime.now()

    session.commit()
    return grupo

def insert_grupo(id='', nombre='', descripcion='', codigo_nomenclador='', id_user_actualizacion='', id_padre=''):
    session: scoped_session = current_app.session
    nuevoID_grupo=uuid.uuid4()
    nuevoID=uuid.uuid4()
    nuevo_grupo = Grupo(
        id=nuevoID_grupo,
        nombre=nombre.upper(),
        descripcion=descripcion,
        codigo_nomenclador=codigo_nomenclador,
        id_user_actualizacion=id_user_actualizacion,
        fecha_actualizacion=datetime.now(),
        fecha_creacion=datetime.now()
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



def get_grupos_all():
    session: scoped_session = current_app.session
    query = text("""
  WITH RECURSIVE GroupTree AS (
    -- Anchor member: Start with all parentless nodes
    SELECT 
        g.id AS id_padre,
        g.id AS id_hijo,
        g.descripcion AS parent_name,
        g.descripcion AS child_name,
        g.id::text AS path,
        0 AS level,  -- Set level to 0 for parentless groups
        true AS is_parentless,
        g.id AS group_id  -- Add the group ID column
    FROM 
        tareas.grupo g
    LEFT JOIN 
        tareas.herarquia_grupo_grupo hgg1 ON g.id = hgg1.id_hijo
    WHERE 
        hgg1.id_hijo IS NULL

    UNION ALL

    -- Recursive member: Join with the hierarchical table to find child groups
    SELECT 
        hgg.id_padre,
        hgg.id_hijo,
        gp_padre.descripcion AS parent_name,
        gp_hijo.descripcion AS child_name,
        gt.path || ' -> ' || hgg.id_hijo::text AS path,
        gt.level + 1 AS level,
        false AS is_parentless,
        gp_hijo.id AS group_id  -- Add the group ID column for children
    FROM 
        tareas.herarquia_grupo_grupo hgg
    INNER JOIN 
        GroupTree gt ON gt.id_hijo = hgg.id_padre
    INNER JOIN 
        tareas.grupo gp_padre ON hgg.id_padre = gp_padre.id
    INNER JOIN 
        tareas.grupo gp_hijo ON hgg.id_hijo = gp_hijo.id
)

-- Select from the CTE to get the full hierarchy
SELECT 
    gt.id_padre,
    gt.parent_name,
    gt.id_hijo,
    gt.child_name,
    gt.path,
    gt.level,
    gt.is_parentless,
    gt.group_id  -- Include the new group ID column in the final select
FROM 
    GroupTree gt
ORDER BY 
    gt.path;





                """)
    
    res = session.execute(query).fetchall()
    return res


def eliminar_grupo_recursivo(id):

    session: scoped_session = current_app.session
    hijos = session.query(Grupo.id,
                  Grupo.eliminado,          
                  HerarquiaGrupoGrupo.id_padre,
                  HerarquiaGrupoGrupo.id_hijo
                  ).join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre
                  ).filter(Grupo.id == id, Grupo.eliminado==False).all() 
    
    if not hijos:
        return
    
    for hijo in hijos:
        if not hijo.eliminado:
            eliminar_grupo_recursivo(hijo.id_hijo)
            grupo = session.query(Grupo).filter(Grupo.id == hijo.id_hijo, Grupo.eliminado==False).first()
            if grupo is not None:
                grupo.eliminado = True
                session.add(grupo)

    

def delete_grupo(id,todos=False):
    print("Borrando grupo con id:", id)
    session = current_app.session
    try:
        if todos:
            # Eliminar todos los hijos
            eliminar_grupo_recursivo(id)
            grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
            if grupo:
                grupo.eliminado = True
                session.add(grupo)
        else:    
            # Eliminar solo el grupo
            grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
            if grupo:
                grupo.eliminado = True
                session.add(grupo)
            else:
                print("No se encontró el grupo a eliminar")
                return None

        session.commit()
    except Exception as e:
        session.rollback()
        print(f'Error al eliminar el grupo: {e}')
        return None

    return grupo
    