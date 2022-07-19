# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, Extension, find_packages
from pyquicksetup import read_version, read_readme, default_cmdclass

project_var_name = "python3_module_template"
github_owner = "sdpython"
versionPython = f"{sys.version_info.major}.{sys.version_info.minor}"
path = "Lib/site-packages/" + project_var_name
readme = 'README.rst'
history = "HISTORY.rst"
requirements = None

KEYWORDS = project_var_name + ""
DESCRIPTION = ""
CLASSIFIERS = []

packages = find_packages('src', exclude='src')
package_dir = {k: "src/" + k.replace(".", "/") for k in packages}
package_data = {}

setup(
    name=project_var_name,
    version="0.1",
    author='Xavier Dupré',
    author_email='xavier.dupre@gmail.com',
    license="MIT",
    url="",
    download_url="",
    description=DESCRIPTION,
    long_description="",
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=packages,
    package_dir=package_dir,
    package_data=package_data,
    ext_modules=[],
    cmdclass=default_cmdclass(),
    install_requires=[]
)
