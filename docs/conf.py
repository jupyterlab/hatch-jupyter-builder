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
from importlib.metadata import version as package_version

# -- Project information -----------------------------------------------------

project = "hatch-jupyter-builder"
copyright = "2022, Project Jupyter"
author = "Project Jupyter"

# The full version, including alpha/beta/rc tags
__version__ = package_version("hatch_jupyter_builder")
# The short X.Y version.
version_parsed = tuple(__version__.split("."))
version = ".".join(version_parsed[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx_autodoc_typehints",
]

try:
    import enchant

    extensions += ["sphinxcontrib.spelling"]
except ImportError:
    pass

myst_enable_extensions = ["html_image"]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_theme_options = {"navigation_with_keys": False}

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": {"https://docs.python.org/3/": None}}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


import shutil
from pathlib import Path

HERE = Path(__file__).parent.resolve()


def setup(_):
    dest = HERE / "source" / "reference" / "changelog.md"
    shutil.copy(HERE / ".." / "CHANGELOG.md", dest)
