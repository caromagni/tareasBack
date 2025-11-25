# common/error_handling.py
from flask import jsonify

# Excepciones personalizadas
class ForbiddenAccess(Exception):
    def __init__(self, message="Acceso denegado"):
        self.message = message
        self.code = 403
        self.error = "Forbidden"
        super().__init__(self.message)

class DataNotFound(Exception):
    def __init__(self, message="Datos no encontrados"):
        self.message = message
        self.code = 800
        self.error = "DataNotFound"
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message="Datos inválidos"):
        self.message = str(message)
        self.code = 400
        self.error = "InvalidData"
        super().__init__(self.message)

# Función para registrar manejadores de errores
def register_error_handlers(app):
    @app.errorhandler(ForbiddenAccess)
    def handle_forbidden_error(e):
        return jsonify({
            "code": e.code,
            "error": e.error,
            "error_description": e.message
        }), e.code

    @app.errorhandler(DataNotFound)
    def handle_not_found_error(e):
        return jsonify({
            "code": e.code,
            "error": e.error,
            "error_description": e.message
        }), 404 if e.code == 800 else e.code

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            "code": e.code,
            "error": e.error,
            "error_description": e.message
        }), e.code

