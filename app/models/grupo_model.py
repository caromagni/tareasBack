import uuid
from sqlalchemy.orm import scoped_session, aliased
from datetime import datetime
from sqlalchemy import text, and_
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql
from apiflask.fields import Integer, String
from flask import current_app
from common.utils import *

from .alch_model import Grupo, HerarquiaGrupoGrupo, UsuarioGrupo, Usuario, TareaXGrupo, Tarea


def get_grupo_by_id(id):

    session: scoped_session = current_app.session
    res = session.query(Grupo).filter(Grupo.id == str(id)).first()
    #print("Grupo encontrado:", res.nombre)
    results=[]
    hijos=[]
    padres=[]
    usuarios=[]
    tareas=[]

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
                                    Usuario.apellido,
                                    UsuarioGrupo.eliminado).join(Usuario, Usuario.id == UsuarioGrupo.id_usuario  ).filter(UsuarioGrupo.id_grupo == res.id, UsuarioGrupo.eliminado==False).all()
        
        
        res_tarea = session.query(Tarea.id, 
                                    Tarea.titulo,
                                    Tarea.estado,
                                    Tarea.fecha_creacion,
                                    Tarea.fecha_inicio,
                                    Tarea.fecha_fin,
                                    Tarea.id_tipo_tarea,
                                    Tarea.tipo_tarea,
                                    Tarea.id_subtipo_tarea
                                ).join(TareaXGrupo, TareaXGrupo.id_tarea==Tarea.id).filter(TareaXGrupo.id_grupo==res.id).all()
        
        if res_hijos is not None:
            #print("tiene hijos")
            for row in res_hijos:
                hijo = {
                    "id_hijo": row.id_hijo,
                    "nombre_hijo": row.nombre,
                    "eliminado": row.eliminado
                }
                hijos.append(hijo)

        if res_padre is not None:
            #print("tiene padre")
            for row in res_padre:
                padre = {
                    "id_padre": row.id_padre,
                    "nombre_padre": row.nombre,
                    "eliminado": row.eliminado
                }
                padres.append(padre)

        if res_usuario is not None:
            #print("tiene usuarios")
            for row in res_usuario:
                usuario = {
                    "id": row.id,
                    "nombre": row.nombre,
                    "apellido": row.apellido,
                    "activo": not(row.eliminado)
                }
                usuarios.append(usuario)

        if res_tarea is not None:
            #print("tiene tareas: ", len(res_tarea))
            for row in res_tarea:
                tarea = {
                    "id": row.id,
                    "titulo": row.titulo,
                    "estado": row.estado,
                    #"subtipo_tarea": row.subtipo_tarea,
                    "id_tipo_tarea": row.id_tipo_tarea,
                    "id_subtipo_tarea": row.id_subtipo_tarea,
                    #"tipo_tarea": row.tipo_tarea,
                    "fecha_creacion": row.fecha_creacion,
                    "fecha_inicio": row.fecha_inicio,
                    "fecha_fin": row.fecha_fin
                    }
                tareas.append(tarea)        

        ###################Formatear el resultado####################
        results = {
            "id": res.id,
            "nombre": res.nombre,
            "descripcion": res.descripcion,
            "base": res.base,
            "eliminado": res.eliminado,
            "padre": padres,
            "hijos": hijos,
            "usuarios": usuarios,
            "tareas": tareas,
            "nomenclador": res.nomenclador,
            "id_user_actualizacion": res.id_user_actualizacion,
            "id_user_asignado_default": res.id_user_asignado_default,
            "fecha_actualizacion": res.fecha_actualizacion
        }
        #print("Resultado:", results)
        #results.append(result)
   
    
    return results    


