"""
@file
@brief Command line about noteboooks.
"""
from ..ipythonhelper import run_notebook as _run_notebook


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
