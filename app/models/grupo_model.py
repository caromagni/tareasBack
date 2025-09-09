import uuid
from sqlalchemy.orm import aliased
from datetime import datetime
from sqlalchemy import text, desc
import common.utils as utils
import common.logger_config as logger_config
from db.alchemy_db import db
from .alch_model import Grupo, HerarquiaGrupoGrupo, UsuarioGrupo, Usuario, TareaXGrupo, Tarea, Organismo, Dominio
from common.cache import *
import common.cache as cache_common
from datetime import time
import common.functions as functions
#import decorators.cache_error_wrapper as cache_error_wrapper

@cache_common.cache.memoize(CACHE_TIMEOUT_LONG)
def get_grupo_by_id(id):

    res = db.session.query(Grupo).filter(Grupo.id == str(id)).first()
    results=[]
    hijos=[]
    padres=[]
    usuarios=[]
    tareas=[]

    if res is not None:
        #Traigo el padre
        res_padre = db.session.query(HerarquiaGrupoGrupo.id_padre, Grupo.nombre, Grupo.eliminado
                                  ).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_padre).filter(HerarquiaGrupoGrupo.id_hijo == res.id).all()
        
        #Traigo los grupos hijos
        res_hijos = db.session.query(HerarquiaGrupoGrupo.id_hijo, Grupo.nombre, Grupo.eliminado
                                  ).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_hijo).filter(HerarquiaGrupoGrupo.id_padre == res.id).all()
        
        res_usuario = db.session.query(UsuarioGrupo.id,
                                    UsuarioGrupo.id_grupo,
                                    UsuarioGrupo.id_usuario,
                                    Usuario.id,
                                    Usuario.nombre,
                                    Usuario.apellido,
                                    UsuarioGrupo.eliminado).join(Usuario, Usuario.id == UsuarioGrupo.id_usuario  
                                ).filter(UsuarioGrupo.id_grupo == res.id, UsuarioGrupo.eliminado==False
                                ).order_by(Usuario.apellido).all()
        
        
        res_tarea = db.session.query(Tarea
                                ).join(TareaXGrupo, TareaXGrupo.id_tarea==Tarea.id
                                ).filter(TareaXGrupo.id_grupo==res.id and TareaXGrupo.eliminado==False
                                ).order_by(desc(Tarea.fecha_creacion)).all()
        
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
            tareas=[]

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
            "id_dominio": res.id_dominio_ext,
            "id_organismo": res.id_organismo_ext,
            "organismo": res.organismo,
            "dominio": res.dominio,
            "id_user_actualizacion": res.id_user_actualizacion,
            "id_user_asignado_default": res.id_user_asignado_default,
            "fecha_actualizacion": res.fecha_actualizacion
        }
        #print("Resultado:", results)
        #results.append(result)
   
    
    return results    

@cache.memoize(CACHE_TIMEOUT_LONG)
def exececuteSubquery(subquery):
    """
    Ejecuta una subconsulta y devuelve los resultados en formato serializable.
    """
    try:
        cursor = db.session.execute(subquery)
        # Use cursor.mappings() to get rows as dictionary-like objects
        results = [dict(row) for row in cursor.mappings()]
        return results
    except Exception as e:
        logger_config.logger.error(f"Error executing subquery: {e}")
        raise e
    
#################################################PRUEBA ######################################################
#def get_all_grupos_nivel_prueba(username=None, page=1, per_page=10, nombre="", fecha_desde=None, fecha_hasta=None, path_name=None, eliminado=False, suspendido=False, todos=True):