def get_all_grupos_nivel(page=1, per_page=10, nombre="", fecha_desde='01/01/2000', fecha_hasta=datetime.now(), path_name=False, eliminado=False, suspendido=False):
    print ("Fecha desde:", fecha_desde)
    print ("Fecha hasta:", fecha_hasta)
    print("Tipo fecha desde:", type(fecha_desde))
    print("Tipo fecha hasta:", type(fecha_hasta))

    #fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
    #fecha_hasta = datetime.strftime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)
    
    cursor=None
    session: scoped_session = current_app.session
    # Subconsulta recursiva
    if path_name=='true':
        #print("Con consulta recursiva")
        subquery= text("""WITH RECURSIVE GroupTree AS (
                -- Anchor member: Start with all parentless nodes
                SELECT 
                    g.id AS id_padre,
                    g.id AS id_hijo,
                    g.descripcion AS parent_name,
                    g.descripcion AS child_name,
                    g.id::text AS path,
                    COALESCE(g.nombre, hgg1.id_hijo::text) AS path_name,
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
                    gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
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
                gt.path_name,
                gt.level,
                gt.is_parentless,
                gt.group_id  -- Include the new group ID column in the final select
            FROM 
                GroupTree gt
            ORDER BY 
                gt.path;""")
        
        result =[]
        cursor=session.execute(subquery)
    
    query= session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))
 
    if nombre is not "":
        query = query.filter(Grupo.nombre.ilike(f"%{nombre}%"))
    if eliminado:
        query = query.filter(Grupo.eliminado==eliminado)
    if suspendido:
        query = query.filter(Grupo.suspendido==suspendido)    

    total = len(query.all())

    if cursor:
        for reg in cursor:
            #print(reg.path_name)
            grupo=query.filter(Grupo.id==reg.id_hijo).first()
            if grupo is not None:
                #continue
                data = {
                    "id": reg.id_hijo,
                    "nombre": grupo.nombre,
                    "path": reg.path,
                    "path_name": reg.path_name,
                    "fecha_actualizacion": grupo.fecha_actualizacion,
                    "level": reg.level,
                    "descripcion": grupo.descripcion,
                    "nomenclador": grupo.nomenclador,
                    "codigo_nomenclador": grupo.codigo_nomenclador,
                    "fecha_creacion": grupo.fecha_creacion,
                    "id_user_actualizacion": grupo.id_user_actualizacion,
                    "id_user_asignado_default": grupo.id_user_asignado_default,
                    "user_asignado_default": grupo.user_asignado_default,
                    "eliminado": grupo.eliminado,
                    "suspendido": grupo.suspendido
                }

                result.append(data)

        start = (page - 1) * per_page
        end = start + per_page


    # Extraer los registros de la página actual
        result_paginated = result[start:end]
    else:
        result_paginated= query.order_by(Grupo.nombre).offset((page - 1) * per_page).limit(per_page)    

    #result = query.order_by(Grupo.nombre).offset((page - 1) * per_page).limit(per_page).all()

    return result_paginated, total
def encontrar_grupo_base(res_grupos, id):
    for r in res_grupos:
        if id == str(r['id_hijo']):
            print("############ENCONTRADO##############")
            if r['is_parentless']:
                print("GRUPO BASE ENCONTRADO:", r)
                return r  # Retornar el grupo base si es parentless
            else:
                print("PADRE:", r['id_padre'])
                # Llamada recursiva con el padre como nuevo ID
                return encontrar_grupo_base(res_grupos, str(r['id_padre']))    

def buscar_mismos_base(res_grupos, id, grupos_acumulados=None):
    if grupos_acumulados is None:
        grupos_acumulados = []

    hijos_directos = [r for r in res_grupos if r['id_padre'] == id]
    
    grupos_acumulados.extend(hijos_directos)    
    
    print ("Grupos acumulados:", hijos_directos)

    for hijo in hijos_directos:
        buscar_mismos_base(res_grupos, hijo['id_hijo'], grupos_acumulados)
    
    return grupos_acumulados
    
