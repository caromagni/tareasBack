from apiflask import APIBlueprint
from flask import current_app, jsonify, request
import boto3
import json
import os
from datetime import datetime
from models.tarea_model import get_tarea_grupo, get_all_tarea_detalle
from schemas.schemas import ActuacionOut, TipoActuacionOut,TareaAllOut
from common.error_handling import ValidationError

ai_assistant = APIBlueprint('ai_assistant', __name__)

@ai_assistant.post('/chat')
def chat():
    """
    Chat with AI Assistant.
    ==============

    **Chat with Claude 3.5 (Sonnet) via AWS Bedrock**
 
    :return: JSON object with assistant's response or an error message.
    :rtype: json
    """
    try:
        # Get the message from request
        data = request.get_json()
       
        if not data or 'message' not in data:
            return jsonify({
                "error": "No message provided"
            }), 400
        if not data or 'loggedUserData' not in data:
            return jsonify({
                "error": "No loggedUserData provided"
            }), 400
        context="""Eres un asistente de sistema de gestion de tareas,el usuario te puede preguntar por informacion de sus tareas.
        el usuario pertenece a uno o mas grupos, cada grupo puede tener una o mas tareas asignadas.
        a continuacion tendras los datos de las tareas del usuario provenientes de la base de datos.
        luego de los datos, vendran las preguntas del usuario dentro de un arreglo de mensajes, cada mensaje(objeto) tendra in "isUser" para denotar si es el mensage de usuario o tu respuesta.
        y un campo "text" con el contenido del mensaje.

        datos de tareas:
        

        """
        user_message = data['message']
        loggedUser = request.get_json()['loggedUserData']

        #check if ai_temp_data folder exists if not create it
        if not os.path.exists('ai_temp_data'):
            os.makedirs('ai_temp_data')

        #fetch all tasks related to the user and save it in a json file in the temp folder with the user id as filename
        print('user group id is')
        user_groups=[]
        for grupo in loggedUser["grupo"]:
            print("ID GRUPO FOR USER")
            print(grupo['id_grupo'])
            user_groups.append(grupo['id_grupo'])
        print("group array is")
        print(user_groups)
        res,cant=get_all_tarea_detalle(grupos=user_groups)
        print("got all user tasks")
        print(res)    
        date_now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'ai_temp_data/{loggedUser["id"]+"_"+date_now}.json', 'w') as f:
            json.dump(TareaAllOut().dump(res, many=True), f, default=str)
         
        # Initialize Bedrock Runtime client
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        # Prepare the request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": context+str(TareaAllOut().dump(res, many=True))+str(user_message)}] 
                }
            ]
        }

        # Invoke the model
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(request_body)
        )

        # Parse the response
        response_body = json.loads(response.get('body').read())
        
        # Return the response
        return jsonify({
            "response": response_body['content'][0]['text']
        })

    except Exception as err:
        current_app.logger.error(f"Error in chat endpoint: {str(err)}")
        return jsonify({
            "error": str(err)
        }), 500
