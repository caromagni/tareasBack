from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify
from sqlalchemy.orm import scoped_session
from ..alch_model import Grupo,Tarea,Usuario
from sqlalchemy.sql import text
from typing import List
from flask_cors import cross_origin


# from apiflask import Schema, abort, APIBlueprint, input, output
# from apiflask.fields import Integer, String
# from apiflask.validators import Length, OneOf
# from flask import current_app, jsonify
# from sqlalchemy.orm import scoped_session, Session
# from ..alch_model import Grupo, Tarea, Usuario, TareaAsignadaUsuario
# from sqlalchemy.sql import text
# from typing import List


groups_b = APIBlueprint('groups_b', __name__)

class GrupoIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
    test = String()

class GrupoOut(Schema):
    id = Integer()
    name = String()
    name3 = String()
    category = String()

@groups_b.patch('/grupo/<int:grupo_id>')
@groups_b.input(GrupoIn(partial=True))  # -> json_data
@groups_b.output(GrupoOut)
def update_grupo(grupo_id, json_data):
    print("grupo_id: ", grupo_id)
    print("get all grupos")
    
    # Get the session from the current app context
    session: scoped_session = current_app.session
    
    # Query all groups from the Grupo table
    grupos = session.query(Grupo).all()
    print("grupos: ", grupos)
    
    if grupo_id > len(grupos) - 1:
        abort(404)
    
    for attr, value in json_data.items():
        grupos[grupo_id][attr] = value
    
    return grupos[grupo_id]

@groups_b.get('/grupo')
@cross_origin(origin='http://shouldnotpass.com', supports_credentials=True)
def get_grupos():
    session: scoped_session = current_app.session
    grupos = session.query(Grupo).all()
    # result_raw = session.execute(text("SELECT * FROM tareas.grupo WHERE descripcion = :val"), {'val': 'auxiliares'}) #example of raw query, reusing session pool from sqlalchemy
    # for item_raw in result_raw:
    #     print("RAW")
    #     print(item_raw)
   
    return jsonify([{
        'id': str(grupo.id),
        'id_user_actualizacion': str(grupo.id_user_actualizacion),
        'fecha_actualizacion': grupo.fecha_actualizacion,
        'descripcion': grupo.descripcion
    } for grupo in grupos])

@groups_b.get('/tareas')
def get_tareas():
    session: scoped_session = current_app.session
    tareas = session.query(Tarea).all()
    return jsonify([{
        'id': str(tarea.id),
        'id_grupo': str(tarea.id_grupo),
        'prioridad': tarea.prioridad,
        'titulo': tarea.titulo,
        'cuerpo': tarea.cuerpo,
        'id_tipo_tarea': str(tarea.id_tipo_tarea),
        'eliminable': tarea.eliminable,
        'fecha_eliminacion': tarea.fecha_eliminacion
    } for tarea in tareas])

@groups_b.get('/tareas/{tarea_id}/usuarios-asignados')
def get_usuarios_asignados(tarea_id: str):
    session: scoped_session = current_app.session
    
    usuarios = session.query(Usuario)\
                     .join(TareaAsignadaUsuario, Usuario.id == TareaAsignadaUsuario.id_usuario)\
                     .filter(TareaAsignadaUsuario.id_tarea == tarea_id)\
                     .all()
    
    return jsonify([{
        'id': str(usuario.id),
        'fecha_actualizacion': usuario.fecha_actualizacion,
        'id_user_actualizacion': str(usuario.id_user_actualizacion),
        'nombre': usuario.nombre,
        'apellido': usuario.apellido,
        'id_persona_ext': str(usuario.id_persona_ext)
    } for usuario in usuarios])