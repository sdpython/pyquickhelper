# coding: utf-8
"""
Defines the setup for *pyquickhelpersetup*.
"""

from distutils.core import setup  # pylint: disable=E0401, E0611
from setuptools import find_packages  # pylint: disable=W0611

project_var_name = "pyquickhelpersetup"

CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Topic :: Engineering',
    'Topic :: Education',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]

setup(
    name=project_var_name,
    version='0.1',
    author='Xavier Dupré',
    author_email='xavier.dupre@gmail.com',
    license="MIT",
    url="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html",
    download_url="https://github.com/sdpython/pyquickhelper",
    description="Predefined setup commands relying on pyquickhelper",
    long_description="Predefined setup commands relying on pyquickhelper",
    keywords=['pyquickhelper', 'setup'],
    classifiers=CLASSIFIERS,
    install_requires=["setuptools"],
    py_modules=["pyquickhelpersetup"],
)
