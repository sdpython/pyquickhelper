"""
@file
@brief Function to run notebooks

.. versionadded:: 1.4
    Split from *notebook_helper.py*.
"""
import sys
import time
import os

from ..loghelper.flog import noLOG
from .notebook_runner import NotebookRunner
from .notebook_exception import NotebookException
from .notebook_helper import writes


try:
    from nbformat.reader import reads
except ImportError:
    from IPython.nbformat.reader import reads


if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
    FileNotFoundError = Exception
    import urllib2 as urllib_request
else:
    from io import StringIO
    import urllib.request as urllib_request


def _cache_url_to_file(cache_urls, folder, fLOG=noLOG):
    """
    download file corresponding to url stored in *cache_urls*

    @param      cache_urls      list of urls
    @param      folder          where to store the cached files
    @param      fLOG            logging function
    @return                     dictionary { url: file }

    The function detects if the file was already downloaded.
    In that case, it does not do it a second time.

    .. versionadded:: 1.4
    """
    if cache_urls is None:
        return None
    if folder is None:
        raise FileNotFoundError("folder cannot be None")
    res = {}
    for url in cache_urls:
        local_file = "__cached__" + url.split("/")[-1]
        local_file = local_file.replace(":", "_").replace("%", "_")
        local_file = os.path.abspath(os.path.join(folder, local_file))
        if not os.path.exists(local_file):
            fLOG("download", url, "to", local_file)
            with open(local_file, "wb") as f:
                fu = urllib_request.urlopen(url)
                c = fu.read(2 ** 21)
                while len(c) > 0:
                    f.write(c)
                    f.flush()
                    c = fu.read(2 ** 21)
                fu.close()

        # to avoid having backslahes inside strings
        res[url] = "file:///" + local_file.replace("\\", "/")
    return res


def run_notebook(filename, profile_dir=None, working_dir=None, skip_exceptions=False,
                 outfilename=None, encoding="utf8", additional_path=None,
                 valid=None, clean_function=None, code_init=None,
                 fLOG=noLOG, kernel_name="python", log_level="30",
                 extended_args=None, cache_urls=None, replacements=None,
                 detailed_log=None):
    """
    run a notebook end to end, it uses module `runipy <https://github.com/paulgb/runipy/>`_

    @param      filename            notebook filename
    @param      profile_dir         profile directory
    @param      working_dir         working directory
    @param      skip_exceptions     skip exceptions
    @param      outfilename         if not None, saves the output in this notebook
    @param      encoding            encoding for the notebooks
    @param      additional_path     additional paths for import
    @param      valid               if not None, valid is a function which returns whether
                                    or not the cell should be executed or not, if the function
                                    returns None, the execution of the notebooks and skip the execution
                                    of the other cells
    @param      clean_function      function which cleans a cell's code before executing it (None for None)
    @param      code_init           code to run before the execution of the notebook as if it was a cell
    @param      fLOG                logging function
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @param      cache_urls          list of urls to cache
    @param      replacements        list of additional replacements, list of tuple
    @param      detailed_log        a second function to log more information when executing the notebook,
                                    this should be a function with the same signature as ``print`` or None
    @return                         tuple (statistics, output)

    @warning The function calls `basicConfig <https://docs.python.org/3.4/library/logging.html#logging.basicConfig>`_.

    .. exref::
        :title: Run a notebook end to end

        ::

            from pyquickhelper.ipythonhelper import run_notebook
            run_notebook("source.ipynb", working_dir="temp",
                        outfilename="modified.ipynb",
                        additional_path = [ "c:/temp/mymodule/src" ] )

    The function adds the local variable ``theNotebook`` with
    the absolute file name of the notebook.

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.

    .. versionchanged:: 1.4
        Parameter *cache_urls* was added.
        Function *valid* can return None and stops the execution of the notebook.

    .. versionchanged:: 1.5
        Parameter *detailed_log* was added.
    """
    cached_rep = _cache_url_to_file(cache_urls, working_dir, fLOG=fLOG)
    if replacements is None:
        replacements = cached_rep
    elif cached_rep is not None:
        cached_rep.update(replacements)

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

        nb_runner = NotebookRunner(nb, profile_dir, working_dir, fLOG=flogging, filename=filename,
                                   theNotebook=os.path.abspath(filename),
                                   code_init=code_init, log_level=log_level,
                                   extended_args=extended_args, kernel_name=kernel_name,
                                   replacements=replacements, kernel=True, detailed_log=detailed_log)
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


def execute_notebook_list(folder, notebooks, clean_function=None, valid=None, fLOG=noLOG,
                          additional_path=None, deepfLOG=noLOG, kernel_name="python",
                          log_level="30", extended_args=None, cache_urls=None,
                          replacements=None, detailed_log=None):
    """
    execute a list of notebooks

    @param      folder              folder (where to execute the notebook, current folder for the notebook)
    @param      notebooks           list of notebooks to execute (or a list of tuple(notebook, code which initializes the notebook))
    @param      clean_function      function which transform the code before running it
    @param      valid               if not None, valid is a function which returns whether
                                    or not the cell should be executed or not, if the function
                                    returns None, the execution of the notebooks and skip the execution
                                    of the other cells
    @param      fLOG                logging function
    @param      deepfLOG            logging function used to run the notebook
    @param      additional_path     path to add to *sys.path* before running the notebook
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @param      cache_urls          list of urls to cache
    @param      replacements        additional replacements
    @param      detailed_log        detailed log
    @return                         dictionary ``{ notebook_file: (isSuccess, statistics, outout) }``

    If *isSucess* is False, *statistics* contains the execution time, *output* is the exception
    raised during the execution.

    The signature of function ``valid_cell`` is::

        def valid_cell(cell) : return True or False or None to stop execution of the notebook before this cell

    The signature of function ``clean_function`` is::

        def clean_function(cell) : return new_cell_content

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.

    .. versionchanged:: 1.4
        Parameter *cache_urls* was added.
        Function *valid* can return None.

    .. versionchanged:: 1.5
        Parameter *detailed_log* was added.
    """
    if additional_path is None:
        additional_path = []

    # we cache urls before running through the list of notebooks
    _cache_url_to_file(cache_urls, folder, fLOG=fLOG)

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
                stat, out = run_notebook(note, working_dir=folder, outfilename=outfile,
                                         additional_path=additional_path, valid=valid,
                                         clean_function=clean_function, fLOG=deepfLOG,
                                         code_init=code_init, kernel_name=kernel_name,
                                         log_level=log_level, extended_args=extended_args,
                                         cache_urls=cache_urls, replacements=replacements,
                                         detailed_log=detailed_log)
                if not os.path.exists(outfile):
                    raise FileNotFoundError(outfile)
                results[note] = (True, stat, out)
            except Exception as e:
                etime = time.clock() - cl
                results[note] = (False, dict(time=etime), e)
    return results
