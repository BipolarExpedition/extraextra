import os
import sys

# Set project root directory for Sphinx documentation
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'extraextra'
author = 'BipolarExpedition({authorName})'
release = '0.0.1'

# Configure other options as necessary, such as:
html_theme = 'alabaster'  # Example, can choose others like 'sphinx_rtd_theme'

# simply add the extension to your list of extensions
extensions = ['myst_parser']

source_suffix = ['.rst', '.md']
