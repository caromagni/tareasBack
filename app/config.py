
import os
#add default string values if variable is not exported
os.environ.setdefault('postgres_user', 'NOT_SET')
os.environ.setdefault('postgres_password', 'NOT_SET')
class Config:
    POSGRESS_USER = os.environ.get('postgres_user') 
    POSGRESS_PASSWORD = os.environ.get('postgres_password')

    PROPAGATE_EXCEPTIONS = True

    # Database configuration
    #SQLALCHEMY_DATABASE_URI = os.getenv("SETTINGS_CONECTION")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SHOW_SQLALCHEMY_LOG_MESSAGES = True

    ERROR_404_HELP = False

    SERVERS = [
        {
            'name': 'localhost',
            'url': 'http://192.168.68.201:5005'
        },
        {
            'name': 'localhost',
            'url': 'http://localhost:5005'
        }
    ]
    DESCRIPTION='APIs Sistema de Tareas'
    TITLE='APIs Tareas'

    # JWT DECODE CONFIG
    JWT_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkc4U80tR0RofRTdcUm07Nv/aK4dZqv7oZAARl7tv0Y6lUHkdkgAhoXMm3Q7+HPOwy8df7zm2bGhTAZyl65o9W9CNoQlEQCmP/DoeizLoRcrNsaLAYXOCrERUw4oqgo4j1N7hboPtdGJJ7bSyngWoRkFT1HRxm0yHnDA8XYhR6DUG5JOeHX6BTUWCopAOGzWQwruG9WB+MCHv9FQnD7TjnukodIuTCOFCeY9yJeqTcct3p8tb6hZmxsOahZvmXc3kXCvO95uJE2Hzl3l4bVVhWvLqXgg+hwQ3GyGPMqEqQx+n3R8fCVQhkRVz1V83mJ0I9YVPMUUcCE0xuI/sbWEZFQIDAQAB' + "\n-----END PUBLIC KEY-----"
    JWT_ALGORITHM = "RS256"
    JWT_DECODE_AUDIENCE = "pyapis"
    JWT_IDENTITY_CLAIM = "jti"
   