def get_all_base(id):
    cursor=None
    session: scoped_session = current_app.session
    # Subconsulta recursiva
    subquery = text("""
        WITH RECURSIVE GroupTree AS (
            -- Anchor member: Start with all parentless nodes
            SELECT 
                g.id AS id_padre,
                g.id AS id_hijo,
                g.descripcion AS parent_name,
                g.descripcion AS child_name,
                g.id::text AS path,
                COALESCE(g.nombre, g.id::text) AS path_name,
                0 AS level,
                true AS is_parentless,
                g.id AS group_id,
                g.base AS is_base
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
                gt.path || ',' || hgg.id_hijo::text AS path,
                gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
                gt.level + 1 AS level,
                false AS is_parentless,
                gp_hijo.id AS group_id,
                gp_padre.base AS is_base
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
            gt.path_name,
            gt.level,
            gt.is_parentless,
            gt.group_id,
            gt.is_base
        FROM 
            GroupTree gt
        ORDER BY 
            gt.path;
        """)

    # Ejecutar la subconsulta
    cursor = session.execute(subquery)
    
    result = cursor.fetchall()
    res_grupos=[]
    res=[]
    #print("Result:", result)
    #print('#'*50)
    for reg in result:
        #print(reg.group_id,"- id padre: ",reg.id_padre,"-id hijo:",reg.id_hijo,"-", reg.path_name,"-", reg.is_base, "-", reg.is_parentless)
        print(reg.path_name)
        data = {
            "id": reg.group_id,
            "id_padre": reg.id_padre,
            "id_hijo": reg.id_hijo,
            "path": reg.path,
            "path_name": reg.path_name,
            "is_parentless": reg.is_parentless,
        }    

        res_grupos.append(data)

    grupo_base = None
    
    grupo_base=encontrar_grupo_base(res_grupos, id)

    print("GRUPO BASE DE ID:", id,"-", grupo_base)
    grupos_mismo_base = []
    if grupo_base:
        # Filtrar los grupos con el mismo grupo base
        
        #grupos_mismo_base.append(buscar_mismos_base(res_grupos, grupo_base['id']))
        grupos_mismo_base = [r for r in res_grupos if r['id_padre'] == grupo_base['id']]
        #grupos_mismo_base = buscar_mismos_base(res_grupos, grupo_base['id'])
        print(grupos_mismo_base)
        for grupo in grupos_mismo_base:
            print(grupo['path_name'])
            data = {
                "id": grupo['id'],
                "id_padre": grupo['id_padre'],
                "id_hijo": grupo['id_hijo'],
                "path": grupo['path'],
                "path_name": grupo['path_name'],
                "is_parentless": grupo['is_parentless'],
                }
            
            res.append(data)
    else:
        print("No se encontró un grupo base para el ID proporcionado.")

    return res                                                                          
        
     

   
    #return res, i
   
def get_all_grupos(page=1, per_page=10, nombre="", fecha_desde='01/01/2000', fecha_hasta=datetime.now(), path_name=False): 
    #fecha_hasta = fecha_hasta + " 23:59:59"
    
    #fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
    #fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)
    
    session: scoped_session = current_app.session
    total= session.query(Grupo).count()

    query= session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))
    
    if nombre:
        query= query.filter(Grupo.nombre.ilike(f"%{nombre}%"))

    total= len(query.all()) 

    result= query.order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()  


    return result, total
    

def get_all_grupos_detalle(page=1, per_page=10, nombre="", fecha_desde='01/01/2000', fecha_hasta=datetime.now()): 
    #fecha_hasta = fecha_hasta + " 23:59:59"
    #fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
    #fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)
    
    session: scoped_session = current_app.session
    total= session.query(Grupo).count()

    query= session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))
    
    if nombre:
        query= query.filter(Grupo.nombre.ilike(f"%{nombre}%"))

    total= len(query.all()) 

    result= query.order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()  

    if result is not None:
        results=[]
        for res in result:
            usuarios=[]
            tareas=[]
           
            res_usuario = session.query(UsuarioGrupo.id_grupo,
                                        Usuario.id, Usuario.nombre, 
                                        Usuario.apellido, 
                                        Usuario.eliminado, 
                                        Usuario.suspendido, 
                                        Usuario.fecha_actualizacion
                        ).join(Usuario, Usuario.id==UsuarioGrupo.id_usuario).filter(UsuarioGrupo.id_grupo==res.id).all()
            
            res_tareas = session.query(TareaXGrupo.id_grupo, 
                                       Tarea.id, 
                                       Tarea.titulo, 
                                       Tarea.id_tipo_tarea,
                                       Tarea.id_subtipo_tarea,
                                      # Tarea.subtipo_tarea,
                                      # Tarea.tipo_tarea,
                                       Tarea.eliminado,
                                       Tarea.estado,
                                       Tarea.fecha_actualizacion
                                       ).join(Tarea, Tarea.id==TareaXGrupo.id_tarea
                                                   ).filter(TareaXGrupo.id_grupo==res.id).all()
            
            if res_usuario is not None:
                for row in res_usuario:
                    usuario = {
                        "apellido": row.apellido,
                        "nombre": row.nombre,
                        "id": row.id,
                        "eliminado": row.eliminado,
                        "suspendido": row.suspendido,
                        "fecha_actualizacion": row.fecha_actualizacion
                    }
                    usuarios.append(usuario)

            if res_tareas is not None:
                #print("Tiene tareas:", len(res_tareas))
                for row in res_tareas:
                    tarea = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "id_tipo_tarea": row.id_tipo_tarea,
                        "id_subtipo_tarea": row.id_subtipo_tarea,
                        "estado": row.estado,
                        #"subtipo_tarea": row.subtipo_tarea,
                        #"tipo_tarea": row.tipo_tarea,
                        "eliminado": row.eliminado,
                        "fecha_actualizacion": row.fecha_actualizacion
                    }
                    tareas.append(tarea)

            result = {
                "id": res.id,
                "nombre": res.nombre,
                "descripcion": res.descripcion,
                "nomenclador": res.nomenclador,
                "fecha_creacion": res.fecha_creacion,
                "fecha_actualizacion": res.fecha_actualizacion,
                "id_user_actualizacion": res.id_user_actualizacion,
                "id_user_asignado_default": res.id_user_asignado_default,
                "eliminado": res.eliminado,
                "suspendido": res.suspendido,
                "usuarios": usuarios,
                "tareas": tareas
            } 
                  
            results.append(result)

    return results, total