#@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_grupos_nivel(username=None, page=1, per_page=10, nombre="", fecha_desde=None, fecha_hasta=None, path_name=None, eliminado=False, suspendido=False, todos=True, id_dominio=None, id_organismo=None):
    """
    Obtiene todos los grupos con nivel jerárquico, con soporte para caché.
    """
    if username is not None:
        id_user = utils.get_username_id(username)

    if id_user is not None:
        utils.verifica_usr_id(id_user)
    else:
        logger_config.logger.error("Id de usuario no ingresado")

    # Parse and normalize date filters
    fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y').date() if fecha_desde else datetime.strptime("30/01/1900", "%d/%m/%Y").date()
    fecha_desde = datetime.combine(fecha_desde, time.min)
    fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y') if fecha_hasta else datetime.now()
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())

    #valido que fecha_dsde no sea mayor a fecha_hasta
    if fecha_desde > fecha_hasta:
        raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")
    
    print("TIMETRACK_INITIAL:", datetime.now())
    print("Fecha desde:", fecha_desde)
    print("Fecha hasta:", fecha_hasta)
    print("Eliminado:", eliminado)
    print("Suspendido:", suspendido)
    print("Path name:", path_name)
    print("Tipo de datos de fechas:",type(fecha_desde), "-",type(fecha_hasta))
    result = []

    # Subconsulta recursiva
    if path_name is True or path_name == 'true':
        
        params = {
            "nombre": nombre or None,
            "eliminado": eliminado if eliminado is not None else None,
            "suspendido": suspendido if suspendido is not None else None,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "id_dominio": id_dominio,
            "id_organismo": id_organismo
        }
        #COALESCE(g.nombre, g.id::text) AS path_name,
        subquery1 = text("""
            WITH RECURSIVE GroupTree AS (
                -- Parte base: todos los grupos, incluso si no están en la jerarquía
                SELECT 
                    g.id AS id_padre,
                    g.id AS id_hijo,
                    g.descripcion AS parent_name,
                    g.descripcion AS child_name,
                    g.id::text AS path,
                    COALESCE(g.nombre, g.id::text) AS path_name,
                    0 AS level,
                    NOT EXISTS (SELECT 1 FROM tareas.herarquia_grupo_grupo hgg WHERE hgg.id_hijo = g.id) AS is_parentless,
                    g.id AS group_id,
                    g.eliminado AS eliminado_hijo,
                    g.suspendido AS suspendido_hijo,    
                    g.nombre AS nombre_hijo,
                    g.descripcion AS descripcion_hijo,
                    g.id_dominio_ext AS id_dominio_hijo,
                    g.id_organismo_ext AS id_organismo_hijo,
                    g.fecha_actualizacion AS fecha_actualizacion_hijo,
                    g.fecha_creacion AS fecha_creacion_hijo,    
                    g.base AS base_hijo,    
                    NULL::boolean AS eliminado_padre,
                    NULL::boolean AS suspendido_padre,    
                    NULL::text AS nombre_padre,
                    NULL::text AS descripcion_padre,
                    NULL::text AS id_dominio,
                    NULL::text AS id_organismo,
                    NULL::timestamp AS fecha_actualizacion_padre,
                    NULL::timestamp AS fecha_creacion_padre,    
                    NULL::boolean AS base_padre     
                FROM tareas.grupo g
                WHERE 
                    (:nombre IS NULL OR g.nombre ILIKE '%' || :nombre || '%')
                    AND (:eliminado IS NULL OR g.eliminado = :eliminado)
                    AND (:suspendido IS NULL OR g.suspendido = :suspendido)
                    AND (:id_dominio IS NULL OR g.id_dominio_ext = :id_dominio)
                    AND (:id_organismo IS NULL OR g.id_organismo_ext = :id_organismo)
                    AND (:fecha_desde IS NULL OR g.fecha_actualizacion >= :fecha_desde)
                    AND (:fecha_hasta IS NULL OR g.fecha_actualizacion <= :fecha_hasta)         

                UNION ALL

                -- Parte recursiva: sigue relaciones padre → hijo
                SELECT 
                    hgg.id_padre,
                    hgg.id_hijo,
                    gp_padre.descripcion AS parent_name,
                    gp_hijo.descripcion AS child_name,
                    gt.path || ' -> ' || hgg.id_hijo::text AS path,
                    gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
                    gt.level + 1 AS level,
                    false AS is_parentless,
                    gp_hijo.id AS group_id,
                    gp_hijo.eliminado AS eliminado_hijo,
                    gp_hijo.suspendido AS suspendido_hijo,    
                    gp_hijo.nombre AS nombre_hijo,
                    gp_hijo.descripcion AS descripcion_hijo,
                    gp_hijo.id_dominio_ext AS id_dominio_hijo,
                    gp_hijo.id_organismo_ext AS id_organismo_hijo,
                    gp_hijo.fecha_actualizacion AS fecha_actualizacion_hijo,
                    gp_hijo.fecha_creacion AS fecha_creacion_hijo,
                    gp_hijo.base AS base_hijo,    
                    gp_padre.eliminado AS eliminado_padre,
                    gp_padre.suspendido AS suspendido_padre,    
                    gp_padre.nombre AS nombre_padre,
                    gp_padre.descripcion AS descripcion_padre,
                    gp_padre.id_dominio_ext AS id_dominio_padre,
                    gp_padre.id_organismo_ext AS id_organismo_padre,
                    gp_padre.fecha_actualizacion AS fecha_actualizacion_padre,
                    gp_padre.fecha_creacion AS fecha_creacion_padre,    
                    gp_padre.base AS base_padre    
                FROM tareas.herarquia_grupo_grupo hgg
                INNER JOIN GroupTree gt ON gt.id_hijo = hgg.id_padre
                INNER JOIN tareas.grupo gp_padre ON hgg.id_padre = gp_padre.id
                INNER JOIN tareas.grupo gp_hijo ON hgg.id_hijo = gp_hijo.id
                WHERE 
                    (:nombre IS NULL OR gp_hijo.nombre ILIKE '%' || :nombre || '%')
                    AND (:eliminado IS NULL OR gp_hijo.eliminado = :eliminado)
                    AND (:suspendido IS NULL OR gp_hijo.suspendido = :suspendido)
                    AND (:id_dominio IS NULL OR gp_hijo.id_dominio_ext = :id_dominio)
                    AND (:id_organismo IS NULL OR gp_hijo.id_organismo_ext = :id_organismo)    
                FROM tareas.herarquia_grupo_grupo hgg
                INNER JOIN GroupTree gt ON gtL OR gp_hijo.id_organismo_ext = :id_organismo)
                    AND (:fecha_desde IS NULL OR gp_hijo.fecha_actualizacion >= :fecha_desde)
                    AND (:fecha_hasta IS NULL OR gp_hijo.fecha_actualizacion <= :fecha_hasta)         
            )

            -- Selección final (puede incluir DISTINCT si lo deseás)
            SELECT DISTINCT ON (gt.group_id) 
                gt.id_padre,
                gt.parent_name,
                gt.nombre_padre,
                gt.descripcion_padre,
                gt.eliminado_padre,
                gt.suspendido_padre,     
                gt.id_dominio_ext AS id_dominio_padre,
                gt.id_organismo_ext AS id_organismo_padre,   
                gt.fecha_actualizacion_padre,
                gt.fecha_creacion_padre,
                gt.base_padre,        
                gt.id_hijo as id,
                gt.child_name as name,
                gt.nombre_hijo as nombre,
                gt.descripcion_hijo as descripcion,
                gt.eliminado_hijo as eliminado,
                gt.suspendido_hijo as suspendido, 
                gt.id_dominio_ext AS id_dominio_hijo,
                gt.id_organismo_ext AS id_organismo_hijo,       
                gt.fecha_actualizacion_hijo as fecha_actualizacion,
                gt.fecha_creacion_hijo as fecha_creacion,        
                gt.base_hijo as base,        
                gt.path,
                gt.path_name,
                gt.level,
                gt.is_parentless,
                gt.group_id
            FROM GroupTree gt
            ORDER BY gt.group_id, gt.level DESC;
        
        """)     
        subquery = text("""
            WITH RECURSIVE GroupTree AS (
                -- Parte base
                SELECT 
                    g.id AS id_padre,
                    g.id AS id_hijo,
                    g.descripcion AS parent_name,
                    g.descripcion AS child_name,
                    g.id::text AS path,
                    COALESCE(g.nombre, g.id::text) AS path_name,
                    0 AS level,
                    NOT EXISTS (SELECT 1 FROM tareas.herarquia_grupo_grupo hgg WHERE hgg.id_hijo = g.id) AS is_parentless,
                    g.id AS group_id,
                    g.eliminado AS eliminado_hijo,
                    g.suspendido AS suspendido_hijo,
                    g.nombre AS nombre_hijo,
                    g.descripcion AS descripcion_hijo,
                    g.id_dominio_ext AS id_dominio_hijo,
                    g.id_organismo_ext AS id_organismo_hijo,
                    g.fecha_actualizacion AS fecha_actualizacion_hijo,
                    g.fecha_creacion AS fecha_creacion_hijo,    
                    g.base AS base_hijo,
                    NULL::boolean AS eliminado_padre,
                    NULL::boolean AS suspendido_padre,
                    NULL::text AS nombre_padre,
                    NULL::text AS descripcion_padre,
                    NULL::uuid AS id_dominio_padre,
                    NULL::uuid AS id_organismo_padre,
                    NULL::timestamp AS fecha_actualizacion_padre,
                    NULL::timestamp AS fecha_creacion_padre,
                    NULL::boolean AS base_padre
                FROM tareas.grupo g
                
                WHERE 
                    (:nombre IS NULL OR g.nombre ILIKE '%' || :nombre || '%')
                    AND (:eliminado IS NULL OR g.eliminado = :eliminado)
                    AND (:suspendido IS NULL OR g.suspendido = :suspendido)
                    AND (:id_dominio IS NULL OR g.id_dominio_ext = :id_dominio)
                    AND (:id_organismo IS NULL OR g.id_organismo_ext = :id_organismo)
                    AND (:fecha_desde IS NULL OR g.fecha_creacion >= :fecha_desde)
                    AND (:fecha_hasta IS NULL OR g.fecha_creacion <= :fecha_hasta)
                    

                UNION ALL

                -- Parte recursiva
                SELECT 
                    hgg.id_padre,
                    hgg.id_hijo,
                    gp_padre.descripcion AS parent_name,
                    gp_hijo.descripcion AS child_name,
                    gt.path || ' -> ' || hgg.id_hijo::text AS path,
                    gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
                    gt.level + 1 AS level,
                    false AS is_parentless,
                    gp_hijo.id AS group_id,
                    gp_hijo.eliminado AS eliminado_hijo,
                    gp_hijo.suspendido AS suspendido_hijo,
                    gp_hijo.nombre AS nombre_hijo,
                    gp_hijo.descripcion AS descripcion_hijo,
                    gp_hijo.id_dominio_ext AS id_dominio_hijo,
                    gp_hijo.id_organismo_ext AS id_organismo_hijo,
                    gp_hijo.fecha_actualizacion AS fecha_actualizacion_hijo,
                    gp_hijo.fecha_creacion AS fecha_creacion_hijo,    
                    gp_hijo.base AS base_hijo,
                    gp_padre.eliminado AS eliminado_padre,
                    gp_padre.suspendido AS suspendido_padre,
                    gp_padre.nombre AS nombre_padre,
                    gp_padre.descripcion AS descripcion_padre,
                    gp_padre.id_dominio_ext AS id_dominio_padre,
                    gp_padre.id_organismo_ext AS id_organismo_padre,
                    gp_padre.fecha_actualizacion AS fecha_actualizacion_padre,
                    gp_padre.fecha_creacion AS fecha_creacion_padre,    
                    gp_padre.base AS base_padre
                FROM tareas.herarquia_grupo_grupo hgg
                INNER JOIN GroupTree gt ON gt.id_hijo = hgg.id_padre
                INNER JOIN tareas.grupo gp_padre ON hgg.id_padre = gp_padre.id
                INNER JOIN tareas.grupo gp_hijo ON hgg.id_hijo = gp_hijo.id
                
                WHERE 
                    (:nombre IS NULL OR gp_hijo.nombre ILIKE '%' || :nombre || '%')
                    AND (:eliminado IS NULL OR gp_hijo.eliminado = :eliminado)
                    AND (:suspendido IS NULL OR gp_hijo.suspendido = :suspendido)
                    AND (:id_dominio IS NULL OR gp_hijo.id_dominio_ext = :id_dominio)
                    AND (:id_organismo IS NULL OR gp_hijo.id_organismo_ext = :id_organismo)
                    AND (:fecha_desde IS NULL OR gp_hijo.fecha_creacion >= :fecha_desde)
                    AND (:fecha_hasta IS NULL OR gp_hijo.fecha_creacion <= :fecha_hasta)
                    
            )
            SELECT DISTINCT ON (gt.group_id) 
                gt.id_padre,
                gt.parent_name,
                gt.nombre_padre,
                gt.descripcion_padre,
                gt.eliminado_padre,
                gt.suspendido_padre,     
                gt.id_dominio_padre,
                gt.id_organismo_padre, 
                gt.fecha_actualizacion_padre,
                gt.fecha_creacion_padre,
                gt.base_padre,        
                gt.id_hijo as id,
                gt.child_name as name,
                gt.nombre_hijo as nombre,
                gt.descripcion_hijo as descripcion,
                gt.eliminado_hijo as eliminado,
                gt.suspendido_hijo as suspendido,    
                gt.id_dominio_hijo as id_dominio,
                gt.id_organismo_hijo as id_organismo, 
                gt.fecha_actualizacion_hijo as fecha_actualizacion,
                gt.fecha_creacion_hijo as fecha_creacion,        
                gt.base_hijo as base,        
                gt.path,
                gt.path_name,
                gt.level,
                gt.is_parentless,
                gt.group_id
            FROM GroupTree gt
            {where_final}            
            ORDER BY gt.group_id, name, gt.level DESC;
        """)

        # Armar cláusulas condicionales de JOIN y WHERE
        join_usuario_base = ""
        where_usuario_base = ""
        join_usuario_rec = ""
        where_usuario_rec = ""
        where_final = ""
        if (todos is None or todos==False or todos=='false') and id_user:
            #join_usuario_base = "INNER JOIN tareas.usuario_grupo ug ON ug.id_grupo = g.id"
            #where_usuario_base = "AND ug.id_usuario = :id_usuario"
            #join_usuario_rec = "INNER JOIN tareas.usuario_grupo ug2 ON ug2.id_grupo = gp_hijo.id"
            #where_usuario_rec = "AND ug2.id_usuario = :id_usuario"
            where_final = "WHERE EXISTS (SELECT 1 FROM tareas.usuario_grupo ug WHERE ug.id_grupo = gt.group_id AND ug.id_usuario = :id_usuario)"
            params["id_usuario"] = id_user

        # Reemplazar placeholders en la consulta
        final_query = subquery.text.replace("{where_final}", where_final)
            
            #.replace("{join_usuario_base}", join_usuario_base) \
            #.replace("{where_usuario_base}", where_usuario_base) \
            #.replace("{join_usuario_rec}", join_usuario_rec) \
            #.replace("{where_usuario_rec}", where_usuario_rec)\

        result = db.session.execute(text(final_query), params).mappings().all()
        #result1 = db.session.execute((subquery1), params).mappings().all()
        # Paginación
        total = len(result)
        start = (page - 1) * per_page
        end = start + per_page
        result_paginated = result[start:end]

        return result_paginated, total

    # Query for non-hierarchical groups
    query = db.session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))
    print("todos:", todos)
    # Apply filters
    if nombre:
        query = query.filter(Grupo.nombre.ilike(f"%{nombre}%"))
    if eliminado is not None:
        query = query.filter(Grupo.eliminado == eliminado)
    if suspendido is not None:
        query = query.filter(Grupo.suspendido == suspendido)
    if todos is None or todos== False or todos== 'false':
        query = query.join(UsuarioGrupo, UsuarioGrupo.id_grupo == Grupo.id).filter(UsuarioGrupo.id_usuario == id_user)    
    if id_dominio:
        query = query.filter(Grupo.id_dominio_ext == id_dominio)
    if id_organismo:
        query = query.filter(Grupo.id_organismo_ext == id_organismo)

    total = query.count()
    result_paginated = query.order_by(Grupo.nombre).offset((page - 1) * per_page).limit(per_page).all()

    # Convert query results into serializable format
    result = [
        {
            "id": grupo.id,
            "nombre": grupo.nombre,
            "descripcion": grupo.descripcion,
            "fecha_creacion": grupo.fecha_creacion,
            "fecha_actualizacion": grupo.fecha_actualizacion,
            "eliminado": grupo.eliminado,
            "suspendido": grupo.suspendido,
            "base": grupo.base,
            "id_dominio": grupo.id_dominio_ext,
            "id_organismo": grupo.id_organismo_ext,
            "organismo": grupo.organismo,
            "dominio": grupo.dominio
        }
        for grupo in result_paginated
    ]

    return result, total

