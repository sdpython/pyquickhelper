# -*- coding: utf-8 -*-
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
package_data = {project_var_name + ".funcwin": ["*.ico"],
                project_var_name + ".sphinxext": ["*.png"],
                project_var_name + ".filehelper": ["*.js", "*.css"],
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

    if os.path.exists("version.txt"):
        with open("version.txt", "r") as f:
            lines = f.readlines()
        subversion = "." + lines[0].strip("\r\n ")
        if subversion == ".0":
            raise Exception("subversion is wrong: " + subversion)
    else:
        raise FileNotFoundError("version.txt")
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
        layout=["html"], additional_notebook_path=["jyquickhelper"],
        fLOG=logging_function, covtoken=("69193a28-dc79-4a24-98ed-aedf441a8249", "'_UT_35_std' in outfile"))

    if not r and not ({"bdist_msi", "sdist",
                       "bdist_wheel", "publish", "publish_doc", "register",
                       "upload_docs", "bdist_wininst"} & set(sys.argv)):
        raise Exception("unable to interpret command line: " + str(sys.argv))

    if "build_script" in sys.argv and sys.platform.startswith("win"):
        norm = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")))
        folds = [os.path.join(norm, _) for _ in os.listdir(norm)]
        folds = [_ for _ in folds if os.path.exists(
            os.path.join(_, "build_script.bat"))]
        with open("build_sphinx_all.bat", "w") as f:
            for fold in folds:
                f.write("cd {}\n".format(os.path.abspath(fold)))
                f.write("call build_script.bat\n")
                f.write("call auto_setup_build_sphinx.bat\n")
                f.write("call auto_cmd_copy_sphinx.bat\n")
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
            "docutils",
            "entrypoints",
            "numpy>=1.11.1",
            "IPython>=5.0.0",
            "ipykernel",
            "ipython_genutils",
            "ipywidgets",
            "jupyter",
            "jupyter_client",
            "jupyter_console",
            "jupyter_core",
            "jyquickhelper",
            "matplotlib",
            "metakernel",
            "multi_key_dict",
            "nbconvert>=4.2.0",
            "nbformat",
            "nbpresent",
            "notebook>=4.2.0",
            "path.py",
            "pickleshare",
            "pandas>=0.18.1",
            "pycodestyle>=2.0.0",
            "pyflakes",
            "python-dateutil",
            "requests",
            "simplegeneric",
            "sphinx>=1.5",
            "sphinxcontrib-imagesvg",
            "sphinxcontrib-jsdemo",
            "sphinxjp.themes.revealjs",
            "traitlets",
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
            ]})
