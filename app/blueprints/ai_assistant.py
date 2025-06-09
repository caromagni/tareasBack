from apiflask import APIBlueprint
from common.bedrock_service import invoke_bedrock_model
from flask import request, jsonify, current_app
from common.auth import verify_header
from common.error_handling import ValidationError
from common.cache import cache
from models.tarea_model import get_all_tarea_detalle
from schemas.schemas import ActuacionOut, TipoActuacionOut,TareaAllOut
from datetime import datetime
from decorators.role import require_role

ai_assistant = APIBlueprint('ai_assistant_blueprint', __name__)

@ai_assistant.post('/chat')
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        if not data or 'loggedUserData' not in data:
            return jsonify({"error": "No loggedUserData provided"}), 400

        user_message = data['message']
        loggedUser = data['loggedUserData']

        print("loggedUser", loggedUser['id'])

        # Fetch tasks and prepare context
        user_groups = ",".join([str(grupo['id_grupo']) for grupo in loggedUser["grupo"]])
        res, _ = get_all_tarea_detalle(grupos=user_groups)

        context="""Eres un asistente de sistema de gestion de tareas, el usuario es el que viene en loggedUser (loggedUser['nombre_completo']) te puede preguntar por informacion de las tareas.
        El usuario pertenece a uno o mas grupos, las tareas están asignadas a un grupo y a un usuario de ese grupo.
        A continuacion tendras los datos de las tareas de los grupos del usuario sin finalizar ni eliminar (solo debes informar tareas abiertas o en progreso, tarea_estado == 1 o 2). , 
        provenientes de la base de datos.
        Luego de los datos, vendran las preguntas del usuario dentro de un arreglo de mensajes, cada mensaje(objeto) tendra in "isUser" para denotar si es el mensage de usuario o tu respuesta.
        y un campo "text" con el contenido del mensaje. 
        Si no encuentras tareas, debes responder amablemente que no hay resultados para esa consultta.
        Debes mostrar el nombre de la tarea, la fecha de vencimiento, el estado de la tarea y a quien se encuentra asignada (nombre_completo cuando asignada=true).
        La respuesta debe ser en lenguaje natural, en español, breve y concisa. Las distintas tareas deben mostrarse en formato de listado, numeradas ascendentemente por orden de venciminento.
        una debajo de otra para mejorar la visualización.
       ( A modo de ejemplo debes indicarlas así: 
        1. Titulo, Fecha de vencimiento, estado, usuario asignado.
        2. Titulo, Fecha de vencimiento, estado, usuario asignado.
        3. Titulo, Fecha de vencimiento, estado, usuario asignado.
        ...)
        Si solicita las tareas finalizadas, mostrar tareas en estado 3, indicando que usuario la finalizó
        No debe incluir detalles innecesarios. No debes mostrar los id de la base de datos
        No debes mostrar el formato de los datos. 
        Si el usuario indica la palabra "mis", "mi", "mí" o "mias" en el mensaje, debes mostrar solo las tareas asignadas al usuario logueado que es el que viene en loggedUser (usuario: [{id_usuario==loggedUser['id'] && asignada==true}]).
        Después del análisis, ofrece ver más detalles una tarea en particular segun el número listado (solicita que te indique el número de la tarea que desea visualizar).

        datos de tareas:
        [
            {
                id_tarea: id de la tarea
                id_grupo: id del grupo al que pertenece la tarea
                titulo: nombre de la tarea
                cuerpo: descripcion de la tarea
                estado: estado de la tarea (abierta, cerrada, en progreso)
                tipo_actuacion: tipo de actuacion de la tarea (tipo_actuacion)
                caratula_expediente: caratula expediente de la tarea
                actuacion: actuacion de la tarea (actuacion)
                fecha_creacion: fecha de creacion de la tarea
                fecha_modificacion: fecha de modificacion de la tarea
            }
        ]
        datos de tarea asignada a usuario:
        [
            {
                id_tarea: id de la tarea
                id_usuario: id del usuario asignado a la tarea
                nombre_completo: nombre completo del usuario asignado a la tarea
                fecha_asignacion: fecha de asignacion de la tarea
                fecha_vencimiento: fecha de vencimiento de la tarea
                fecha_realizacion: fecha de realizacion de la tarea
            }
        ]   
        
        """

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": context+str(TareaAllOut().dump(res, many=True))+str(user_message)+str(loggedUser)}] 
                }
            ]
        }

        # Call Bedrock
        print("Request body for Bedrock:")
        print(datetime.now())
        response_body = invoke_bedrock_model(
            model_id='anthropic.claude-3-sonnet-20240229-v1:0',
            request_body=request_body
        )
        print("Response body from Bedrock:")
        print(datetime.now())
        return jsonify({"response": response_body['content'][0]['text']})

    except Exception as err:
        current_app.logger.error(f"Error in chat endpoint: {str(err)}")
        return jsonify({"error": str(err)}), 500