@cache.memoize(CACHE_TIMEOUT_LONG)
def encontrar_grupo_base(res_grupos, id):
    print("Encontrar grupo base para el ID:", id)
    for r in res_grupos:
        if id == str(r['id_hijo']):
           # print("############ENCONTRADO##############")
            if r['is_parentless']:
                #print("GRUPO BASE ENCONTRADO:", r)
                return r  # Retornar el grupo base si es parentless
            else:
               # print("PADRE:", r['id_padre'])
                # Llamada recursiva con el padre como nuevo ID
                return encontrar_grupo_base(res_grupos, str(r['id_padre']))    

@cache.memoize(CACHE_TIMEOUT_LONG)
def buscar_mismos_base(res_grupos, id, grupos_acumulados=None, visitados=None):
    if grupos_acumulados is None:
        grupos_acumulados = []
    
    if visitados is None:
        visitados = set()
    
    if id in visitados:
        return grupos_acumulados
    
    hijos_directos = []
    
    visitados.add(id)
    
    for r in res_grupos:
        if r['id_padre'] == id:
            hijos_directos.append(r)

    grupos_acumulados.extend(hijos_directos)    
    
    #print ("Hijos directos:", hijos_directos)

    for hijo in hijos_directos:
        buscar_mismos_base(res_grupos, hijo['id_hijo'], grupos_acumulados, visitados)
    
    return grupos_acumulados

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_base(id, usuarios=False):
    cursor=None
   
    #session: scoped_session = current_app.session
    # Subconsulta recursiva
    subquery = text("""
        WITH RECURSIVE GroupTree AS (
            -- Anchor member: Start with all parentless nodes
            SELECT 
                g.id AS id_padre,
                g.id AS id_hijo,
                g.nombre AS parent_name,
                g.nombre AS child_name,
                g.id::text AS path,
                COALESCE(g.nombre, g.id::text) AS path_name,
                0 AS level,
                true AS is_parentless,
                g.id AS group_id,
                g.base AS is_base,
                g.eliminado AS eliminado,
                g.suspendido AS suspendido,
                g.id_dominio_ext AS id_dominio,
                g.id_organismo_ext AS id_organismo
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
                gp_hijo.nombre AS child_name,
                gt.path || ' -> ' || hgg.id_hijo::text AS path,
                gt.path_name || ' -> ' || COALESCE(gp_hijo.nombre, hgg.id_hijo::text) AS path_name,
                gt.level + 1 AS level,
                false AS is_parentless,
                gp_hijo.id AS group_id,
                gp_padre.base AS is_base,
                gp_hijo.eliminado AS eliminado,
                gp_hijo.suspendido AS suspendido,
                gp_hijo.id_dominio_ext AS id_dominio,
                gp_hijo.id_organismo_ext AS id_organismo
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
            gt.eliminado,
            gt.suspendido,
            gt.id_dominio,
            gt.id_organismo,
            gt.is_base
        FROM 
            GroupTree gt
        ORDER BY 
            gt.path;
        """)

    # Ejecutar la subconsulta
    cursor = db.session.execute(subquery)
    
    result = cursor.fetchall()
    res_grupos=[]
    res=[]
    print("Usuarios:", usuarios)
    for reg in result:

        data = {
            "id": reg.group_id,
            "id_padre": reg.id_padre,
            "id_hijo": reg.id_hijo,
            "parent_name": reg.parent_name,
            "child_name": reg.child_name,
            "path": reg.path,
            "path_name": reg.path_name,
            "eliminado": reg.eliminado,
            "suspendido": reg.suspendido,
            "id_dominio": reg.id_dominio,
            "id_organismo": reg.id_organismo,
            "organismo": reg.organismo if hasattr(reg, 'organismo') else None,
            "dominio": reg.dominio if hasattr(reg, 'dominio') else None,
            "is_base": reg.is_base,
            "is_parentless": reg.is_parentless
        }    

        res_grupos.append(data) 
    

    grupo_base = None
    print("Antes de encontrar grupo base", id)
    grupo_base=encontrar_grupo_base(res_grupos, id)

    grupos_mismo_base = []
    if grupo_base:
        # Filtrar los grupos con el mismo grupo base
        grupos_mismo_base = buscar_mismos_base(res_grupos, grupo_base['id'])

        #print(grupos_mismo_base)
        for grupo in grupos_mismo_base:
            usuarios_g = []
            id_grupo = grupo['id']
            if usuarios=='true' or usuarios==True:
                res_usuarios = db.session.query(UsuarioGrupo.id_grupo,
                                        UsuarioGrupo.id_usuario,
                                        Usuario.id,
                                        Usuario.nombre,
                                        Usuario.apellido,
                                        Usuario.eliminado,
                                        Usuario.suspendido,
                                        UsuarioGrupo.eliminado.label("eliminado_grupo"),
                                        ).join(Usuario, Usuario.id == UsuarioGrupo.id_usuario
                                        ).filter(UsuarioGrupo.id_grupo == id_grupo, UsuarioGrupo.eliminado==False
                                        ).order_by(Usuario.apellido).all()
                
                if res_usuarios is not None:
                    for row in res_usuarios:
                        usuario = {
                            "id_usuario": row.id,
                            "nombre": row.nombre,
                            "apellido": row.apellido,
                            "eliminado": row.eliminado,
                            "suspendido": row.suspendido,
                            "eliminado_grupo": row.eliminado_grupo,
                            "username": row.nombre
                        }
                        usuarios_g.append(usuario)
                else:
                    print("No se encontraron usuarios para el grupo:", reg.id_hijo)  

            data = {
                "id": grupo['id'],
                "id_padre": grupo['id_padre'],
                "id_hijo": grupo['id_hijo'],
                "parent_name": grupo['parent_name'],
                "child_name": grupo['child_name'],
                "path": grupo['path'],
                "path_name": grupo['path_name'],
                "eliminado": grupo['eliminado'],
                "suspendido": grupo['suspendido'],
                "is_base": grupo['is_base'],
                "is_parentless": grupo['is_parentless'],
                "usuarios": usuarios_g
                }
            
            res.append(data)
    else:
        print("No se encontró un grupo base para el ID proporcionado.")

    return res                                                                          
        
     

   
    #return res, i
