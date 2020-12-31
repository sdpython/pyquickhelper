"""
@file
@brief Some automation helpers about notebooks
"""
import os
import sys
import json
import warnings
from io import StringIO
from nbformat import versions
from nbformat.reader import reads, NotJSONError
from nbformat.v4 import upgrade
from ..filehelper import read_content_ufs
from ..loghelper import noLOG
from ..filehelper import explore_folder_iterfile, remove_folder
from .notebook_runner import NotebookRunner
from .notebook_exception import NotebookException


with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=ImportWarning)
    try:
        from ipykernel.kernelspec import install as install_k
        raisewarn = False
    except ImportError:  # pragma: no cover
        raisewarn = True
if raisewarn:  # pragma: no cover
    warnings.warn("ipykernel is not installed. pyquickhelper cannot execute a notebook.",
                  category=ImportWarning)


def writes(nb, **kwargs):
    """
    Write a notebook to a string in a given format in the current nbformat version.

    This function always writes the notebook in the current nbformat version.

    Parameters
    ++++++++++

    nb : NotebookNode
        The notebook to write.
    kwargs :
        Among these parameters, *version* (int) which is
        The nbformat version to write.
        Used for downgrading notebooks.

    Returns
    +++++++

    s : unicode
        The notebook string.
    """
    try:
        return versions[nb.nbformat].writes_json(nb, **kwargs)
    except AttributeError as e:  # pragma: no cover
        raise NotebookException(
            "probably wrong error: {0}".format(nb.nbformat)) from e


def upgrade_notebook(filename, encoding="utf-8"):
    """
    Converts a notebook from version 2 to latest.

    @param      filename        filename
    @param      encoding        encoding
    @return                     modification?
    """
    with open(filename, "r", encoding=encoding) as payload:
        content = payload.read()

    try:
        nb = reads(content)
    except NotJSONError as e:  # pragma: no cover
        if len(content) > 10:
            lc = list(content[:10])
        else:
            lc = list(content)
        raise ValueError(
            "Unable to read content type '{0}' in '{2}' ---- {1}".format(type(content), lc, filename)) from e

    if not hasattr(nb, "nbformat") or nb.nbformat >= 4:
        return False

    try:
        upgrade(nb, from_version=nb.nbformat)
    except ValueError as e:  # pragma: no cover
        raise ValueError("Unable to convert '{0}'.".format(filename)) from e

    s = writes(nb)
    if isinstance(s, bytes):
        s = s.decode('utf8')

    if s == content:
        return False
    with open(filename, "w", encoding=encoding) as f:
        f.write(s)
    return True


def read_nb(filename, profile_dir=None, encoding="utf8", working_dir=None,
            comment="", fLOG=noLOG, code_init=None,
            kernel_name="python", log_level="30", extended_args=None,
            kernel=False, replacements=None):
    """
    Reads a notebook and return a @see cl NotebookRunner object.

    @param      filename        notebook filename (or stream)
    @param      profile_dir     profile directory
    @param      encoding        encoding for the notebooks
    @param      working_dir     working directory
    @param      comment         additional information added to error message
    @param      code_init       to initialize the notebook with a python code as if it was a cell
    @param      fLOG            logging function
    @param      log_level       Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      kernel_name     kernel name, it can be None
    @param      extended_args   others arguments to pass to the command line
                                (`--KernelManager.autorestar=True` for example),
                                see :ref:`l-ipython_notebook_args` for a full list
    @param      kernel          *kernel* is True by default, the notebook can be run, if False,
                                the notebook can be read but not run
    @param      replacements    replacements to make in every cell before running it,
                                dictionary ``{ string: string }``
    @return                     @see cl NotebookRunner
    """
    if isinstance(filename, str):
        with open(filename, "r", encoding=encoding) as payload:
            nb = reads(payload.read())

        nb_runner = NotebookRunner(
            nb, profile_dir=profile_dir, theNotebook=os.path.abspath(filename),
            kernel=kernel, working_dir=working_dir,
            comment=comment, fLOG=fLOG, code_init=code_init,
            kernel_name="python", log_level="30", extended_args=None,
            filename=filename, replacements=replacements)
        return nb_runner
    else:
        nb = reads(filename.read())
        nb_runner = NotebookRunner(nb, kernel=kernel,
                                   profile_dir=profile_dir, working_dir=working_dir,
                                   comment=comment, fLOG=fLOG, code_init=code_init,
                                   kernel_name="python", log_level="30", extended_args=None,
                                   filename=filename, replacements=replacements)
        return nb_runner


