# coding: utf-8
import sys
import os
import alabaster
from pyquickhelper.helpgen.default_conf import set_sphinx_variables

sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))

set_sphinx_variables(__file__, "python3_module_template", "Xavier Dupré", 2021,
                     "alabaster", alabaster.get_path(), locals(), add_extensions=['alabaster'],
                     extlinks=dict(issue=(
                         'https://github.com/sdpython/python3_module_template/issues/%s',
                         'issue %s')))

blog_root = "http://www.xavierdupre.fr/app/python3_module_template/helpsphinx/"

notebooks_urls = "http://www.xavierdupre.fr/app/python3_module_template/helpsphinx/notebooks/"

nblinks = {
    'slideshowrst': notebooks_urls + 'slide_show.html',
}