#@cache.cached(CACHE_TIMEOUT_LONG, make_cache_key='get_all_grupos_'+page+'_'+per_page+'_'+nombre+'_'+fecha_desde+'_'+fecha_hasta+'_'+path_name)
@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_grupos(page=1, per_page=10, nombre="", fecha_desde='01/01/2000', fecha_hasta=datetime.now().strftime('%d/%m/%Y'), path_name=False): 
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())
    #fecha_hasta = fecha_hasta + " 23:59:59"
    print("Fecha hasta:", fecha_hasta) 
    #fecha_desde = datetime.strptime(fecha_desde, "%d/%m/%Y").replace(hour=0, minute=1, second=0, microsecond=0)
    #fecha_hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y").replace(hour=23, minute=59, second=59, microsecond=0)
    
    #session: scoped_session = current_app.session
    total= db.session.query(Grupo).count()

    query= db.session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))
    
    if nombre:
        query= query.filter(Grupo.nombre.ilike(f"%{nombre}%"))

    total= len(query.all()) 

    result= query.order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()  


    return result, total
    
@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_grupos_detalle(page=1, per_page=10, nombre=None, eliminado=None, suspendido=None, fecha_desde=None, fecha_hasta=None, id_dominio=None, id_organismo=None): 
   
    if fecha_desde is not None:
        fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y')
    else:
        fecha_desde=datetime.strptime("30/01/1900","%d/%m/%Y")

    if fecha_hasta is not None:
        fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y')
    else:
        fecha_hasta=datetime.now()
        #.date()
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())
    #valido que fecha_dsde no sea mayor a fecha_hasta
    if fecha_desde > fecha_hasta:
        raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")
    
    query= db.session.query(Grupo).filter(Grupo.fecha_creacion.between(fecha_desde, fecha_hasta))

    filters = []

    if nombre:
        filters.append(Grupo.nombre.ilike(f"%{nombre}%"))
    if eliminado:
        filters.append(Grupo.eliminado == eliminado)
    if suspendido:
        filters.append(Grupo.suspendido == suspendido)
    if id_dominio:
        filters.append(Grupo.id_dominio_ext == id_dominio)
    if id_organismo:
        filters.append(Grupo.id_organismo_ext == id_organismo)

    # Apply all filters at once
    if filters:
        query = query.filter(*filters)    

    if eliminado:
        filters.append(Grupo.eliminado == eliminado)
    if suspendido:
        filters.append(Grupo.suspendido == suspendido)


    total= len(query.all()) 

    result= query.order_by(Grupo.nombre).offset((page-1)*per_page).limit(per_page).all()  

    if result is not None:
        results=[]
        for res in result:
            usuarios=[]
            tareas=[]
           
            res_usuario = db.session.query(UsuarioGrupo.id_grupo,
                                        UsuarioGrupo.eliminado.label("eliminado_usrgrupo"),
                                        Usuario.id, Usuario.nombre, 
                                        Usuario.apellido,
                                        Usuario.eliminado.label("eliminado_usr"), 
                                        Usuario.suspendido.label("suspendido_usr"), 
                                        Usuario.fecha_actualizacion
                        ).join(Usuario, Usuario.id==UsuarioGrupo.id_usuario).filter(UsuarioGrupo.id_grupo==res.id).order_by(Usuario.apellido).all()
            
            res_tareas = db.session.query(TareaXGrupo.id_grupo, 
                                       Tarea.id, 
                                       Tarea.titulo, 
                                       Tarea.id_tipo_tarea,
                                       Tarea.id_subtipo_tarea,
                                      # Tarea.subtipo_tarea,
                                      # Tarea.tipo_tarea,
                                       Tarea.eliminado.label("tarea_eliminado"),
                                       Tarea.estado,
                                       Tarea.fecha_actualizacion,
                                       TareaXGrupo.eliminado.label("eliminado_tareaxgrupo"),
                                       ).join(Tarea, Tarea.id==TareaXGrupo.id_tarea
                                                   ).filter(TareaXGrupo.id_grupo==res.id).order_by(desc(Tarea.fecha_creacion)).all()
            
            if res_usuario is not None:
                for row in res_usuario:
                    usuario = {
                        "apellido": row.apellido,
                        "nombre": row.nombre,
                        "id": row.id,
                        "eliminado_grupo": row.eliminado_usrgrupo,
                        "usr_eliminado": row.eliminado_usr,
                        "usr_suspendido": row.suspendido_usr,
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
                        "eliminado_grupo": row.eliminado_tareaxgrupo,
                        "tarea_eliminado": row.tarea_eliminado,
                        "fecha_actualizacion": row.fecha_actualizacion
                    }
                    tareas.append(tarea)

            result = {
                "id": res.id,
                "nombre": res.nombre,
                "descripcion": res.descripcion,
                "organismo": res.organismo,
                "dominio": res.dominio,
                "fecha_creacion": res.fecha_creacion,
                "fecha_actualizacion": res.fecha_actualizacion,
                "id_user_actualizacion": res.id_user_actualizacion,
                "id_user_asignado_default": res.id_user_asignado_default,
                "eliminado": res.eliminado,
                "suspendido": res.suspendido,
                "id_dominio": res.id_dominio_ext,
                "id_organismo": res.id_organismo_ext,
                "usuarios": usuarios,
                "tareas": tareas
            } 
                  
            results.append(result)

    return results, total

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_herarquia():
    #session: scoped_session = current_app.session
    res =db.session.query(HerarquiaGrupoGrupo).all()
    return res

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_grupos_herarquia():
    #session: scoped_session = current_app.session
    res=db.session.query(Grupo.id, Grupo.nombre, HerarquiaGrupoGrupo.id_hijo, HerarquiaGrupoGrupo.id_padre)\
        .join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_padre)\
        .all()
    #print(len(res))
    return res

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_grupos_herarquia_labels():
    GrupoPadre = aliased(Grupo)
    GrupoHijo = aliased(Grupo)
    #session: scoped_session = current_app.session
    
    # Realizar la consulta con los joins necesarios
    res = db.session.query(
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


def update_grupo(username=None,id=None, **kwargs):
    #session: scoped_session = current_app.session

    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)


    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    if id is None:
        raise Exception("ID de grupo no ingresado")
    if id is not None:  
        if not(functions.es_uuid(id)):
            raise Exception("El id del grupo debe ser un UUID: " + id)  

    grupo = db.session.query(Grupo).filter(Grupo.id == id).first()
    if grupo is None:
        return None
    
    if grupo.eliminado:
        raise Exception("Grupo eliminado")
    
    """ if grupo.suspendido:
        raise Exception("Grupo suspendido") """


    if 'nombre' in kwargs:
        grupo.nombre = kwargs['nombre']
    if 'descripcion' in kwargs:
        grupo.descripcion = kwargs['descripcion']
    if 'suspendido' in kwargs:
        grupo_con_tarea= db.session.query(TareaXGrupo).join(Tarea, Tarea.id==TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id, Tarea.estado==1 or Tarea.estado==1).all()
        if len(grupo_con_tarea)>0:
            raise Exception("No se puede suspender el grupo. El grupo tiene tareas sin cerrar")
        grupo.suspendido = kwargs['suspendido']
    if 'id_organismo' in kwargs:
        if not(functions.es_uuid(kwargs['id_organismo'])):
            raise Exception("El id del organismo debe ser un UUID: " + kwargs['id_organismo'])
        organismo = db.session.query(Organismo).filter(Organismo.id==kwargs['id_organismo'], Organismo.habilitado==True).first()
        if organismo is None:
            raise Exception("Organismo no encontrado")
        grupo.id_organismo_ext = kwargs['id_organismo']
    if 'id_dominio' in kwargs:
        if not(functions.es_uuid(kwargs['id_dominio'])):
            raise Exception("El id del dominio debe ser un UUID: " + kwargs['id_dominio'])
        dominio = db.session.query(Dominio).filter(Dominio.id==kwargs['id_dominio'], Dominio.habilitado==True).first()
        if dominio is None:
            raise Exception("Dominio no encontrado")
        grupo.id_dominio_ext = kwargs['id_dominio']
        
    if 'id_user_asignado_default' in kwargs:
        if not(functions.es_uuid(kwargs['id_user_asignado_default'])):
            raise Exception("El id del usuario asignado default debe ser un UUID: " + kwargs['id_user_asignado_default'])
        print("--Id user asignado default:", kwargs['id_user_asignado_default'])
        if(kwargs['id_user_asignado_default']==None):
             grupo.id_user_asignado_default = None
        else:     
            usuario= db.session.query(Usuario).filter(Usuario.id==kwargs['id_user_asignado_default'], Usuario.eliminado==False).first()
            if usuario is None:
                raise Exception("Usuario asignado default no encontrado")
            
            usuario_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo==id, UsuarioGrupo.id_usuario==kwargs['id_user_asignado_default'], UsuarioGrupo.eliminado==False).first()
            if usuario_grupo is None:
                raise Exception("Usuario por defecto no asignado al grupo")

            grupo.id_user_asignado_default = kwargs['id_user_asignado_default']

    # Siempre actualizar la fecha de actualización
    grupo.fecha_actualizacion = datetime.now()
    
    if 'id_padre' in kwargs:
        if not(functions.es_uuid(kwargs['id_padre'])):
            raise Exception("El id del grupo padre debe ser un UUID: " + kwargs['id_padre'])
        herarquia = db.session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo==id).first()      
        if herarquia is None:
            nueva_herarquia = HerarquiaGrupoGrupo(
                id=uuid.uuid4(),
                id_padre=kwargs['id_padre'],
                id_hijo=id,
                #id_user_actualizacion=kwargs['id_user_actualizacion'],
                id_user_actualizacion= id_user_actualizacion,
                fecha_actualizacion=datetime.now()
            )
            db.session.add(nueva_herarquia)
        else:
            herarquia.id_padre = kwargs['id_padre']
            #herarquia.id_user_actualizacion = kwargs['id_user_actualizacion']
            herarquia.id_user_actualizacion = id_user_actualizacion
            herarquia.fecha_actualizacion = datetime.now()

    if 'usuario' in kwargs:
        #elimino los usuarios existentes para ese grupo
        usuario_grupo=db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo == id)
        for usr in usuario_grupo:
            usr.eliminado=True
            usr.fecha_actualizacion=datetime.now()
            #usr.id_user_actualizacion=kwargs['id_user_actualizacion']
            usr.id_user_actualizacion=id_user_actualizacion
            
        for usuario in kwargs['usuario']:
            if not(functions.es_uuid(usuario['id_usuario'])):
                raise Exception("El id del usuario debe ser un UUID: " + usuario['id_usuario'])
            encuentra_usuario = db.session.query(Usuario).filter(Usuario.id==usuario['id_usuario']).first()
            if encuentra_usuario is None:
                raise Exception("Usuario no encontrado:" + usuario['id_usuario'])
            if encuentra_usuario.eliminado:
                raise Exception("Usuario eliminado:" + usuario['id_usuario'])
            
            usuario_grupo = db.session.query(UsuarioGrupo).filter(UsuarioGrupo.id_grupo==id, UsuarioGrupo.id_usuario==usuario['id_usuario']).first()
            
            if usuario_grupo is None:
                #Agrego el usuario al grupo
                nuevo_usuario_grupo = UsuarioGrupo(
                    id=uuid.uuid4(),
                    id_grupo=id,
                    id_usuario=usuario['id_usuario'],
                    fecha_actualizacion=datetime.now(),
                    id_user_actualizacion=id_user_actualizacion
                )
                db.session.add(nuevo_usuario_grupo)
            else:
                #encuentra el usuario y lo reactiva 
                usuario_grupo.eliminado = False
                usuario_grupo.fecha_actualizacion = datetime.now()
                usuario_grupo.id_user_actualizacion = id_user_actualizacion    
                

    db.session.commit()
    return grupo

