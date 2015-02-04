"""
@file
@brief Some automation helpers about notebooks
"""
import os, logging, io
from IPython.nbformat.current import read, write
from .notebook_runner import NotebookRunner, NotebookError

def run_notebook(filename,
                profile_dir     = None,
                working_dir     = None,
                skip_exceptions = False,
                outfilename     = None,
                encoding        = "utf8",
                additional_path = None,
                valid           = None,
                clean_function  = None):
    """
    run a notebook end to end, it uses module `runipy <https://github.com/paulgb/runipy/>`_

    @param      filename        notebook filename
    @param      profile_dir     profile directory
    @param      working_dir     working directory
    @param      skip_exceptions skip exceptions
    @param      outfilename     if not None, saves the output in this notebook
    @param      encoding        encoding for the notebooks
    @param      additional_path additional paths for import
    @param      valid           if not None, valid is a function which returns wether or not the cell should be executed or not
    @param      clean_function  function which cleans a cell's code before executing it (None for None)
    @return                     output

    @warning The function calls `basicConfig <https://docs.python.org/3.4/library/logging.html#logging.basicConfig>`_.

    @example(Run a notebook end to end)
    @code
    from pyquickhelper.ipythonhelper.notebook_helper import run_notebook
    run_notebook("source.ipynb", working_dir="temp",
                outfilename="modified.ipynb",
                additional_path = [ "c:/temp/mymodule/src" ] )
    @endcode
    @endexample

    .. versionadded:: 1.0
    """
    with open(filename, "r", encoding=encoding) as payload:
        nb = read(payload, 'json')

        out = io.StringIO()
        def flogging(*l, **p):
            if len(l) > 0 : out.write( " ".join(l) )
            if len(p) > 0 : out.write( str(p) )
            out.write("\n")

        nb_runner = NotebookRunner(nb, profile_dir, working_dir, fLOG=flogging)
        nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
                valid = valid, clean_function=clean_function)

        if outfilename is not None:
            with open(outfilename, 'w', encoding=encoding) as f:
                write(nb_runner.nb, f, 'json')

        nb_runner.shutdown_kernel()
        return out.getvalue()