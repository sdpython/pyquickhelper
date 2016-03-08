"""
@file
@brief Some automation helpers about notebooks
"""
from .notebook_runner import NotebookRunner
from ..loghelper.flog import noLOG
from .notebook_exception import NotebookException
from ..filehelper import explore_folder_iterfile, remove_folder

import os
import sys
import time
import json

try:
    from nbformat import versions
    from nbformat.reader import reads
    from nbformat.v4 import upgrade
    from jupyter_client.kernelspec import KernelSpecManager
    from notebook.nbextensions import install_nbextension, _get_nbext_dir
    from ipykernel.kernelspec import install as install_k
except ImportError:
    from IPython.nbformat import versions
    from IPython.nbformat.reader import reads
    from IPython.nbformat.v4 import upgrade
    from IPython.kernel.kernelspec import KernelSpecManager
    from IPython.html.nbextensions import install_nbextension, _get_nbext_dir
    try:
        from IPython.kernel.kernelspec import install as install_k
    except ImportError:
        import IPython
        raise ImportError("upgrade IPython, this one is not recent enough: {0}".format(
            IPython.__version__))


if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


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

    if not hasattr(nb, "format") or nb.nbformat >= 4:
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
                 fLOG=noLOG,
                 kernel_name="python",
                 log_level="30",
                 extended_args=None):
    """
    run a notebook end to end, it uses module `runipy <https://github.com/paulgb/runipy/>`_

    @param      filename            notebook filename
    @param      profile_dir         profile directory
    @param      working_dir         working directory
    @param      skip_exceptions     skip exceptions
    @param      outfilename         if not None, saves the output in this notebook
    @param      encoding            encoding for the notebooks
    @param      additional_path     additional paths for import
    @param      valid               if not None, valid is a function which returns wether or not the cell should be executed or not
    @param      clean_function      function which cleans a cell's code before executing it (None for None)
    @param      code_init           code to run before the execution of the notebook as if it was a cell
    @param      fLOG                logging function
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @return                         tuple (statistics, output)

    @warning The function calls `basicConfig <https://docs.python.org/3.4/library/logging.html#logging.basicConfig>`_.

    @example(Run a notebook end to end)
    @code
    from pyquickhelper.ipythonhelper import run_notebook
    run_notebook("source.ipynb", working_dir="temp",
                outfilename="modified.ipynb",
                additional_path = [ "c:/temp/mymodule/src" ] )
    @endcode
    @endexample

    The function adds the local variable ``theNotebook`` with
    the absolute file name of the notebook.

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.
    """
    with open(filename, "r", encoding=encoding) as payload:
        nb = reads(payload.read())

        out = StringIO()

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
            code_init=code_init, log_level=log_level,
            extended_args=extended_args, kernel_name=kernel_name)
        stat = nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
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
        return stat, out.getvalue()


def read_nb(filename, profile_dir=None, encoding="utf8", kernel=True):
    """
    reads a notebook and return a @see cl NotebookRunner object

    @param      filename        notebook filename (or stream)
    @param      profile_dir     profile directory
    @param      encoding        encoding for the notebooks
    @param      kernel          *kernel* is True by default, the notebook can be run, if False,
                                the notebook can be read but not run
    @return                     @see cl NotebookRunner

    .. versionchanged:: 1.3
        Parameter *kernel* was added.
    """
    if isinstance(filename, str  # unicode#
                  ):
        with open(filename, "r", encoding=encoding) as payload:
            nb = reads(payload.read())

            nb_runner = NotebookRunner(
                nb, profile_dir, theNotebook=os.path.abspath(filename),
                kernel=kernel)
            return nb_runner
    else:
        nb = reads(filename.read())
        nb_runner = NotebookRunner(nb, profile_dir, kernel=kernel)
        return nb_runner