def insert_grupo(username=None, dominio=None, organismo=None, nombre='', descripcion='', id_user_actualizacion=None, id_padre=None, id_user_asignado_default=None):
    #session: scoped_session = current_app.session
    #Validaciones
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado")
    
    if id_user_asignado_default is not None:
        usuario = db.session.query(Usuario).filter(Usuario.id==id_user_asignado_default, Usuario.eliminado==False).first()
        if usuario is None: 
            raise Exception("Usuario de asignación de tareas no encontrado")

    if id_user_actualizacion is not None:
        usuario = db.session.query(Usuario).filter(Usuario.id==id_user_actualizacion, Usuario.eliminado==False).first()
        if usuario is None: 
            raise Exception("Usuario de actualización no encontrado")
        
    """ if id_organismo is not None:
        organismo = db.session.query(Organismo).filter(Organismo.id==id_organismo, Organismo.habilitado==True).first()
        if organismo is None: 
            raise Exception("Organismo no encontrado")
        dominio = db.session.query(Dominio).filter(Dominio.id_dominio_ext==organismo.id_dominio_ext, Dominio.habilitado==True).first()
        if dominio is not None:
            id_dominio = dominio.id
    ##################### REVISAR ESTO ######################
    if id_dominio is not None:
        dominio = db.session.query(Dominio).filter(Dominio.id==id_dominio, Dominio.habilitado==True).first()
        if dominio is None:
            raise Exception("Dominio no encontrado")
    else:
        if id_dominio is not None:
            id_dominio = id_dominio """
    id_dominio = None
    id_organismo = None
    if id_padre is not None and id_padre is not '':
        grupos_padres = get_all_base(id_padre, usuarios=False)   
        print("Grupos padres:", grupos_padres)

        if len(grupos_padres) > 0:
            #busco en grupos padres si alguno tiene el atributo is_parentless=True
            id_base = None
            for grupo in grupos_padres:
                if grupo['is_parentless']== True:
                    id_base = grupo['id']
                    print("#"* 30)
                    print("Grupo base encontrado:", id_base)
                    print("#"* 30)
                    break
            query_base = db.session.query(Grupo).filter(Grupo.id==id_base).first()

            if query_base is not None:
                id_dominio = query_base.id_dominio_ext
                id_organismo = query_base.id_organismo_ext

    """ if id_dominio is None:
        id_dominio = dominio
    if id_organismo is None:
        id_organismo = organismo """

    nuevoID_grupo=uuid.uuid4()
    nuevoID=uuid.uuid4()
    nuevo_grupo = Grupo(
        id=nuevoID_grupo,
        nombre=nombre.upper(),
        descripcion=descripcion,
        base=False,
        id_organismo_ext=id_organismo,
        id_dominio_ext=id_dominio,
        eliminado=False,
        suspendido=False,
        id_user_actualizacion=id_user_actualizacion,
        id_user_asignado_default=id_user_asignado_default,
        fecha_actualizacion=datetime.now(),
        fecha_creacion=datetime.now()
    )
    db.session.add(nuevo_grupo)

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
        db.session.add(nuevo_usuario_grupo)

    """ if id_organismo is not None:
        nuevoID_org_grp=uuid.uuid4()
        nuevo_organismo_grupo = Organismo(
            id=nuevoID_org_grp,
            id_grupo=nuevoID_grupo,
            id_organismo=id_organismo,
            fecha_actualizacion=datetime.now(),
            id_user_actualizacion=id_user_actualizacion
        )
        db.session.add(nuevo_organismo_grupo) """

    if id_padre is not '':        
        nueva_herarquia = HerarquiaGrupoGrupo(
            id=nuevoID,
            id_padre=id_padre,
            id_hijo=nuevoID_grupo,
            id_user_actualizacion=id_user_actualizacion,
            fecha_actualizacion=datetime.now()
        )
        db.session.add(nueva_herarquia)
    
    db.session.commit()

    id_grupo= nuevo_grupo.id
    subquery = text("""
            WITH RECURSIVE GroupTree AS (
                        -- Anchor: empezar desde el grupo dado
                        SELECT 
                            g.id AS id_hijo,
                            g.id AS id_padre,
                            g.descripcion AS child_name,
                            g.descripcion AS parent_name,
                            g.id::text AS path,
                            COALESCE(g.nombre, g.id::text) AS path_name,
                            0 AS level,
                            true AS is_childless,
                            g.id AS group_id
                        FROM 
                            tareas.grupo g
                        WHERE 
                            g.id = :id_grupo

                        UNION ALL

                        -- Recursive: buscar padre del grupo actual
                        SELECT 
                            gpadre.id AS id_hijo,
                            hgg.id_padre,
                            ghijo.descripcion AS child_name,
                            gpadre.descripcion AS parent_name,
                            gpadre.id::text || ' -> ' || gt.path AS path,
                            COALESCE(gpadre.nombre, gpadre.id::text) || ' -> ' || gt.path_name AS path_name,
                            gt.level + 1 AS level,
                            false AS is_childless,
                            gpadre.id AS group_id
                        FROM 
                            tareas.herarquia_grupo_grupo hgg
                        INNER JOIN 
                            GroupTree gt ON gt.id_padre = hgg.id_hijo
                        INNER JOIN 
                            tareas.grupo ghijo ON hgg.id_hijo = ghijo.id
                        INNER JOIN 
                            tareas.grupo gpadre ON hgg.id_padre = gpadre.id
                    )

                    SELECT 
                        gt.id_padre,
                        gt.parent_name,
                        gt.id_hijo,
                        gt.child_name,
                        gt.path,
                        gt.path_name,
                        gt.level,
                        gt.is_childless,
                        gt.group_id
                    FROM 
                        GroupTree gt
                    ORDER BY 
                        gt.level DESC;
                    """)

    cursor = db.session.execute(subquery, {"id_grupo": id_grupo}).fetchall()
    if cursor:
        print("Path posta:", cursor[0].path)

    data={
        "id": nuevo_grupo.id,
        "nombre": nuevo_grupo.nombre,
        "descripcion": nuevo_grupo.descripcion,
        "base": nuevo_grupo.base,
        "eliminado": nuevo_grupo.eliminado,
        "suspendido": nuevo_grupo.suspendido,
        "id_user_actualizacion": nuevo_grupo.id_user_actualizacion,
        "user_actualizacion": nuevo_grupo.user_actualizacion,
        "id_user_asignado_default": nuevo_grupo.id_user_asignado_default,
        "user_asignado_default": nuevo_grupo.user_asignado_default,
        "fecha_creacion": nuevo_grupo.fecha_creacion,
        "fecha_actualizacion": nuevo_grupo.fecha_actualizacion,
        "path": cursor[0].path if cursor else "",
        "path_name": cursor[0].path_name if cursor else "",
        "id_dominio": nuevo_grupo.id_dominio_ext,
        "id_organismo": nuevo_grupo.id_organismo_ext,
        "organismo": nuevo_grupo.organismo,
        "dominio": nuevo_grupo.dominio
    }

    return data