def get_all_herarquia():
    session: scoped_session = current_app.session
    res =session.query(HerarquiaGrupoGrupo).all()
    return res

def get_grupos_herarquia():
    session: scoped_session = current_app.session
    res=session.query(Grupo.id, Grupo.nombre, HerarquiaGrupoGrupo.id_hijo, HerarquiaGrupoGrupo.id_padre)\
        .join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre)\
        .all()
    #print(len(res))
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


def update_grupo(id='', **kwargs):
    session: scoped_session = current_app.session
    grupo = session.query(Grupo).filter(Grupo.id == id).first()
    if grupo is None:
        return None
    
    if grupo.eliminado:
        raise Exception("Grupo eliminado")
    
    if grupo.suspendido:
        raise Exception("Grupo suspendido")


    if 'nombre' in kwargs:
        grupo.nombre = kwargs['nombre']
    if 'descripcion' in kwargs:
        grupo.descripcion = kwargs['descripcion']
    if 'suspendido' in kwargs:
        grupo_con_tarea= session.query(TareaXGrupo).join(Tarea, Tarea.id==TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id, Tarea.estado==1 or Tarea.estado==1).all()
        if len(grupo_con_tarea)>0:
            raise Exception("No se puede suspender el grupo. El grupo tiene tareas sin cerrar")
        grupo.suspendido = kwargs['suspendido']
    
    if 'codigo_nomenclador' in kwargs:
        grupo.codigo_nomenclador = kwargs['codigo_nomenclador']  

    if 'id_user_actualizacion' in kwargs:
        usuario= session.query(Usuario).filter(Usuario.id==kwargs['id_user_actualizacion'], Usuario.eliminado==False).first()
        if usuario is None:
            raise Exception("Usuario de actualizacion no encontrado")
        
        grupo.id_user_actualizacion = kwargs['id_user_actualizacion']

    #print("Antes del if")

    if 'id_user_asignado_default' in kwargs:
        print("--Id user asignado default:", kwargs['id_user_asignado_default'])
        if(kwargs['id_user_asignado_default']==None):
             grupo.id_user_asignado_default = None
        else:     
            usuario= session.query(Usuario).filter(Usuario.id==kwargs['id_user_asignado_default'], Usuario.eliminado==False).first()
            if usuario is None:
                raise Exception("Usuario asignado default no encontrado")
            
            usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo==id, UsuarioGrupo.id_usuario==kwargs['id_user_asignado_default'], UsuarioGrupo.eliminado==False).first()
            if usuario_grupo is None:
                raise Exception("Usuario por defecto no asignado al grupo")

            grupo.id_user_asignado_default = kwargs['id_user_asignado_default']

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

    if 'usuario' in kwargs:
        #elimino los usuarios existentes para ese grupo
        usuario_grupo=session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo == id)
        for usr in usuario_grupo:
            usr.eliminado=True
            usr.fecha_actualizacion=datetime.now()
            usr.id_user_actualizacion=kwargs['id_user_actualizacion']
            
        for usuario in kwargs['usuario']:
            encuentra_usuario = session.query(Usuario).filter(Usuario.id==usuario['id_usuario']).first()
            if encuentra_usuario is None:
                raise Exception("Usuario no encontrado:" + usuario['id_usuario'])
            if encuentra_usuario.eliminado:
                raise Exception("Usuario eliminado:" + usuario['id_usuario'])
            
            usuario_grupo = session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo==id, UsuarioGrupo.id_usuario==usuario['id_usuario']).first()
            
            if usuario_grupo is None:
                #Agrego el usuario al grupo
                nuevo_usuario_grupo = UsuarioGrupo(
                    id=uuid.uuid4(),
                    id_grupo=id,
                    id_usuario=usuario['id_usuario'],
                    fecha_actualizacion=datetime.now(),
                    id_user_actualizacion=kwargs['id_user_actualizacion']
                )
                session.add(nuevo_usuario_grupo)
            else:
                #encuentra el usuario y lo reactiva 
                usuario_grupo.eliminado = False
                usuario_grupo.fecha_actualizacion = datetime.now()
                usuario_grupo.id_user_actualizacion = kwargs['id_user_actualizacion']    
                

    session.commit()
    return grupo

