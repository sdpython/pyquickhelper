# coding: utf-8
"""
Setup commands used by package
`pyquickhelper <https://github.com/sdpython/pyquickhelper>`_.
"""

__version__ = "0.2"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__license__ = "MIT License"


from .simple import SetupCommandDisplay
from .pyquick import (
    SetupCommandBuildScript,
    SetupCommandCleanSpace,
    SetupCommandHistory,
    SetupCommandLab,
    SetupCommandLocalJenkins,
    SetupCommandNotebook,
    SetupCommandSphinx,
    SetupCommandUnitTests,
    SetupCommandUnitTestGUI,
    SetupCommandUnitTestLONG,
    SetupCommandUnitTestSKIP,
    SetupCommandVersion)
from .helper import _clean_readme


def default_cmdclass():
    """
    Defines additional setup command.
    """
    return {'build_script': SetupCommandBuildScript,
            'build_sphinx': SetupCommandSphinx,
            'clean_space': SetupCommandCleanSpace,
            'display': SetupCommandDisplay,
            'history': SetupCommandHistory,
            'lab': SetupCommandLab,
            'local_jenkins': SetupCommandLocalJenkins,
            'notebook': SetupCommandNotebook,
            'unittests': SetupCommandUnitTests,
            'unittests_GUI': SetupCommandUnitTestGUI,
            'unittests_LONG': SetupCommandUnitTestLONG,
            'unittests_SKIP': SetupCommandUnitTestSKIP,
            'write_version': SetupCommandVersion}


def read_version(setup_file, name, default_value=None, subfolder=None):
    """
    Extracts version from file `__init__.py` without importing the
    module.

    :param setup_file: setup file calling this function,
        used to guess the location of the package
    :param name: name of the package
    :param default_value: if not found, falls back to that value
    :param subfolder: if the package is in a subfolder like `src`
    :return: version
    :raise: RuntimeError if the returned version is None
    """
    import os
    version_str = default_value
    TOP_DIR = os.path.abspath(os.path.dirname(setup_file))
    if not os.path.exists(TOP_DIR):
        if version_str is None:
            raise FileNotFoundError(
                "Unable to find folder %r." % TOP_DIR)
    else:
        if subfolder is None:
            init = os.path.join(TOP_DIR, name, '__init__.py')
        else:
            init = os.path.join(TOP_DIR, subfolder, name, '__init__.py')
        looked = []
        with open(init, "r") as f:
            line = [_ for _ in [_.strip("\r\n ") for _ in f.readlines()]
                    if _.startswith("__version__")]
            if len(line) > 0:
                looked = line
                version_str = line[0].split('=')[1].strip('" \'')
        if version_str is None:
            raise RuntimeError(
                "Unable to extract version from file %r, "
                "interesting lines %r." % (init, looked))
    if version_str is None:
        raise RuntimeError(
            "Unable to extract version from path %r. Content is %r." % (
                TOP_DIR, os.listdir(TOP_DIR)))
    return version_str


def read_readme(setup_file, name="README.rst"):
    """
    Extracts version from file `__init__.py` without importing the
    module.

    :param setup_file: setup file calling this function,
        used to guess the location of the package
    :param name: name of the readme
    :return: content
    """
    import os
    TOP_DIR = os.path.abspath(os.path.dirname(setup_file))
    if not os.path.exists(TOP_DIR):
        raise FileNotFoundError(
            "Unable to find folder %r." % TOP_DIR)
    readme = os.path.join(TOP_DIR, name)
    if not os.path.exists(readme):
        raise FileNotFoundError(
            "Unable to find file %r." % TOP_DIR)
    with open(readme, "r", encoding="utf-8") as f:
        content = f.read()
    return _clean_readme(content)