@cache.cached(CACHE_TIMEOUT_LONG)
def get_usuarios_by_grupo(grupos):
    print("Grupos:", grupos)
    res = []
    #for id in ids:
    
    if grupos is None:
        logger_config.logger.error("No se han proporcionado grupos para conultar usuarios")
        raise Exception("No se han proporcionado grupos para conultar usuarios") 

    grupos = grupos.split(",")
    for i in range(len(grupos)):
        grupos[i] = grupos[i].strip()
        if not(functions.es_uuid(grupos[i])):
            logger_config.logger.error("El id del grupo debe ser un UUID: " + grupos[i])
            raise Exception("El id del grupo debe ser un UUID: " + grupos[i])
        
    usrs = db.session.query(Grupo.id.label("id_grupo"),
            Grupo.nombre.label("nombre_grupo"),
            Usuario.nombre.label("nombre"),
            Usuario.apellido.label("apellido"),
            Usuario.id.label("id_usuario"),
            Usuario.eliminado.label("eliminado"),
            Usuario.suspendido.label("suspendido"),
            Usuario.username.label("username"),
            Usuario.email.label("email")                  
            ).join(UsuarioGrupo, Grupo.id == UsuarioGrupo.id_grupo
            ).join(Usuario, UsuarioGrupo.id_usuario == Usuario.id
            ).filter(Grupo.id.in_(grupos), UsuarioGrupo.eliminado==False
            ).order_by(Grupo.nombre).all()
    #.distinct()
    return usrs
   


