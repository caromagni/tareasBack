from apiflask import APIBlueprint
from flask import current_app, jsonify, request
import boto3
import json
import os

from models.actuacion_model import get_all_actuaciones, get_all_tipoactuaciones
from schemas.schemas import ActuacionOut, TipoActuacionOut
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

        user_message = data['message']

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
                    "content": [{"type": "text", "text": str(user_message)}] 
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
