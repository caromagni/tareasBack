import os
import sys

# Agregar la carpeta de blueprints a sys.path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('./../modulos'))


import sphinx_pdj_theme



# Archivo de configuración para el generador de documentación Sphinx

project = 'tareas'
copyright = '2024 Direccion de Informatica SCJ - Martin Diaz, Silvia Imperiale, Mauro Bonadeo, Carolina Magni'
author = '2024 Direccion de Informatica SCJ - Martin Diaz, Silvia Imperiale, Mauro Bonadeo, Carolina Magni '

extensions = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.httpdomain'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
#html_theme = 'conestack'
#html_theme = 'sphinx_pdj_theme'
html_theme_path = [sphinx_pdj_theme.get_html_theme_path()]
html_static_path = ['_static']

# Configuración de las páginas del manual
master_doc = 'index'



# Leer el contenido de index_content.txt
with open(os.path.join(os.path.dirname(__file__), 'index.rst'), 'r') as f:
    index_content = f.read()

# # Crear el contenido para el archivo index.rst
# index_content = '''
# Documentación de Tareas
# =========================================

# .. toctree::
#    :maxdepth: 2
#    :caption: Contenido:

#    introduccion
#    arquitectura
#    referencia_api
#    /modulos/alertas
#    /modulos/bandeja_principal
#    /modulos/calendario
#    /modulos/contenido_multimedia
#    /modulos/creacion_tarea
#    /modulos/grupos
#    /modulos/tareas_anidadas
#    /modulos/tareas_automaticas
#    /modulos/tareas_fechas_intermedias
#    /modulos/tareas_personales
#    /modulos/tareas_programadas
#    /modulos/tareas_recurrentes
#    /modulos/visibilidad_externa

# Índices y tablas
# ================

# * :ref:`genindex`
# * :ref:`modindex`
# * :ref:`search`
# '''



# Configurar el idioma a español
language = 'es'