def get_grupos_recursivo():
    #session: scoped_session = current_app.session
    
    
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
    res = db.session.execute(query).fetchall()
    return res
 


def get_grupos_all(eliminado=None):
    #print("eliminado:", eliminado)
    #session: scoped_session = current_app.session
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
        'g.id AS group_id, '
        'd.id AS dominio_id, '
        'd.descripcion AS dominio_descripcion '
        'FROM tareas.grupo g '
        'LEFT JOIN tareas.herarquia_grupo_grupo hgg1 ON g.id = hgg1.id_hijo '
        'LEFT JOIN tareas.dominio d ON g.id_dominio_ext = d.id_dominio_ext '
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
        'gp_hijo.id AS group_id, '
        'd.id AS dominio_id, '
        'd.descripcion AS dominio_descripcion '
        'FROM tareas.herarquia_grupo_grupo hgg '
        'INNER JOIN GroupTree gt ON gt.id_hijo = hgg.id_padre '
        'INNER JOIN tareas.grupo gp_padre ON hgg.id_padre = gp_padre.id '
        'INNER JOIN tareas.grupo gp_hijo ON hgg.id_hijo = gp_hijo.id '
        'LEFT JOIN tareas.dominio d ON gp_hijo.id_dominio_ext = d.id_dominio_ext '
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
        'gt.group_id, '
        'gt.dominio_id, '
        'gt.dominio_descripcion '
        'FROM GroupTree gt '
    )

    if eliminado is not None:
        query_str += ' WHERE gt.child_eliminado = :eliminado'

    query_str += ' ORDER BY gt.path;'

    query = text(query_str)

    # Ejecutar la consulta con el parámetro `eliminado` si es necesario
    if eliminado is not None:
        res = db.session.execute(query, {"eliminado": eliminado}).fetchall()
    else:
        res = db.session.execute(query).fetchall()
   
    return res


