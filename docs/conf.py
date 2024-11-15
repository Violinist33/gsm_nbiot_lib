# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sim7020py'
copyright = '2024, Antonii Lupandin'
author = 'Antonii Lupandin'
release = '0.1.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Добавляем необходимые расширения
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',          # Поддержка Google и NumPy docstring стилей
    'sphinx_autodoc_typehints',      # Для отображения аннотаций типов
]

# Указываем путь к проекту, чтобы Sphinx мог найти модули
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Mocking imports for modules not available in the build environment
autodoc_mock_imports = [
    'machine',
    'utime',
    'network',
    'json',
    # Добавьте другие модули по необходимости
]
