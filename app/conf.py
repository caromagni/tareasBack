import os
import sys

# Agregar la carpeta de blueprints a sys.path
sys.path.insert(0, os.path.abspath('..'))

# Archivo de configuración para el generador de documentación Sphinx

project = 'tareas'
copyright = '2024, Silvia Imperiale, Mauro Bonadeo, Carolina Magni, Martin Diaz'
author = 'Silvia Imperiale, Mauro Bonadeo, Carolina Magni, Martin Diaz'

extensions = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.httpdomain'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

#html_theme = 'alabaster'
html_theme = 'conestack'

html_static_path = ['_static']

# Configuración de las páginas del manual
master_doc = 'index'

# Crear el contenido para el archivo index.rst
index_content = '''
Documentación de Tareas
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contenido:

   introduccion
   arquitectura
   referencia_api

Índices y tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

# Escribir el archivo index.rst
with open(os.path.join(os.path.dirname(__file__), 'loindex.rst'), 'w') as f:
    f.write(index_content)

# Configurar el idioma a español
language = 'es'