def eliminar_grupo_recursivo(id):

    #session: scoped_session = current_app.session
    hijos = db.session.query(Grupo.id,
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
            grupo = db.session.query(Grupo).filter(Grupo.id == hijo.id_hijo, Grupo.eliminado==False).first()
            if grupo is not None:
                grupo.eliminado = True
                db.session.add(grupo)

    

def delete_grupo(username=None, id='', todos=False):
    #print("Borrando grupo con id:", id)
    #session = current_app.session
    

    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        logger_config.logger.error("Id de usuario no ingresado")
        #raise Exception("Usuario no ingresado")    
    
    grupo = db.session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
    if grupo is None:
        raise Exception("Grupo no encontrado")
    
    grupo_con_tarea= db.session.query(TareaXGrupo).join(Tarea, Tarea.id==TareaXGrupo.id_tarea).filter(TareaXGrupo.id_grupo == id, Tarea.estado==1 or Tarea.estado==1).all()
    if len(grupo_con_tarea)>0:
        raise Exception("No se puede eliminar el grupo. El grupo tiene tareas sin cerrar")
       
    if todos:
        # Eliminar todos los hijos
        #print("Eliminar todos los hijos")
        eliminar_grupo_recursivo(id)
        grupo = db.session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
        if grupo:
            grupo.eliminado = True

    else:    
        # Eliminar solo el grupo
        #print("Eliminar solo el grupo")
        tiene_hijos = db.session.query(HerarquiaGrupoGrupo).join(Grupo, Grupo.id==HerarquiaGrupoGrupo.id_hijo).filter(HerarquiaGrupoGrupo.id_padre == id, Grupo.eliminado==False).all()
        #print("Tiene hijos:", tiene_hijos)
        if len(tiene_hijos)>0:
            #for hijo in tiene_hijos:
                 #print("El grupo tiene hijos - id_padre:", hijo.id_padre, "-id_hijo:", hijo.id_hijo)

            raise Exception("El grupo tiene hijos")
                    
        grupo = db.session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == False).first()
        if grupo:
            grupo.eliminado = True
        else:
            #print("No se encontró el grupo a eliminar")
            raise Exception("No se encontró el grupo a eliminar")
            

    db.session.commit()
    

    return grupo

def undelete_grupo(username=None, id=None):
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")
    
    grupo = db.session.query(Grupo).filter(Grupo.id == id, Grupo.eliminado == True).first()
    if grupo is None:
        raise Exception("Grupo no encontrado")
    grupo.eliminado = False
    db.session.commit()
    return grupo




    
    
