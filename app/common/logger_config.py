import logging
import os
from logging.handlers import TimedRotatingFileHandler

""" logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
) """

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()  # Por defecto: DEBUG
# Validar nivel
valid_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Usar nivel válido o default (DEBUG)
level = valid_levels.get(LOG_LEVEL, logging.DEBUG)

# --- Crear carpeta de logs ---
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Crear logger principal
logger = logging.getLogger(__name__)


logger.setLevel(level)  # Nivel global del logger

if not logger.hasHandlers():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler consola (WARNING+)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler archivo rotativo diario
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when='midnight', interval=1, backupCount=7, encoding='utf-8'
    )
    #file_handler.setFormatter(formatter)
    #logger.addHandler(file_handler)


logger.info("Logger configurado correctamente")
logger.debug("Nivel de log actual: %s", LOG_LEVEL)



