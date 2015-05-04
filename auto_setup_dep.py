
import sys
from distutils.core import setup, Extension
import distutils.sysconfig as SH
from setuptools import find_packages

project_var_name = "dependencies_pyquickhelper"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name

setup(
    name=project_var_name,
    version=versionPython,
    install_requires=[
        "numpy",
        "dateutils",
        "IPython",
        "matplotlib",
        "sphinx",
        "pandas",
        "docutils", ],
)
