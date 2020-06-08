"""
@file
@brief Command line about noteboooks.
"""
import os


def run_notebook(filename, profile_dir='', working_dir='',
                 skip_exceptions=False,
                 outfilename='', additional_path='',
                 kernel_name="python", log_level="30",
                 startup_timeout=300,
                 verbose=0, fLOG=print):
    """
    Runs a notebook end to end,
    it is inspired from module `runipy <https://github.com/paulgb/runipy/>`_.

    :param filename: notebook filename
    :param profile_dir: profile directory
    :param working_dir: working directory
    :param skip_exceptions: skip exceptions
    :param outfilename: if not None, saves the output in this notebook
    :param additional_path: additional paths for import (comma separated)
    :param kernel_name: kernel name, it can be None
    :param log_level: Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    :param detailed_log: a second function to log more information when executing the notebook,
                                    this should be a function with the same signature as ``print`` or None
    :param startup_timeout: wait for this long for the kernel to be ready,
        see `wait_for_ready
        <https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/blocking/client.py#L84>`_
    :param verbose: 0 for standard logging, 1 for more
    :param fLOG: logging function
    :return: tuple (statistics, output)

    .. cmdref::
        :title: Run a notebook
        :cmd: -m pyquickhelper run_notebook --help

        The command line runs a notebook and stores the modified
        notebook.
    """
    from ..ipythonhelper import run_notebook as _run_notebook
    detailed_log = fLOG if verbose else None
    if profile_dir == '':
        profile_dir = None
    if working_dir == '':
        working_dir = None
    if outfilename == '':
        outfilename = None
    if additional_path in ('', None):
        additional_path = None
    else:
        additional_path = additional_path.split(',')
    return _run_notebook(filename, profile_dir=profile_dir, working_dir=working_dir,
                         skip_exceptions=skip_exceptions, outfilename=outfilename,
                         additional_path=additional_path, kernel_name=kernel_name,
                         log_level=log_level, startup_timeout=int(
                             startup_timeout),
                         fLOG=fLOG, detailed_log=detailed_log)


def convert_notebook(filename, outfold=None, build=None,
                     latex_path=None, pandoc_path=None,
                     formats="html,python", exc=True, nblinks=None,
                     remove_unicode_latex=False,
                     fLOG=print):
    """
    Converts a notebook into a specific format.

    :param filename: notebook name
    :param outfold: notebook is first copied into this directory
        to make some preprocessing. This directory must exist,
        directory ``_convertnb`` will be created otherwise.
    :param build: can be the current one
    :param latex_path: if format includes latex
    :param pandoc_path: for word format
    :param formats: list of formats to use (comma separated),
        full list is ``ipynb,html,python,rst,slides,pdf,github``
    :param exc: raises an exception of be silent
    :param nblinks: to add some link
    :param remove_unicode_latex: should not be necessary

    .. cmdref::
        :title: Convert a notebook into a different format
        :cmd: -m pyquickhelper convert_notebook --help

        The command line converts notebook into HTML, RST, PDF, slides...
        It calls :epkg:`nbconvert` but adds some preprocessing before calling
        it.
    """
    from ..helpgen.process_notebooks import process_notebooks
    if not os.path.exists(filename):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}'.".format(filename))
    if outfold in ('.', '', None):
        outfold = os.path.abspath(os.path.dirname(filename))
    if not os.path.exists(outfold):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}'.".format(outfold))
    if build in ('.', '', None):
        build = os.path.join(outfold, "_convertnb")
        if not os.path.exists(build):
            os.mkdir(build)
    if not os.path.exists(build):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}'.".format(build))
    return process_notebooks(
        notebooks=filename, outfold=outfold, build=build,
        latex_path=latex_path, pandoc_path=pandoc_path,
        formats=formats, exc=exc, nblinks=nblinks,
        remove_unicode_latex=remove_unicode_latex,
        fLOG=fLOG)
