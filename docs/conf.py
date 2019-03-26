#!/usr/bin/env python3

"""Sphinx configuration."""

# pylint: disable=invalid-name

from innoconv.metadata import __author__, __version__

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_click.ext',
]

templates_path = []
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'innoConv'
copyright = '2018, innoCampus, TU Berlin'  # pylint: disable=w0622
author = __author__

version = __version__
release = __version__  # The full version, including alpha/beta/rc tags.

language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = True
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.6', None),
}

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'style_external_links': True,
}
html_static_path = []
html_sidebars = {
    '**': [
        'globaltoc.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'innoconvdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'innoconv.tex', 'innoConv Documentation',
     'Innocampus', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'innoconv', 'innoConv Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'innoconv', 'innoConv Documentation',
     author, 'innoconv', 'Converter for educational content.',
     'Miscellaneous'),
]
