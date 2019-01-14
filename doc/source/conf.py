# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
#  nova documentation build configuration file
#
# Refer to the Sphinx documentation for advice on configuring this file:
#
#   http://www.sphinx-doc.org/en/stable/config.html

import os
import sys

from deepaas import version

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('./'))

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.

extensions = ['sphinx.ext.autodoc',
              'oslo_config.sphinxconfiggen',
              'oslo_config.sphinxext',
              "reno.sphinxext",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

config_generator_config_file = '../../etc/deepaas-config-generator.conf'
sample_config_basename = '_static/deepaas'

todo_include_todos = True

source_parsers = {
   '.md': 'recommonmark.parser.CommonMarkParser',
}

# The suffix of source filenames.
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'DEEP-Hybrid-DataCloud'
copyright = u'2017-present, <a href="https://deep-hybrid-datacloud.eu">DEEP-Hybrid-DataCloud</a> consortium'
author = u"DEEP-Hybrid-DataCloud consortium"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = version.release_string
# The short X.Y version.
version = version.version_string

# A list of glob-style patterns that should be excluded when looking for
# source files. They are matched against the source file names relative to the
# source directory, using slashes as directory separators on all platforms.
exclude_patterns = []

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['deepaas.']

# -- Options for man page output ----------------------------------------------


# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('cli/deepaas-run', "deepaas-run", "DEEPaaS API", [author], 1),
    (master_doc, 'deepaas', u'DEEPaaS documentation', [author], 1),
]

# If true, show URL addresses after external links.
#man_show_urls = False

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'logo': 'logo.png',
    'show_powered_by': False,
    'github_user': 'indigo-dc',
    'github_repo': 'DEEPaaS',
    'github_banner': False,
    'show_related': False,
    'note_bg': '#FFF59C',
    'description': 'DEEPaaS is an API for machine learning models',
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any paths that contain "extra" files, such as .htaccess or
# robots.txt.
html_extra_path = ['_extra']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%Y-%m-%d %H:%M'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = False


# Custom sidebar templates, maps document names to template names.
html_sidebars = {
#    'index':    ['sidebar.html', 'sourcelink.html', 'searchbox.html'],
#    '**':       ['sidebar.html', 'localtoc.html', 'relations.html',
#                 'sourcelink.html', 'searchbox.html'],
    'index':       ['about.html', 'navigation.html', 'relations.html',
                 'sourcelink.html', 'searchbox.html', 'sidebarfooter.html'],
}


# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'DEEPaaSdoc'

# -- Options for LaTeX output -------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index', 'deepaas.tex', u'DEEPaaS Documentation',
     author, 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = "_static/logo.png"

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True
