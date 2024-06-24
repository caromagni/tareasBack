from apiflask import Schema, abort, APIBlueprint
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app, jsonify
from sqlalchemy.orm import scoped_session
from ..alch_model import Grupo,Usuario

usuario_b = APIBlueprint('usuario_b', __name__)

class UsuarioIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['usera', 'userb']))
    test = String()

class UsuarioOut(Schema):
    id = Integer()
    name = String()
    name3 = String()
    category = String()

@usuario_b.get('/usuario')
def get_grupos():
    session: scoped_session = current_app.session
    usuarios = session.query(Usuario).all()
    
    return jsonify([{
        'id': str(usuario.id),
        'nombre': str(usuario.nombre),
        'apellido': usuario.apellido,
        'fecha_actualizacion': usuario.fecha_actualizacion
    } for usuario in usuarios])
