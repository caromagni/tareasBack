from flask import jsonify
import sys

class AppErrorBaseClass(Exception):
    pass

class HealthCheckError(AppErrorBaseClass):
    pass

class ObjectNotFound(AppErrorBaseClass):
    pass

class ConfigNotFound(AppErrorBaseClass):
    pass

class ValidationError(AppErrorBaseClass):
    pass

class GetTokenError(AppErrorBaseClass):
    pass

class InvalidPayload(AppErrorBaseClass):
    pass

class DataNotFound(AppErrorBaseClass):
    pass

class DataError(AppErrorBaseClass):
    def __init__(self,code,desc):
        self.code = code
        self.desc = desc
        

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        print(e)
        return jsonify({'msg': 'Internal server error'}), 500
    
    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({'msg': 'Method not allowed'}), 405

    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({'msg': 'Forbidden error'}), 403

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({'msg': 'Not Found error'}), 404

    @app.errorhandler(HealthCheckError)
    def handle_object_not_found_error(e):
        print(e)
        return jsonify(error='HealthCheckError',
                        error_description=str(e)), 400

    @app.errorhandler(AppErrorBaseClass)
    def handle_app_base_error(e):
        print("E1")
        return jsonify({'msg': str(e)}), 500

    @app.errorhandler(ObjectNotFound)
    def handle_object_not_found_error(e):
        print("Error ObjectNotFound:", e)
        #return jsonify(error='ObjectNotFound', code=e), 200
        return jsonify({'msg': str(e)}), 200
    
    @app.errorhandler(ValidationError)
    def handle_object_not_found_error(e):
        print(e)
        #system_error = sys.exc_info()
        #return jsonify(e.with_traceback(system_error[2])), 403
        return jsonify(error='ValidationError', error_description=str(e)), 403
   
    @app.errorhandler(GetTokenError)
    def handle_object_not_found_error(e):
        print(e)
        return jsonify({'GetTokenError': str(e)}), 403

    @app.errorhandler(InvalidPayload)
    def handle_object_not_found_error(e):
        print(e)
        return jsonify(error='InvalidPayload',
                        error_description=str(e)), 400
    
    @app.errorhandler(DataError)
    def handle_obs_error(e):
        print("DataError")
        return jsonify(error="DataError",error_description=e, code = e.code)
    
    @app.errorhandler(DataNotFound)
    def handle_obs_error(e):
        return jsonify(error="DataNotFound",error_description=str(e), code = 800), 200