def insert_grupo(username=None, id='', nombre='', descripcion='', codigo_nomenclador='', id_user_actualizacion=None, id_padre=None, base=False, id_user_asignado_default=None):
    session: scoped_session = current_app.session
    #Validaciones
    if username is not None:
        id_user_actualizacion = verifica_username(username)

    if id_user_actualizacion is not None:
        verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    if id_user_asignado_default is not None:
        usuario = session.query(Usuario).filter(Usuario.id==id_user_asignado_default, Usuario.eliminado==False).first()
        if usuario is None: 
            raise Exception("Usuario de asignación de tareas no encontrado")

    if id_user_actualizacion is not None:
        usuario = session.query(Usuario).filter(Usuario.id==id_user_actualizacion, Usuario.eliminado==False).first()
        if usuario is None: 
            raise Exception("Usuario de actualización no encontrado")

    nuevoID_grupo=uuid.uuid4()
    nuevoID=uuid.uuid4()
    nuevo_grupo = Grupo(
        id=nuevoID_grupo,
        nombre=nombre.upper(),
        descripcion=descripcion,
        base=base,
        codigo_nomenclador=codigo_nomenclador,
        id_user_actualizacion=id_user_actualizacion,
        id_user_asignado_default=id_user_asignado_default,
        fecha_actualizacion=datetime.now(),
        fecha_creacion=datetime.now()
    )
    session.add(nuevo_grupo)

    #Agregar el usuario asignado por defecto al grupo
    if id_user_asignado_default is not None:
        nuevoID_usr_grp=uuid.uuid4()
        nuevo_usuario_grupo = UsuarioGrupo(
            id=nuevoID_usr_grp,
            id_grupo=nuevoID_grupo,
            id_usuario=id_user_asignado_default,
            fecha_actualizacion=datetime.now(),
            id_user_actualizacion=id_user_actualizacion
        )
        session.add(nuevo_usuario_grupo)

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
                  ).filter(Grupo.id == id, UsuarioGrupo.eliminado==False).all() 
                                       
    #print("Encontrados:",len(res))
    return res


def get_grupos_recursivo():
    session: scoped_session = current_app.session
    
    
    query = text("""WITH RECURSIVE GroupTree AS (
            -- Anchor member: Start with all parentless nodes
            SELECT 
                g.id AS id_padre,
                g.id AS id_hijo,
                g.descripcion AS parent_name,
                g.descripcion AS child_name,
                g.id::text AS path,
                COALESCE(g.nombre, hgg1.id_hijo::text) AS path_name,
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
                gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
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
            gt.path_name,
            gt.level,
            gt.is_parentless,
            gt.group_id  -- Include the new group ID column in the final select
        FROM 
            GroupTree gt
        ORDER BY 
            gt.path;""")
    res = session.execute(query).fetchall()
    return res



