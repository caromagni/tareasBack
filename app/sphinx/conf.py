import os
import sys

# Agregar la carpeta de blueprints a sys.path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('./../modulos'))
#sys.path.insert(0, os.path.abspath('./sphinx'))
#sys.path.insert(0, os.path.abspath('../modulos'))



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

# Configuración para incluir CSS personalizado
html_css_files = [
    'custom.css',
]

# Configuración de las páginas del manual
master_doc = 'index'

# Configuración del tema para mejorar la navegación
html_theme_options = {
    'navigation_depth': 2,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'globaltoc_collapse': False,
    'globaltoc_maxdepth': 2,
}

# Configurar el idioma a español
language = 'es'
