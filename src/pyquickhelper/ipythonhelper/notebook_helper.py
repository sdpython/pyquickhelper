"""
@file
@brief Some automation helpers about notebooks
"""
import io
from IPython.nbformat import versions
from IPython.nbformat.reader import reads
from .notebook_runner import NotebookRunner
from ..loghelper.flog import noLOG
from IPython.nbformat.v4 import upgrade


def writes(nb, **kwargs):
    """Write a notebook to a string in a given format in the current nbformat version.

    This function always writes the notebook in the current nbformat version.

    Parameters
    ----------
    nb : NotebookNode
        The notebook to write.
    version : int
        The nbformat version to write.
        Used for downgrading notebooks.

    Returns
    -------
    s : unicode
        The notebook string.
    """
    return versions[nb.nbformat].writes_json(nb, **kwargs)


def upgrade_notebook(filename, encoding="utf8"):
    """
    converts a notebook from version 2 to 3

    @param      filename        filename
    @param      encoding        encoding
    @return                     modification?

    .. versionadded:: 1.0
    """
    with open(filename, "r", encoding=encoding) as payload:
        content = payload.read()

    nb = reads(content)

    if nb.nbformat >= 4:
        return False

    upgrade(nb, from_version=nb.nbformat)

    s = writes(nb)
    if isinstance(s, bytes):
        s = s.decode('utf8')

    if s == content:
        return False
    else:
        with open(filename, "w", encoding=encoding) as f:
            f.write(s)
        return True


def run_notebook(filename,
                 profile_dir=None,
                 working_dir=None,
                 skip_exceptions=False,
                 outfilename=None,
                 encoding="utf8",
                 additional_path=None,
                 valid=None,
                 clean_function=None,
                 fLOG=noLOG):
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
    @param      fLOG            logging function
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
        nb = reads(payload.read())

        out = io.StringIO()

        def flogging(*l, **p):
            if len(l) > 0:
                out.write(" ".join(l))
            if len(p) > 0:
                out.write(str(p))
            out.write("\n")
            fLOG(*l, **p)

        nb_runner = NotebookRunner(
            nb, profile_dir, working_dir, fLOG=flogging, comment=filename)
        nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
                               valid=valid, clean_function=clean_function)

        if outfilename is not None:
            with open(outfilename, 'w', encoding=encoding) as f:
                s = writes(nb_runner.nb)
                if isinstance(s, bytes):
                    s = s.decode('utf8')
                f.write(s)

        nb_runner.shutdown_kernel()
        return out.getvalue()
