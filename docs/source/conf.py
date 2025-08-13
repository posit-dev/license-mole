# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'license-mole'
copyright = '2025, Posit Software PBC'
author = 'Posit Software PBC'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
   'sphinx.ext.autodoc',
   'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src')))
print(sys.path)

napoleon_use_param = True
napoleon_use_ivar = True
napoleon_preprocess_types = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
