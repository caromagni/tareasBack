
import os
import sys

# Add the blueprint folder to sys.path
sys.path.insert(0, os.path.abspath('..'))
# sys.setrecursionlimit(1500)
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


# # Debugging: Print the current working directory and sys.path
# print("Current working directory:", os.getcwd())
# print("sys.path:", sys.path)


# import pkgutil

# # List all importable modules in sys.path
# print("Importable modules in sys.path:")
# for module_info in pkgutil.iter_modules():
#     print(module_info.name)

project = 'tareas'
copyright = '2024, Silvia Imperiale,Mauro Bonadeo,Carolina Magni,Martin Diaz'
author = 'Silvia Imperiale,Mauro Bonadeo,Carolina Magni,Martin Diaz'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinxcontrib.httpdomain',  # To handle HTTP APIs better in docs
]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
autosummary_generate = True  # Turn on sphinx.ext.autosummary
html_static_path = ['_static']

