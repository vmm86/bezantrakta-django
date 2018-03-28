#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import django
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()


# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
]

if tags.has('dev'):
    extensions + [
        'sphinxcontrib.napoleon',
        # 'sphinxcontrib.email',
    ]

    # Napoleon settings
    napoleon_google_docstring = True
    napoleon_numpy_docstring = False
    napoleon_include_init_with_doc = False
    napoleon_include_private_with_doc = False
    napoleon_include_special_with_doc = False
    napoleon_use_admonition_for_examples = False
    napoleon_use_admonition_for_notes = False
    napoleon_use_admonition_for_references = False
    napoleon_use_ivar = False
    napoleon_use_param = True
    napoleon_use_rtype = True
    napoleon_use_keyword = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['docs/_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'
if tags.has('adm'):
    master_doc = 'index_adm'
elif tags.has('dev'):
    master_doc = 'index_dev'

# General information about the project.
project = 'bezantrakta-django'
copyright = '2017-2018 Michail Vasilyev https://github.com/vmm86'
author = 'Michail Vasilyev https://github.com/vmm86'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# version - The short X.Y version.
# release - The full version, including alpha/beta/rc tags.
version = release = '3.3'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'ru'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    'docs/adm',
    'docs/dev',
]
if tags.has('adm'):
    exclude_patterns += [
        'index_dev*',
        '**/index_dev*',

        '**/context_processors*',
        '**/middleware*',

        'api/*',

        'bezantrakta/eticket/*',
        'bezantrakta/seo/*',
        'bezantrakta/index_dev*',

        'project',

        'README*',
    ]
elif tags.has('dev'):
    exclude_patterns += [
        # '**/admin',

        'index_adm*',
        '**/index_adm*',
    ]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Custom roles
rst_prolog = """
.. role:: deleted
  :class: deleted

.. role:: green
  :class: green

.. role:: yellow
  :class: yellow

.. role:: red
  :class: red
"""

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'collapse_navigation': False,
    'display_version': True,
    'navigation_depth': 3,
}

html_logo = 'project/static/svg/bzlogo.svg'
html_favicon = 'project/static/ico/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['docs/_static']

html_add_permalinks = '🔗'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

html_experimental_html5_writer = True


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'bezantrakta-djangodoc'


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'bezantrakta-django', 'bezantrakta-django documentation',
     [author], 1)
]


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/3.5': None}


# -- Autodoc options ------------------------------------------------------
autodoc_default_flags = ['members', 'private-members', 'special-members', 'show-inheritance']
autodoc_member_order = 'bysource'
autoclass_content = 'both'


# Custom CSS style overriding theme CSS styles
def setup(app):
    app.add_stylesheet('css/theme_override.css')