def read_nb_json(js, profile_dir=None, encoding="utf8",
                 working_dir=None, comment="", fLOG=noLOG, code_init=None,
                 kernel_name="python", log_level="30", extended_args=None,
                 kernel=False, replacements=None):
    """
    Reads a notebook from a :epkg:`JSON` stream or string.

    @param      js              string or stream
    @param      profile_dir     profile directory
    @param      encoding        encoding for the notebooks
    @param      working_dir     working directory
    @param      comment         additional information added to error message
    @param      code_init       to initialize the notebook with a python code as if it was a cell
    @param      fLOG            logging function
    @param      log_level       Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      kernel_name     kernel name, it can be None
    @param      extended_args   others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                see :ref:`l-ipython_notebook_args` for a full list
    @param      kernel          *kernel* is True by default, the notebook can be run, if False,
                                the notebook can be read but not run
    @param      replacements    replacements to make in every cell before running it,
                                dictionary ``{ string: string }``
    @return                     instance of @see cl NotebookRunner
    """
    if isinstance(js, str):
        st = StringIO(js)
    else:
        st = js
    return read_nb(st, encoding=encoding, kernel=kernel,
                   profile_dir=profile_dir, working_dir=working_dir,
                   comment=comment, fLOG=fLOG, code_init=code_init,
                   kernel_name="python", log_level="30", extended_args=None,
                   replacements=replacements)


def find_notebook_kernel(kernel_spec_manager=None):
    """
    Returns a dict mapping kernel names to resource directories.

    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/en/
                                        latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @return                             dict

    The list of installed kernels is described at
    `Making kernel for Jupyter <http://jupyter-client.readthedocs.org/en/latest/kernels.html#kernelspecs>`_.
    The function only works with *Jupyter>=4.0*.
    """
    if kernel_spec_manager is None:
        from jupyter_client.kernelspec import KernelSpecManager
        kernel_spec_manager = KernelSpecManager()
    return kernel_spec_manager.find_kernel_specs()


def get_notebook_kernel(kernel_name, kernel_spec_manager=None):
    """
    Returns a `KernelSpec <https://ipython.org/ipython-doc/dev/api/
    generated/IPython.kernel.kernelspec.html>`_.

    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/en/
                                        latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @param      kernel_name             kernel name
    @return                             KernelSpec

    The function only works with *Jupyter>=4.0*.
    """
    if kernel_spec_manager is None:
        from jupyter_client.kernelspec import KernelSpecManager
        kernel_spec_manager = KernelSpecManager()
    return kernel_spec_manager.get_kernel_spec(kernel_name)


