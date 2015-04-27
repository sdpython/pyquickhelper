"""
@file
@brief  Helper for the setup

.. versionadded:: 1.1
"""

import os
import sys
from ..loghelper.pyrepo_helper import SourceRepository
from ..loghelper.flog import fLOG
from ..helpgen.sphinx_main import generate_help_sphinx
from .code_helper import remove_extra_spaces_folder
from .py3to2 import py3to2_convert_tree
from ..pycode.utils_tests import main_wrapper_tests
from ..helpgen import get_help_usage


def get_folder(file_or_folder):
    """
    returns the folder which contains ``setup.py``

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         folder
    """
    file_or_folder = os.path.abspath(file_or_folder)
    if os.path.isdir(file_or_folder):
        folder = file_or_folder
    else:
        folder = os.path.dirname(file_or_folder)
    return folder


def write_version_for_setup(file_or_folder):
    """
    extract the version number,
    the function writes the files ``version.txt`` in this folder

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         version number

    .. versionadded:: 1.1
    """
    src = SourceRepository(commandline=True)
    ffolder = get_folder(file_or_folder)
    version = src.version(ffolder)
    if version in ["0", 0, None]:
        raise Exception("issue with version {0}".format(version))

    # write version number
    if version is not None:
        with open(os.path.join(ffolder, "version.txt"), "w") as f:
            f.write(str(version) + "\n")

    return version


def clean_space_for_setup(file_or_folder):
    """
    .. index:: pep8

    does some cleaning within the module, apply pep8 rules

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         deleted files
    """
    ffolder = get_folder(file_or_folder)
    rem = remove_extra_spaces_folder(
        ffolder,
        extensions=[
            ".py",
            "rst",
            ".bat",
            ".sh"])
    return rem


def standard_help_for_setup(file_or_folder, project_var_name, module_name=None):
    """
    standard function to generate help assuming they follow the same design
    as *pyquickhelper*

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      project_var_name    display name of the module
    @param      module_name         module name, None if equal to *project_var_name* (``import <module_name>``)

    The function outputs some information through function @see fn fLOG.
    """
    if "--help" in sys.argv:
        print(get_help_usage())
    else:
        if module_name is None:
            module_name = project_var_name

        ffolder = get_folder(file_or_folder)
        source = os.path.join(ffolder, "_doc", "sphinxdoc", "source")

        if not os.path.exists(source):
            raise FileNotFoundError(
                "you must get the source from GitHub to build the documentation,\nfolder {0} "
                "should exist\n(file_or_folder={1})\n(ffolder={2})\n(cwd={3})".format(source, file_or_folder, ffolder, os.getcwd()))

        fLOG(OutputPrint=True)
        project_name = os.path.split(
            os.path.split(os.path.abspath(ffolder))[0])[-1]

        if sys.platform.startswith("win"):
            generate_help_sphinx(project_name, module_name=module_name,
                                 layout=["html", "pdf"],
                                 extra_ext=["doc"])
        else:
            # unable to test latex conversion due to adjustbox.sty missing
            # package
            generate_help_sphinx(project_name, nbformats=["ipynb", "html", "python", "rst"],
                                 module_name=project_var_name,
                                 extra_ext=["doc"])


def run_unittests_for_setup(file_or_folder):
    """
    run the unit tests and compute the coverage, stores
    the results in ``_doc/sphinxdoc/source/coverage``
    assuming the module follows the same design as *pyquickhelper*

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    """
    ffolder = get_folder(file_or_folder)
    funit = os.path.join(ffolder, "_unittests")
    if not os.path.exists(funit):
        raise FileNotFoundError(
            "you must get the source from GitHub to run the unittests,\nfolder {0} should exist".format(funit))

    run_unit = os.path.join(funit, "run_unittests.py")
    if not os.path.exists(run_unit):
        raise FileNotFoundError(
            "the folder {0} should contain run_unittests.py".format(funit))

    main_wrapper_tests(run_unit, add_coverage=True)


def copy27_for_setup(file_or_folder):
    """
    prepare a copy of the source for Python 2.7,
    assuming the module follows the same design as *pyquickhelper*

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    """
    if sys.version_info[0] < 3:
        raise Exception("Python needs to be Python3")

    root = get_folder(file_or_folder)
    root = os.path.normpath(root)
    dest = os.path.join(root, "dist_module27")
    py3to2_convert_tree(root, dest)


def process_standard_options_for_setup(argv, file_or_folder, project_var_name, module_name=None,
                                       unittest_modules=None,
                                       pattern_copy=".*[.]((ico)|(dll)|(rst)|(ipynb)|(png)|(txt)|(zip)|(gz))$"):
    """
    process the standard options the module pyquickhelper is
    able to process assuming the module which calls this function
    follows the same design as *pyquickhelper*, it will process the following
    options:
        * ``clean_space``: clean unnecessary spaces in the code
        * ``write_version``: write a file ``version.txt`` with the version number (needs an access to GitHub)
        * ``clean_pyd``: clean file ``*.pyd``
        * ``build_sphinx``: build the documentation
        * ``unittests``: run the unit tests
        * ``copy27``: create a modified copy of the module to run on Python 2.7

    @param      argv                = *sys.argv*
    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      project_var_name    display name of the module
    @param      module_name         module name, None if equal to *project_var_name* (``import <module_name>``)
    @param      unittest_modules    modules added for the unit tests, see @see fn py3to2_convert_tree
    @param      pattern_copy        see @see fn py3to2_convert_tree
    @return                         True (an option was processed) or False,
                                    the file ``setup.py`` should call function ``setup``
    """
    if "clean_space" in argv:
        rem = clean_space_for_setup(file_or_folder)
        print("number of impacted files", len(rem))
        return True
    elif "write_version" in argv:
        write_version_for_setup(file_or_folder)
        return True
    elif "clean_pyd" in sys.argv:
        clean_space_for_setup(file_or_folder)
        return True
    elif "build_sphinx" in sys.argv:
        standard_help_for_setup(
            file_or_folder, project_var_name, module_name=module_name)
        return True
    elif "unittests" in sys.argv:
        main_wrapper_tests(file_or_folder)
        return True
    elif "copy27" in sys.argv:
        if sys.version_info[0] < 3:
            raise Exception("Python needs to be Python3")
        root = os.path.abspath(os.path.dirname(file_or_folder))
        root = os.path.normpath(root)
        dest = os.path.join(root, "dist_module27")
        py3to2_convert_tree(
            root, dest, unittest_modules=unittest_modules, pattern_copy=pattern_copy)
        return True
    else:
        return False