def execute_notebook_list(folder,
                          notebooks,
                          clean_function=None,
                          valid=None,
                          fLOG=noLOG,
                          additional_path=None,
                          deepfLOG=noLOG,
                          kernel_name="python",
                          log_level="30",
                          extended_args=None):
    """
    execute a list of notebooks

    @param      folder              folder (where to execute the notebook, current folder for the notebook)
    @param      notebooks           list of notebooks to execute (or a list of tuple(notebook, code which initializes the notebook))
    @param      clean_function      function which transform the code before running it
    @param      valid               function which tells if a cell should be executed based on its code
    @param      fLOG                logging function
    @param      deepfLOG            logging function used to run the notebook
    @param      additional_path     path to add to *sys.path* before running the notebook
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @return                         dictionary { notebook_file: (isSuccess, statistics, outout) }

    If *isSucess* is False, *statistics* contains the execution time, *output* is the exception
    raised during the execution.

    The signature of function ``valid_cell`` is::

        def valid_cell(cell) : return True or False

    The signature of function ``clean_function`` is::

        def clean_function(cell) : return new_cell_content

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.
    """
    if additional_path is None:
        additional_path = []

    results = {}
    for i, note in enumerate(notebooks):
        if isinstance(note, tuple):
            note, code_init = note
        else:
            code_init = None
        if filter(i, note):
            fLOG("******", i, os.path.split(note)[-1])
            outfile = os.path.join(folder, "out_" + os.path.split(note)[-1])
            cl = time.clock()
            try:
                stat, out = run_notebook(note,
                                         working_dir=folder,
                                         outfilename=outfile,
                                         additional_path=additional_path,
                                         valid=valid,
                                         clean_function=clean_function,
                                         fLOG=deepfLOG,
                                         code_init=code_init,
                                         kernel_name=kernel_name,
                                         log_level=log_level,
                                         extended_args=extended_args
                                         )
                if not os.path.exists(outfile):
                    raise FileNotFoundError(outfile)
                results[note] = (True, stat, out)
            except Exception as e:
                etime = time.clock() - cl
                results[note] = (False, dict(time=etime), e)
    return results


def find_notebook_kernel(kernel_spec_manager=None):
    """
    .. index:: notebook, kernel

    return a dict mapping kernel names to resource directories

    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/en/latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @return                             dict

    The list of installed kernels is described at
    `Making kernel for Jupyter <http://jupyter-client.readthedocs.org/en/latest/kernels.html#kernelspecs>`_.
    The function only works with Jupyter>=4.0.

    .. versionadded:: 1.3
    """
    if kernel_spec_manager is None:
        kernel_spec_manager = KernelSpecManager()
    return kernel_spec_manager.find_kernel_specs()


def get_notebook_kernel(kernel_name, kernel_spec_manager=None):
    """
    return a `KernelSpec <https://ipython.org/ipython-doc/dev/api/generated/IPython.kernel.kernelspec.html>`_

    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/en/latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @param      kernel_name             kernel name
    @return                             KernelSpec

    The function only works with Jupyter>=4.0.

    .. versionadded:: 1.3
    """
    if kernel_spec_manager is None:
        kernel_spec_manager = KernelSpecManager()
    return kernel_spec_manager.get_kernel_spec(kernel_name)


def install_notebook_extension(path=None,
                               overwrite=False,
                               symlink=False,
                               user=False,
                               prefix=None,
                               nbextensions_dir=None,
                               destination=None,
                               verbose=1):
    """
    install notebook extensions,
    see `install_nbextension <https://ipython.org/ipython-doc/dev/api/generated/IPython.html.nbextensions.html#IPython.html.nbextensions.install_nbextension>`_
    for documentation

    @param      path    if None, use default value
    @return             standard output

    Default value is
    `https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip <https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip>`_.

    .. versionadded:: 1.3
    """
    if path is None:
        path = "https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip"

    cout = sys.stdout
    cerr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    install_nbextension(path=path, overwrite=overwrite, symlink=symlink,
                        user=user, prefix=prefix, nbextensions_dir=nbextensions_dir,
                        destination=destination, verbose=verbose)

    out = sys.stdout.getvalue()
    err = sys.stderr.getvalue()
    sys.stdout = cout
    sys.stderr = cerr
    if len(err) != 0:
        raise NotebookException(
            "unable to install exception from: {0}\nOUT:\n{1}\nERR:\n{2}".format(path, out, err))
    return out


def get_jupyter_datadir():
    """
    return the data directory for the notebook

    @return     path

    .. versionadded:: 1.3
    """
    return KernelSpecManager().data_dir


def get_jupyter_extension_dir(user=False,
                              prefix=None,
                              nbextensions_dir=None):
    """
    Parameters
    ----------

    files : list(paths)
        a list of relative paths within nbextensions.
    user : bool [default: False]
        Whether to check the user's .ipython/nbextensions directory.
        Otherwise check a system-wide install (e.g. /usr/local/share/jupyter/nbextensions).
    prefix : str [optional]
        Specify install prefix, if it should differ from default (e.g. /usr/local).
        Will check prefix/share/jupyter/nbextensions
    nbextensions_dir : str [optional]
        Specify absolute path of nbextensions directory explicitly.

    Return
    ------

        path to installed extensions (by the user)


    .. versionadded:: 1.3
    """
    return _get_nbext_dir(nbextensions_dir=nbextensions_dir, user=user, prefix=prefix)