def install_notebook_extension(path=None, overwrite=False, symlink=False,
                               user=False, prefix=None, nbextensions_dir=None,
                               destination=None):
    """
    Installs notebook extensions,
    see `install_nbextension <https://ipython.org/ipython-doc/
    dev/api/generated/IPython.html.nbextensions.html
    #IPython.html.nbextensions.install_nbextension>`_
    for documentation.

    @param      path                if None, use default value
    @param      overwrite           overwrite the extension
    @param      symlink             see the original function
    @param      user                user
    @param      prefix              see the original function
    @param      nbextensions_dir    see the original function
    @param      destination         see the original function
    @return                         standard output

    Default value is
    `https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip
    <https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip>`_.
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
                        destination=destination)

    out = sys.stdout.getvalue()
    err = sys.stderr.getvalue()
    sys.stdout = cout
    sys.stderr = cerr
    if len(err) != 0:
        raise NotebookException(
            "unable to install exception from: {0}\nOUT:\n{1}\n[nberror]\n{2}".format(path, out, err))
    return out


def get_jupyter_datadir():
    """
    Returns the data directory for the notebook.

    @return     path
    """
    from jupyter_client.kernelspec import KernelSpecManager
    return KernelSpecManager().data_dir


def get_jupyter_extension_dir(user=False, prefix=None,
                              nbextensions_dir=None):
    """
    Parameters
    ++++++++++

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
    """
    from notebook.nbextensions import _get_nbextension_dir
    return _get_nbextension_dir(nbextensions_dir=nbextensions_dir, user=user, prefix=prefix)


def get_installed_notebook_extension(user=False, prefix=None,
                                     nbextensions_dir=None):
    """
    Retuns installed extensions.

    :param user: bool [default: False]
        Whether to check the user's .ipython/nbextensions directory.
        Otherwise check a system-wide install (e.g. /usr/local/share/jupyter/nbextensions).
    :param prefix: str [optional]
        Specify install prefix, if it should differ from default (e.g. /usr/local).
        Will check prefix/share/jupyter/nbextensions
    :param nbextensions_dir: str [optional]
        Specify absolute path of nbextensions directory explicitly.
    :return: list: list of installed notebook extension (by the user)

    You can install extensions with function @see fn install_notebook_extension.
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
    Installs a kernel based on executable (this python by default).

    @param  exe                 Python executable
                                current one by default
    @param  kernel_spec_manager (KernelSpecManager [optional]).
                                A KernelSpecManager to use for installation.
                                If none provided, a default instance will be created.
    @param  user                (bool).
                                Whether to do a user-only install, or system-wide.
    @param  kernel_name         (str), optional.
                                Specify a name for the kernelspec.
                                This is needed for having multiple IPython
                                kernels for different environments.
    @param  prefix              (str), optional.
                                Specify an install prefix for the kernelspec.
                                This is needed to install into a non-default
                                location, such as a conda/virtual-env.

    @return                     The path where the kernelspec was installed.

    A kernel is defined by the following fields:

    ::

        {
            "display_name": "Python 3 (ENSAE)",
            "language": "python",
            "argv": [ "c:\\\\PythonENSAE\\\\python\\\\python.exe",
                      "-m",
                      "ipykernel",
                      "-f",
                      "{connection_file}"
                    ]
         }

    For R, it looks like:

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
    """
    exe = exe.replace("pythonw.exe", "python.exe")
    dest = install_k(kernel_spec_manager=kernel_spec_manager,
                     user=user, kernel_name=kernel_name, prefix=prefix)
    kernel_file = os.path.join(dest, "kernel.json")
    kernel = dict(display_name=kernel_name,
                  language="python",
                  argv=[exe, "-m", "ipykernel", "-f", "{connection_file}"])

    s = json.dumps(kernel)
    with open(kernel_file, "w") as f:
        f.write(s)

    return dest


def install_python_kernel_for_unittest(suffix=None):
    """
    Installs a kernel based on this python (sys.executable) for unit test purposes.

    @param      suffix      suffix to add to the kernel name
    @return                 kernel name
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
    Removes a kernel.

    @param      kernel_spec_manager     see `KernelSpecManager <http://jupyter-client.readthedocs.org/
                                        en/latest/api/kernelspec.html#jupyter_client.kernelspec.KernelSpecManager>`_
                                        A KernelSpecManager to use for installation.
                                        If none provided, a default instance will be created.
    @param      kernel_name             kernel name

    The function only works with *Jupyter>=4.0*.
    """
    kernels = find_notebook_kernel(kernel_spec_manager=kernel_spec_manager)
    if kernel_name in kernels:
        fold = kernels[kernel_name]
        if not os.path.exists(fold):
            raise FileNotFoundError("unable to remove folder " + fold)
        remove_folder(fold)
    else:
        raise NotebookException(  # pragma: no cover
            "Unable to find kernel '{0}' in {1}".format(
                kernel_name, ", ".join(kernels.keys())))


def remove_execution_number(infile, outfile=None, encoding="utf-8", indent=2, rule=int):
    """
    Removes execution number from a notebook.

    @param      infile      filename of the notebook
    @param      outfile     None ot save the file
    @param      encoding    encoding
    @param      indent      indentation
    @param      rule        determines the rule which specifies execution numbers,
                            'None' for None, 'int' for consectuive integers numbers.
    @return                 modified string or None if outfile is not None and the file was not modified

    .. todoext::
        :title: remove execution number from notebook facilitate git versionning
        :tag: enhancement
        :issue: 18
        :cost: 1
        :hidden:
        :date: 2016-08-23
        :release: 1.4

        Remove execution number from the notebook
        to avoid commiting changes only about those numbers

    `notebook 5.1.0 <http://jupyter-notebook.readthedocs.io/en/stable/changelog.html#release-5-1-0>`_
    introduced changes which are incompatible with
    leaving the cell executing number empty.
    """
    def fixup(adict, k, v, cellno=0, outputs="outputs"):
        for key in adict.keys():
            if key == k:
                if rule is None:
                    adict[key] = v
                elif rule is int:
                    cellno += 1
                    adict[key] = cellno
                else:
                    raise ValueError(  # pragma: no cover
                        "Rule '{0}' does not apply on {1}={2}".format(rule, key, adict[key]))
            elif key == "outputs":
                if isinstance(adict[key], dict):
                    fixup(adict[key], k, v, cellno=cellno, outputs=outputs)
                elif isinstance(adict[key], list):
                    for el in adict[key]:
                        if isinstance(el, dict):
                            fixup(el, k, v, cellno=cellno, outputs=outputs)
            elif isinstance(adict[key], dict):
                cellno = fixup(adict[key], k, v,
                               cellno=cellno, outputs=outputs)
            elif isinstance(adict[key], list):
                for el in adict[key]:
                    if isinstance(el, dict):
                        cellno = fixup(el, k, v, cellno=cellno,
                                       outputs=outputs)
        return cellno

    content = read_content_ufs(infile)
    js = json.loads(content)
    fixup(js, "execution_count", None)
    st = StringIO()
    json.dump(js, st, indent=indent, sort_keys=True)
    res = st.getvalue()
    if outfile is not None:
        if content != res:
            with open(outfile, "w", encoding=encoding) as f:
                f.write(res)
            return content
        return None
    return res
