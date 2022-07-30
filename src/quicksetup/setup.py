# coding: utf-8
"""
Defines the setup for *pyquicksetup*.
"""
import os
from setuptools import find_packages, setup

project_var_name = "pyquicksetup"
packages = find_packages()
package_dir = {k: os.path.join('.', k.replace(".", "/")) for k in packages}


def read_version():
    version_str = '0.2.4'
    TOP_DIR = os.path.abspath(os.path.dirname(__file__))
    with (open(os.path.join(
            TOP_DIR, 'pyquicksetup', '__init__.py'), "r")) as f:
        line = [_ for _ in [_.strip("\r\n ") for _ in f.readlines()]
                if _.startswith("__version__")]
        if len(line) > 0:
            version_str = line[0].split('=')[1].strip('" ')
    return version_str


CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]

setup(
    name=project_var_name,
    version=read_version(),
    author='Xavier Dupré',
    author_email='xavier.dupre@gmail.com',
    license="MIT",
    url="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html",
    download_url="https://github.com/sdpython/pyquickhelper",
    description="Predefined setup commands relying on pyquickhelper.",
    long_description="Predefined setup commands relying on pyquickhelper.",
    keywords=['pyquickhelper', 'setup', 'pyquicksetup'],
    classifiers=CLASSIFIERS,
    install_requires=["setuptools"],
    packages=packages,
    package_dir=package_dir,
)
