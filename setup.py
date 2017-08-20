# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os

from distutils.core import setup, Extension
import distutils.sysconfig as SH
from setuptools import find_packages

#########
# settings
#########

project_var_name = "pyquickhelper"
sversion = "1.5"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name
readme = 'README.rst'
history = "HISTORY.rst"
requirements = None

KEYWORDS = project_var_name + \
    ', synchronization, files, documentation, Xavier, Dupré'
DESCRIPTION = "Various functionalities: folder synchronization, a logging function, " + \
              "helpers to generate documentation with sphinx, generation of code for Python 2.7 from Python 3"
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering',
    'Topic :: Education',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]

#######
# data
#######

packages = find_packages('src', exclude='src')
package_dir = {k: "src/" + k.replace(".", "/") for k in packages}
package_data = {project_var_name + ".sphinxext": ["*.png"],
                project_var_name + ".ipythonhelper": ["*.png"],
                project_var_name + ".filehelper": ["*.js", "*.css"],
                project_var_name + ".helpgen": ["*.js"],
                project_var_name + ".sphinxext.releases": ["*.txt"],
                }

############
# functions
############


def is_local():
    file = os.path.abspath(__file__).replace("\\", "/").lower()
    if "/temp/" in file and "pip-" in file:
        return False
    if \
       "bdist_msi" in sys.argv or \
       "build27" in sys.argv or \
       "build_script" in sys.argv or \
       "build_sphinx" in sys.argv or \
       "build_ext" in sys.argv or \
       "bdist_wheel" in sys.argv or \
       "bdist_wininst" in sys.argv or \
       "clean_pyd" in sys.argv or \
       "clean_space" in sys.argv or \
       "copy27" in sys.argv or \
       "copy_dist" in sys.argv or \
       "local_pypi" in sys.argv or \
       "notebook" in sys.argv or \
       "publish" in sys.argv or \
       "publish_doc" in sys.argv or \
       "register" in sys.argv or \
       "unittests" in sys.argv or \
       "unittests_LONG" in sys.argv or \
       "unittests_SKIP" in sys.argv or \
       "unittests_GUI" in sys.argv or \
       "run27" in sys.argv or \
       "sdist" in sys.argv or \
       "setupdep" in sys.argv or \
       "test_local_pypi" in sys.argv or \
       "upload_docs" in sys.argv or \
       "setup_hook" in sys.argv or \
       "copy_sphinx" in sys.argv or \
       "write_version" in sys.argv:
        import_pyquickhelper()
        return True
    else:
        return False


def import_pyquickhelper():
    try:
        import pyquickhelper
    except ImportError:
        p = os.path.normpath(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "src")))
        sys.path.append(p)
        try:
            import pyquickhelper
        except ImportError as e:
            message = "module pyquickhelper is needed to build the documentation ({0}), not found in path {1} - current {2}".format(
                sys.executable,
                sys.path[-1],
                os.getcwd())
            raise ImportError(message) from e
    return pyquickhelper


def verbose():
    print("---------------------------------")
    print("package_dir =", package_dir)
    print("packages    =", packages)
    print("package_data=", package_data)
    print("current     =", os.path.abspath(os.getcwd()))
    print("---------------------------------")

##########
# version
##########


if is_local() and "--help" not in sys.argv and "--help-commands" not in sys.argv:
    def write_version():
        pyquickhelper = import_pyquickhelper()
        from pyquickhelper.pycode import write_version_for_setup
        return write_version_for_setup(__file__)

    if sys.version_info[0] != 2:
        write_version()

    versiontxt = os.path.join(os.path.dirname(__file__), "version.txt")
    if os.path.exists(versiontxt):
        with open(versiontxt, "r") as f:
            lines = f.readlines()
        subversion = "." + lines[0].strip("\r\n ")
        if subversion == ".0":
            raise Exception("Subversion is wrong: '{0}'.".format(subversion))
    else:
        raise FileNotFoundError(versiontxt)
else:
    # when the module is installed, no commit number is displayed
    subversion = ""

