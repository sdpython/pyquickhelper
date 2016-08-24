"""
@file
@brief Some automation helpers about notebooks
"""
from .notebook_runner import NotebookRunner
from .notebook_exception import NotebookException
from ..filehelper import explore_folder_iterfile, remove_folder

import os
import sys
import json
from nbformat import versions
from nbformat.reader import reads
from nbformat.v4 import upgrade
from ..filehelper import read_content_ufs


if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


if sys.version_info[0] == 2:
    from codecs import open


def writes(nb, **kwargs):
    """
    Write a notebook to a string in a given format in the current nbformat version.

    This function always writes the notebook in the current nbformat version.

    Parameters
    ++++++++++

    nb : NotebookNode
        The notebook to write.
    version : int
        The nbformat version to write.
        Used for downgrading notebooks.

    Returns
    +++++++

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


def find_notebook_kernel(kernel_spec_manager=None):
    """
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
        from jupyter_client.kernelspec import KernelSpecManager
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
        from jupyter_client.kernelspec import KernelSpecManager
        kernel_spec_manager = KernelSpecManager()
    return kernel_spec_manager.get_kernel_spec(kernel_name)


def install_notebook_extension(path=None, overwrite=False, symlink=False,
                               user=False, prefix=None, nbextensions_dir=None,
                               destination=None, verbose=1):
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
    from notebook.nbextensions import install_nbextension
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
    from jupyter_client.kernelspec import KernelSpecManager
    return KernelSpecManager().data_dir


def get_jupyter_extension_dir(user=False, prefix=None,
                              nbextensions_dir=None):
    """
    Parameters
    ++++++++++

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
    ++++++

    path: path to installed extensions (by the user)


    .. versionadded:: 1.3
    """
    from notebook.nbextensions import _get_nbextension_dir
    return _get_nbextension_dir(nbextensions_dir=nbextensions_dir, user=user, prefix=prefix)


def get_installed_notebook_extension(user=False, prefix=None,
                                     nbextensions_dir=None):
    """
    Parameters
    ++++++++++

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
    ++++++

    list: list of installed notebook extension (by the user)

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
    ++++++++++

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
    +++++++

    path: The path where the kernelspec was installed.

    A kernel is defined by the following fields:

    ::

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

    For R, it looks like

    ::

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
    from ipykernel.kernelspec import install as install_k
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


def remove_execution_number(infile, outfile=None, encoding="utf-8", indent=2):
    """
    remove execution number from a notebook

    @param      infile      filename of the notebook
    @param      outfile     None ot save the file
    @param      encoding    encoding
    @param      indent      indentation
    @return                 modified string

    .. todoext::
        :title: remove execution number from notebook facilitate git versionning
        :tag: enhancement
        :issue: 18
        :cost: 1
        :hidden:

        Remove execution number from the notebook
        to avoid commiting changes only about those numbers
    """

    def fixup(adict, k, v):
        for key in adict.keys():
            if key == k:
                adict[key] = v
            elif isinstance(adict[key], dict):
                fixup(adict[key], k, v)
            elif isinstance(adict[key], list):
                for el in adict[key]:
                    if isinstance(el, dict):
                        fixup(el, k, v)

    content = read_content_ufs(infile)
    js = json.loads(content, encoding=encoding)
    fixup(js, "execution_count", None)
    st = StringIO()
    json.dump(js, st, indent=indent, sort_keys=True)
    res = st.getvalue()
    if outfile is not None:
        with open(outfile, "w", encoding=encoding) as f:
            f.write(res)
    return res
