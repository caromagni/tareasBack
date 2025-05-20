import json
import os
import logging

# Configurar logger básico
logger = logging.getLogger("EPCache")
logging.basicConfig(level=logging.INFO)

class EPCache:
    _instance = None
    _data = None
    _archivo_json = "ep_cu.json"

    def __new__(cls, archivo_json=None):
        if cls._instance is None:
            cls._instance = super(EPCache, cls).__new__(cls)
            if archivo_json:
                cls._archivo_json = archivo_json
            cls._load_data()
        return cls._instance
    
    @classmethod
    def _load_data(cls):
        if not os.path.exists(cls._archivo_json):
            logger.error(f"[EPCache] El archivo '{cls._archivo_json}' no existe.")
            raise FileNotFoundError(f"Archivo '{cls._archivo_json}' no encontrado.")

        try:
            with open(cls._archivo_json, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)
            logger.info(f"[EPCache] Datos cargados desde '{cls._archivo_json}' ({len(cls._data)} endpoints).")
        except json.JSONDecodeError as e:
            logger.error(f"[EPCache] Error al parsear JSON: {str(e)}")
            raise

    def get_api_cu(self, url):
        if not url:
            logger.warning("[EPCache] URL no proporcionada.")
            return []

        for ep in self._data:
            if ep.get("url") == url:
                return [item["codigo"] for item in ep.get("caso_uso", [])]

        logger.info(f"[EPCache] No se encontraron casos de uso para la URL: {url}")
        return []
    
    #def recargar_cache(self, nuevo_archivo_json="ep_cu.json"):
    def recargar_cache(cls, archivo_json=None):
        if archivo_json:
            cls._archivo_json = archivo_json
        logger.info(f"[EPCache] Recargando cache desde '{cls._archivo_json}'...")
        cls._load_data()

    

