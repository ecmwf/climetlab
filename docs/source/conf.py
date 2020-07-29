# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import datetime
import os
import sys

top = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, top)


import climetlab


source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"
html_theme_options = {"logo_only": True}
html_logo = "_static/logo.png"


# -- Project information -----------------------------------------------------

project = 'CliMetLab'

author = 'ECMWF'

year = datetime.datetime.now().year
if year == 2020:
    years = "2020"
else:
    years = "2020-%s" % (year,)

copyright = '%s, ECMWF' % (years,)


# The full version, including alpha/beta/rc tags
release = climetlab.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    # "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",

    'nbsphinx',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'sphinx-prompt',
    'climetlab.sphinxext.sources',
    # 'climetlab.sphinxext.datasets',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


nbsphinx_prolog = """
{% set docname = env.doc2path(env.docname, base=None) %}

You can run this notebook in |Binder| or in |Colab|.

.. |Binder| image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/ecmwf/climetlab/master?urlpath=lab/tree/docs/source/{{ docname }}


.. |Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/googlecolab/ecmwf/climetlab/master/docs/source/{{ docname }}

"""


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