def get_grupos_all(eliminado=None):
    #print("eliminado:", eliminado)
    session: scoped_session = current_app.session
    query1 = text("""
  WITH RECURSIVE GroupTree AS (
    -- Anchor member: Start with all parentless nodes
    SELECT 
        g.id AS id_padre,
        g.id AS id_hijo,
        g.nombre AS parent_name,
        g.descripcion AS parent_description,            
        g.nombre AS child_name,
        g.descripcion AS child_description,
        g.eliminado AS child_eliminado,         
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
        gp_padre.nombre AS parent_name,
        gp_padre.descripcion AS parent_description,
        gp_hijo.nombre AS child_name,
        gp_hijo.descripcion AS child_description,
        gp_hijo.eliminado AS child_eliminado,         
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
    gt.parent_description,              
    gt.id_hijo,
    gt.child_name,
    gt.child_description,
    gt.child_eliminado,             
    gt.path,
    gt.level,
    gt.is_parentless,
    gt.group_id  -- Include the new group ID column in the final select
FROM 
    GroupTree gt
WHERE 
    gt.child_eliminado = :eliminado   
ORDER BY gt.path;                                 
  """)
    query_str = (
        'WITH RECURSIVE GroupTree AS ('
        'SELECT '
        'g.id AS id_padre, '
        'g.id AS id_hijo, '
        'g.nombre AS parent_name, '
        'g.descripcion AS parent_description, '
        'g.nombre AS child_name, '
        'g.descripcion AS child_description, '
        'g.eliminado AS child_eliminado, '
        'g.id::text AS path, '
        '0 AS level, '  # Nivel 0 para grupos sin padre
        'true AS is_parentless, '
        'g.id AS group_id '
        'FROM tareas.grupo g '
        'LEFT JOIN tareas.herarquia_grupo_grupo hgg1 ON g.id = hgg1.id_hijo '
        'WHERE hgg1.id_hijo IS NULL '
        'UNION ALL '
        'SELECT '
        'hgg.id_padre, '
        'hgg.id_hijo, '
        'gp_padre.nombre AS parent_name, '
        'gp_padre.descripcion AS parent_description, '
        'gp_hijo.nombre AS child_name, '
        'gp_hijo.descripcion AS child_description, '
        'gp_hijo.eliminado AS child_eliminado, '
        'gt.path || \' -> \' || hgg.id_hijo::text AS path, '
        'gt.level + 1 AS level, '
        'false AS is_parentless, '
        'gp_hijo.id AS group_id '
        'FROM tareas.herarquia_grupo_grupo hgg '
        'INNER JOIN GroupTree gt ON gt.id_hijo = hgg.id_padre '
        'INNER JOIN tareas.grupo gp_padre ON hgg.id_padre = gp_padre.id '
        'INNER JOIN tareas.grupo gp_hijo ON hgg.id_hijo = gp_hijo.id '
        ') '
        'SELECT '
        'gt.id_padre, '
        'gt.parent_name, '
        'gt.parent_description, '
        'gt.id_hijo, '
        'gt.child_name, '
        'gt.child_description, '
        'gt.child_eliminado, '
        'gt.path, '
        'gt.level, '
        'gt.is_parentless, '
        'gt.group_id '
        'FROM GroupTree gt '
    )

    if eliminado is not None:
        query_str += ' WHERE gt.child_eliminado = :eliminado'

    query_str += ' ORDER BY gt.path;'

    query = text(query_str)

    # Ejecutar la consulta con el parámetro `eliminado` si es necesario
    if eliminado is not None:
        res = session.execute(query, {"eliminado": eliminado}).fetchall()
    else:
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
    #print("Borrando grupo con id:", id)
    session = current_app.session
    grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
    if grupo is None:
        raise Exception("Grupo no encontrado")
    
    grupo_con_tarea= session.query(TareaXGrupo).join(Tarea, Tarea.id==TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id, Tarea.estado==1 or Tarea.estado==1).all()
    if len(grupo_con_tarea)>0:
        raise Exception("No se puede eliminar el grupo. El grupo tiene tareas sin cerrar")
       
    if todos:
        # Eliminar todos los hijos
        #print("Eliminar todos los hijos")
        eliminar_grupo_recursivo(id)
        grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
        if grupo:
            grupo.eliminado = True

    else:    
        # Eliminar solo el grupo
        #print("Eliminar solo el grupo")
        tiene_hijos = session.query(HerarquiaGrupoGrupo).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_hijo).filter(HerarquiaGrupoGrupo.id_padre == id, Grupo.eliminado==False).all()
        #print("Tiene hijos:", tiene_hijos)
        if len(tiene_hijos)>0:
            #for hijo in tiene_hijos:
                 #print("El grupo tiene hijos - id_padre:", hijo.id_padre, "-id_hijo:", hijo.id_hijo)

            raise Exception("El grupo tiene hijos")
                    
        grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
        if grupo:
            grupo.eliminado = True
        else:
            #print("No se encontró el grupo a eliminar")
            raise Exception("No se encontró el grupo a eliminar")
            

    session.commit()

    return grupo

def undelete_grupo(id):
    session = current_app.session
    grupo = session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == True).first()
    if grupo is None:
        raise Exception("Grupo no encontrado")
    grupo.eliminado = False
    session.commit()
    return grupo    