#-*- coding: utf-8 -*-
import sys
import os
import datetime
import re
import solar_theme

sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
from pyquickhelper.helpgen.default_conf import set_sphinx_variables
set_sphinx_variables(__file__,
                     "pyquickhelper",
                     "Xavier Dupré",
                     2014,
                     "solar_theme",
                     solar_theme.theme_path,
                     locals())
