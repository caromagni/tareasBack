import logging
import os
from logging.handlers import TimedRotatingFileHandler

""" logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
) """

# Crear logger principal
logger = logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)  # Nivel global del logger

# --- FORMATO DE LOG ---
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- HANDLER PARA CONSOLA ---
console_handler = logging.StreamHandler()
#console_handler.setLevel(logging.WARNING)  # Solo WARNING o superior
console_handler.setFormatter(formatter)

# --- HANDLER PARA ARCHIVO ROTATIVO (1 archivo por día, retiene 7 días) ---
file_handler = TimedRotatingFileHandler(
    filename='logs/app.log',
    when='midnight',       # Rota a la medianoche
    interval=1,            # Cada 1 día
    backupCount=7,         # Guarda 7 archivos anteriores
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)  # Guarda todo
file_handler.setFormatter(formatter)

# --- AGREGAR HANDLERS AL LOGGER ---
logger.addHandler(console_handler)
logger.addHandler(file_handler)


logger.info("Logger configurado correctamente")


