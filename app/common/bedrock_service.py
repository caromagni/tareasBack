import boto3
import os
import json
import time
from flask import jsonify, current_app
from schemas.schemas import ActuacionOut, TipoActuacionOut,TareaAllOut




# Initialize Bedrock client once
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-west-2'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def validate_bedrock_env():
    required_env_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    for var in required_env_vars:
        if not os.getenv(var):
            raise EnvironmentError("Missing required environment variable: {var}")

# Validate environment variables at startup
# validate_bedrock_env()

def invoke_bedrock_model(model_id, request_body):
    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        return json.loads(response.get('body').read())
    except Exception as e:
        raise RuntimeError(f"Error invoking Bedrock model: {e}")