if "upload" in sys.argv and not subversion:
    # avoid uploading with a wrong subversion number
    try:
        import pyquickhelper
        pyq = True
    except ImportError:
        pyq = False
    raise Exception(
        "subversion is empty, cannot upload, is_local()={0}, pyquickhelper={1}".format(is_local(), pyq))

##############
# common part
##############

if os.path.exists(readme):
    if sys.version_info[0] == 2:
        from codecs import open
    with open(readme, "r", encoding='utf-8-sig') as f:
        long_description = f.read()
else:
    long_description = ""
if os.path.exists(history):
    if sys.version_info[0] == 2:
        from codecs import open
    with open(history, "r", encoding='utf-8-sig') as f:
        long_description += f.read()

if "--verbose" in sys.argv:
    verbose()

if is_local():
    pyquickhelper = import_pyquickhelper()
    logging_function = pyquickhelper.get_fLOG()
    logging_function(OutputPrint=True)
    from pyquickhelper.pycode import process_standard_options_for_setup
    r = process_standard_options_for_setup(
        sys.argv, __file__, project_var_name, port=8067,
        requirements=requirements, blog_list=pyquickhelper.__blog__,
        layout=["rst", "html"], additional_notebook_path=["jyquickhelper"],
        fLOG=logging_function, covtoken=("69193a28-dc79-4a24-98ed-aedf441a8249", "'_UT_36_std' in outfile"))

    if not r and not ({"bdist_msi", "sdist",
                       "bdist_wheel", "publish", "publish_doc", "register",
                       "upload_docs", "bdist_wininst", "build_ext"} & set(sys.argv)):
        raise Exception("unable to interpret command line: " + str(sys.argv))
else:
    r = False

if not r:
    if len(sys.argv) in (1, 2) and sys.argv[-1] in ("--help-commands",):
        pyquickhelper = import_pyquickhelper()
        from pyquickhelper.pycode import process_standard_options_for_setup_help
        process_standard_options_for_setup_help(sys.argv)

    setup(
        name=project_var_name,
        version='%s%s' % (sversion, subversion),
        author='Xavier Dupré',
        author_email='xavier.dupre@gmail.com',
        license="MIT",
        url="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html",
        download_url="https://github.com/sdpython/pyquickhelper",
        description=DESCRIPTION,
        long_description=long_description,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=packages,
        package_dir=package_dir,
        package_data=package_data,
        ext_modules=[],
        install_requires=[
            "autopep8",     # part of the minimal list
            "babel!=2.0",   # babel 2.0 has issue
            "coverage",
            "docformatter",
            "docutils",
            "entrypoints",
            "IPython>=5.0.0",
            "jupyter",
            "jupyter_client",
            "jupyter_core",
            "jupyter_sphinx",
            "jyquickhelper",
            "matplotlib",
            "metakernel",
            "multi_key_dict",
            "nbconvert>=4.2.0",
            "nbformat",
            "nbpresent",
            "nbsphinx",
            "notebook>=4.2.0",
            "numpy>=1.11.1",
            "pandas>=0.18.1",
            "pycodestyle>=2.0.0",
            "pydocstyle",
            "pyflakes",
            "semantic_version",
            "simplegeneric",
            "sphinx>=1.6",
            "sphinx-gallery",
            "sphinxcontrib-imagesvg",
            "sphinxcontrib-jsdemo",
            "sphinxjp.themes.revealjs",
            "tqdm",
            "unify",
        ],
        extras_require={
            'jenkinshelper': ['python-jenkins', 'pyyaml'],
        },
        entry_points={
            'console_scripts': [
                'encrypt = pyquickhelper.cli.encryption_cli:encrypt',
                'decrypt = pyquickhelper.cli.encryption_cli:decrypt',
                'encrypt_file = pyquickhelper.cli.encryption_file_cli:encrypt_file',
                'decrypt_file = pyquickhelper.cli.encryption_file_cli:decrypt_file',
                'pyq-sync = pyquickhelper.cli.pyq_sync_cli:pyq_sync',
            ]})
