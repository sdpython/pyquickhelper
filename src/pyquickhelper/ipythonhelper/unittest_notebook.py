"""
@file
@brief Functions to test a notebook.
"""
import os
import shutil
import sys
from ..loghelper import noLOG
from .run_notebook import execute_notebook_list, execute_notebook_list_finalize_ut
from .run_notebook import get_additional_paths as pyq_get_additional_paths


def test_notebook_execution_coverage(filename, name, folder, this_module_name,
                                     valid=None, copy_files=None, modules=None,
                                     filter_name=None, fLOG=noLOG):
    """
    Runs and tests a specific list of notebooks.
    The function raises an exception if the execution fails.

    @param      filename            test filename (usually ``__file__``)
    @param      name                substring to look into notebook filenames
    @param      folder              where to look for notebooks
    @param      valid               skip cells if valid is False, None for all valid
    @param      copy_files          files to copy before running the notebooks.
    @param      modules             list of extra dependencies (not installed),
                                    example: ``['pyensae']``
    @param      this_module_name    the module name being tested (as a string)
    @param      filter_name         None or function
    @param      fLOG                logging function

    The function calls @see fn execute_notebook_list_finalize_ut which
    stores information about the notebooks execution. This will be later
    used to compute the coverage of notebooks.
    Modules :epkg:`pyquickhelper` and :epkg:`jyquickhelper` must be
    imported before calling this function.
    Example of a unit test calling this function:

    ::

        from pyquickhelper.loghelper import fLOG
        from pyquickhelper.ipythonhelper import test_notebook_execution_coverage
        from pyquickhelper.pycode import add_missing_development_version
        import src.mymodule


        class TestFunctionTestNotebook(unittest.TestCase):

            def setUp(self):
                add_missing_development_version(["jyquickhelper"], __file__, hide=True)

            def test_notebook_example_pyquickhelper(self):
                fLOG(
                    __file__,
                    self._testMethodName,
                    OutputPrint=__name__ == "__main__")

                folder = os.path.join(os.path.dirname(__file__), ".." , "..", "_doc", "notebooks")
                test_notebook_execution_coverage(__file__, "compare_python_distribution",
                                                 folder, 'mymodule', fLOG=fLOG)
    """
    # delayed import (otherwise, it has circular references)
    from ..pycode import get_temp_folder

    filename = os.path.abspath(filename)
    temp = get_temp_folder(filename, "temp_nb_{0}".format(name))
    doc = os.path.normpath(os.path.join(
        temp, "..", "..", "..", "_doc", "notebooks", folder))
    if not os.path.exists(doc):
        raise FileNotFoundError(doc)  # pragma: no cover
    keepnote = [os.path.join(doc, _) for _ in os.listdir(
        doc) if name in _ and ".ipynb" in _ and ".ipynb_checkpoints" not in _]
    if len(keepnote) == 0:
        raise AssertionError(  # pragma: no cover
            "No found notebook in '{0}'\n{1}".format(
                doc, "\n".join(os.listdir(doc))))

    if copy_files is not None:
        for name_ in copy_files:
            dest = os.path.join(temp, name_)
            dest_dir = os.path.dirname(dest)
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            src_file = os.path.join(doc, name_)
            fLOG("[a_test_notebook_runner] copy '{0}' to '{1}'.".format(
                src_file, dest_dir))
            shutil.copy(src_file, dest_dir)

    if 'pyquickhelper' in this_module_name:
        jyquickhelper = sys.modules['jyquickhelper']
        if "src." + this_module_name in sys.modules:
            thismodule = sys.modules["src." + this_module_name]
        else:
            thismodule = sys.modules[this_module_name]
        base = [jyquickhelper, thismodule]
    else:  # pragma: no cover
        pyquickhelper = sys.modules['pyquickhelper']
        jyquickhelper = sys.modules['jyquickhelper']
        if "src." + this_module_name in sys.modules:
            thismodule = sys.modules["src." + this_module_name]
        else:
            thismodule = sys.modules[this_module_name]
        base = [jyquickhelper, pyquickhelper, thismodule]

    if modules:
        base.extend(modules)
    add_path = pyq_get_additional_paths(base)
    if filter_name:
        keepnote = [_ for _ in keepnote if filter_name(_)]
    res = execute_notebook_list(temp, keepnote, additional_path=add_path,
                                valid=valid, fLOG=fLOG)
    execute_notebook_list_finalize_ut(res, fLOG=fLOG, dump=thismodule)