def get_installed_notebook_extension(user=False,
                                     prefix=None,
                                     nbextensions_dir=None):
    """
    Parameters
    ----------

    files : list(paths)
        a list of relative paths within nbextensions.
    user : bool [default: False]
        Whether to check the user's .ipython/nbextensions directory.
        Otherwise check a system-wide install (e.g. /usr/local/share/jupyter/nbextensions).
    prefix : str [optional]
        Specify install prefix, if it should differ from default (e.g. /usr/local).
        Will check prefix/share/jupyter/nbextensions
    nbextensions_dir : str [optional]
        Specify absolute path of nbextensions directory explicitly.

    Return
    ------

        list of installed notebook extension (by the user)

    You can install extensions with function @see fn install_notebook_extension.

    .. versionadded:: 1.3
    """
    path = get_jupyter_extension_dir(
        user=user, prefix=prefix, nbextensions_dir=nbextensions_dir)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    res = []
    for file in explore_folder_iterfile(path):
        rel = os.path.relpath(file, path)
        spl = os.path.split(rel)
        name = spl[-1]
        if name == "main.js":
            fold = "/".join(spl[:-1]).replace("\\", "/") + "/main"
            res.append(fold)
    return res


def install_jupyter_kernel(exe=sys.executable, kernel_spec_manager=None, user=False, kernel_name=None, prefix=None):
    """
    Install a kernel based on executable (this python by default)

    Parameters
    ----------
    exe: Python executable
        current one by default
    kernel_spec_manager: KernelSpecManager [optional]
        A KernelSpecManager to use for installation.
        If none provided, a default instance will be created.
    user: bool [default: False]
        Whether to do a user-only install, or system-wide.
    kernel_name: str, optional
        Specify a name for the kernelspec.
        This is needed for having multiple IPython kernels for different environments.
    prefix: str, optional
        Specify an install prefix for the kernelspec.
        This is needed to install into a non-default location, such as a conda/virtual-env.

    Returns
    -------

    The path where the kernelspec was installed.

    A kernel is defined by the following fields::

        {
            "display_name": "Python 3 (ENSAE)",
            "language": "python",
            "argv": [ "c:\\\\PythonENSAE\\\\python\\\\python.exe",
                      "-m",
                      "IPython.kernel",
                      "-f",
                      "{connection_file}"
                    ]
         }

    For R, it looks like::

        {
            "display_name": "R (ENSAE)",
            "language": "R",
            "argv": [ "c:\\\\PythonENSAE\\\\tools\\\\R\\\\bin\\\\x64\\\\R.exe",
                      "--quiet",
                      "-e",
                      "IRkernel::main()",
                      "--args",
                      "{connection_file}"
                    ]
        }

    .. versionadded:: 1.3
    """
    exe = exe.replace("pythonw.exe", "python.exe")
    dest = install_k(kernel_spec_manager=kernel_spec_manager,
                     user=user, kernel_name=kernel_name, prefix=prefix)
    kernel_file = os.path.join(dest, "kernel.json")
    kernel = dict(display_name=kernel_name,
                  language="python",
                  argv=[exe, "-m", "IPython.kernel", "-f", "{connection_file}"])

    s = json.dumps(kernel)
    with open(kernel_file, "w") as f:
        f.write(s)

    return dest


def install_python_kernel_for_unittest(suffix=None):
    """
    install a kernel based on this python (sys.executable) for unit test purposes

    @param      suffix      suffix to add to the kernel name
    @return                 kernel name

    .. versionadded:: 1.3
    """
    exe = os.path.split(sys.executable)[0].replace("pythonw", "python")
    exe = exe.replace("\\", "/").replace("/",
                                         "_").replace(".", "_").replace(":", "")
    kern = "ut_" + exe + "_" + str(sys.version_info[0])
    if suffix is not None:
        kern += "_" + suffix
    kern = kern.lower()
    install_jupyter_kernel(kernel_name=kern)
    return kern


def remove_kernel(kernel_name, kernel_spec_manager=None):
    """
    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/en/latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @param      kernel_name             kernel name

    The function only works with Jupyter>=4.0.

    .. versionadded:: 1.3
    """
    kernels = find_notebook_kernel(kernel_spec_manager=kernel_spec_manager)
    if kernel_name in kernels:
        fold = kernels[kernel_name]
        if not os.path.exists(fold):
            raise FileNotFoundError("unable to remove folder " + fold)
        remove_folder(fold)
    else:
        raise NotebookException("unable to find kernel {0} in {1}".format(
            kernel_name, ", ".join(kernels.keys())))
