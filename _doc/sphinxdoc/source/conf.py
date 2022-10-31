# -*- coding: utf-8 -*-
"""
@file
@brief Configuration for sphinx documentation.
"""
import sys
import os
import alabaster

sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
from pyquickhelper.helpgen.default_conf import set_sphinx_variables


set_sphinx_variables(__file__, "pyquickhelper", "Xavier Dupré", 2022,
                     "alabaster", alabaster.get_path(),
                     locals(),
                     github_repo="https://github.com/sdpython/pyquickhelper.git",
                     extlinks=dict(issue=(
                         'https://github.com/sdpython/pyquickhelper/issues/%s',
                         'issue ')),
                     link_resolve="http://www.xavierdupre.fr/app/")

extensions.append([
    "bokeh.sphinxext.bokeh_autodoc",
    "bokeh.sphinxext.bokeh_dataframe",
    "bokeh.sphinxext.bokeh_color",
    "bokeh.sphinxext.bokeh_enum",
    "bokeh.sphinxext.bokeh_example_metadata",
    "bokeh.sphinxext.bokeh_gallery",
    "bokeh.sphinxext.bokeh_jinja",
    "bokeh.sphinxext.bokeh_model",
    "bokeh.sphinxext.bokeh_options",
    "bokeh.sphinxext.bokeh_palette",
    "bokeh.sphinxext.bokeh_palette_group",
    "bokeh.sphinxext.bokeh_plot",
    "bokeh.sphinxext.bokeh_prop",
    "bokeh.sphinxext.bokeh_releases",
    "bokeh.sphinxext.bokeh_roles",
    "bokeh.sphinxext.bokeh_sampledata_xref",
    "bokeh.sphinxext.bokeh_settings",
    "bokeh.sphinxext.bokeh_sitemap",
    "bokeh.sphinxext.bokehjs_content",
])

# there is an issue with this attribute on Anaconda math_number_all
assert math_number_all or not math_number_all
blog_root = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/"

# remove notebooks following this pattern
nbneg_pattern = ".*[\\\\/]temp_.*"

html_css_files = ['my-styles.css', 'gallery-dataframe.css']
