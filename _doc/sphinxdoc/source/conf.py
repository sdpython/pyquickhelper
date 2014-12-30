#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  documentation build configuration file, created by
# sphinx-quickstart on Fri May 10 18:35:14 2013.
#

import sys, os, datetime, re
import solar_theme

sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
from pyquickhelper.helpgen.default_conf import set_sphinx_variables
set_sphinx_variables(   __file__,
                        "pyquickhelper",
                        "Xavier Dupré",
                        2014,
                        "solar_theme",
                        solar_theme.theme_path,
                        locals())