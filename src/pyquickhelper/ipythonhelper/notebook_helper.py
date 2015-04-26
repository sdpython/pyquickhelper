"""
@file
@brief Some automation helpers about notebooks
"""
import io
import os
import sys
from IPython.nbformat import versions
from IPython.nbformat.reader import reads
from .notebook_runner import NotebookRunner
from ..loghelper.flog import noLOG
from IPython.nbformat.v4 import upgrade
from .notebook_exception import NotebookException

if sys.version_info[0] == 2:
    from codecs import open


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
    try:
        return versions[nb.nbformat].writes_json(nb, **kwargs)
    except AttributeError as e:
        raise NotebookException(
            "probably wrong error: {0}".format(nb.nbformat)) from e


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
                 code_init=None,
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
    @param      code_init       code to run before the execution of the notebook as if it was a cell
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

    .. versionchanged:: 1.1
        The function adds the local variable ``theNotebook`` with
        the absolute file name of the notebook.
        Parameter *code_init* was added.
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
            nb, profile_dir, working_dir, fLOG=flogging, comment=filename,
            theNotebook=os.path.abspath(filename),
            code_init=code_init)
        nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
                               valid=valid, clean_function=clean_function)

        if outfilename is not None:
            with open(outfilename, 'w', encoding=encoding) as f:
                try:
                    s = writes(nb_runner.nb)
                except NotebookException as e:
                    raise NotebookException(
                        "issue with notebook: " + filename) from e
                if isinstance(s, bytes):
                    s = s.decode('utf8')
                f.write(s)

        nb_runner.shutdown_kernel()
        return out.getvalue()


def set_notebook_name_theNotebook():
    """
    This function must be called from the notebook
    you want to know the name. It relies on
    a javascript piece of code. It populates
    the variable ``theNotebook`` with the notebook name.

    This solution was found at
    `How to I get the current IPython Notebook name <http://stackoverflow.com/questions/12544056/how-to-i-get-the-current-ipython-notebook-name>`_.

    The function can be called in a cell.
    The variable ``theNotebook`` will be available in the next cells.

    .. versionadded:: 1.1
    """
    code = """var kernel = IPython.notebook.kernel;
              var body = document.body, attribs = body.attributes;
              var command = "theNotebook = " + "'"+attribs['data-notebook-name'].value+"'";
              kernel.execute(command);""".replace("              ", "")

    def get_name():
        from IPython.core.display import Javascript, display
        display(Javascript(code))
    return get_name()


def execute_notebook_list(folder,
                          notebooks,
                          clean_function=None,
                          valid=None,
                          fLOG=noLOG,
                          addpath=None,
                          deepfLOG=noLOG):
    """
    execute a list of notebooks

    @param      folder              folder (where to execute the notebook, current folder for the notebook)
    @param      notebooks           list of notebooks to execute (or a list of tuple(notebook, code which initializes the notebook))
    @param      clean_function      function which transform the code before running it
    @param      valid               function which tells if a cell should be executed based on its code
    @param      fLOG                logging function
    @param      deepfLOG            logging function used to run the notebook
    @param      addpath             path to add to *sys.path* before running the notebook
    @return                         dictionary { notebook_file: (isSuccess, outout) }

    The signature of function ``valid_cell`` is::

        def valid_cell(cell) : return True or False

    The signature of function ``clean_function`` is::

        def clean_function(cell) : return new_cell_content

    .. versionadded:: 1.1

    """
    if addpath is None:
        addpath = []

    results = {}
    for i, note in enumerate(notebooks):
        if isinstance(note, tuple):
            note, code_init = note
        else:
            code_init = None
        if filter(i, note):
            fLOG("******", i, os.path.split(note)[-1])
            outfile = os.path.join(folder, "out_" + os.path.split(note)[-1])
            try:
                out = run_notebook(note,
                                   working_dir=folder,
                                   outfilename=outfile,
                                   additional_path=addpath,
                                   valid=valid,
                                   clean_function=clean_function,
                                   fLOG=deepfLOG,
                                   code_init=code_init
                                   )
                if not os.path.exists(outfile):
                    raise FileNotFoundError(outfile)
                results[note] = (True, out)
            except Exception as e:
                results[note] = (False, e)
    return results
