
import os
from common.keycloak import get_public_key

os.environ.setdefault('postgres_user', 'NOT_SET')
os.environ.setdefault('postgres_password', 'NOT_SET')
class Config:
    # General configuration
    SLEEP=30
    AUTH_URL=os.getenv('AUTH_URL')
    REALM=os.getenv('REALM')
    # Database configuration
    POSGRESS_USER = os.environ.get('postgres_user') 
    POSGRESS_PASSWORD = os.environ.get('postgres_password')
    POSGRESS_BASE = os.environ.get('postgres_base')

    PROPAGATE_EXCEPTIONS = True

    #SQLALCHEMY_DATABASE_URI = os.getenv("SETTINGS_CONECTION")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SHOW_SQLALCHEMY_LOG_MESSAGES = False

    ERROR_404_HELP = False

    SERVERS = [
        {
            'name': 'localhost',
            'url': 'http://localhost:5005'
        },
        {
            'name': 'localhost',
            'url': 'http://172.17.0.2:5005'
        },
        {
            'name': 'localhost',
            'url': 'http://localhost:3000'
        }    
    ]
    DESCRIPTION='APIs Sistema de Tareas'
    TITLE='APIs Tareas'
    MAX_ITEMS_PER_RESPONSE=os.getenv('MAX_ITEMS_PER_RESPONSE')
    

    # JWT DECODE CONFIG
    #JWT_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkc4U80tR0RofRTdcUm07Nv/aK4dZqv7oZAARl7tv0Y6lUHkdkgAhoXMm3Q7+HPOwy8df7zm2bGhTAZyl65o9W9CNoQlEQCmP/DoeizLoRcrNsaLAYXOCrERUw4oqgo4j1N7hboPtdGJJ7bSyngWoRkFT1HRxm0yHnDA8XYhR6DUG5JOeHX6BTUWCopAOGzWQwruG9WB+MCHv9FQnD7TjnukodIuTCOFCeY9yJeqTcct3p8tb6hZmxsOahZvmXc3kXCvO95uJE2Hzl3l4bVVhWvLqXgg+hwQ3GyGPMqEqQx+n3R8fCVQhkRVz1V83mJ0I9YVPMUUcCE0xuI/sbWEZFQIDAQAB' + "\n-----END PUBLIC KEY-----"
    #JWT_ALGORITHM = "RS256"
    #JWT_DECODE_AUDIENCE = "pyapis"
    #JWT_IDENTITY_CLAIM = "jti"
    print(AUTH_URL)

    JWT_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + get_public_key(AUTH_URL,REALM) + "\n-----END PUBLIC KEY-----"
    JWT_ALGORITHM = "RS256"
    JWT_DECODE_AUDIENCE = os.getenv("AUDIENCE")
    JWT_IDENTITY_CLAIM = "jti"

    # RabbitMQ configuration
    RABBITMQ_USER = os.getenv('RABBITMQ_USER')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST')

    