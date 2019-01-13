# -*- coding: utf-8 -*-
"""
@file
@brief Configuration for sphinx documentation.
"""
import sys
import os
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
from pyquickhelper.helpgen.default_conf import set_sphinx_variables, get_default_stylesheet

set_sphinx_variables(__file__, "pyquickhelper", "Xavier Dupré", 2019,
                     "sphinx_rtd_theme", [
                         sphinx_rtd_theme.get_html_theme_path()], locals(),
                     github_repo="https://github.com/sdpython/pyquickhelper.git",
                     extlinks=dict(issue=(
                         'https://github.com/sdpython/pyquickhelper/issues/%s',
                         'issue ')),
                     link_resolve="http://www.xavierdupre.fr/app/")

# there is an issue with this attribute on Anaconda math_number_all
assert math_number_all or not math_number_all
blog_root = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/"

# remove notebooks following this pattern
nbneg_pattern = ".*[\\\\/]temp_.*"

html_context = {
    'css_files': get_default_stylesheet() + ['_static/my-styles.css', '_static/gallery.css'],
}
