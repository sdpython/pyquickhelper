"""
@file
@brief Functions to run notebooks.
"""
import time
import os
import warnings
import re
from io import StringIO
import urllib.request as urllib_request
from datetime import datetime, timedelta

from ..loghelper.flog import noLOG
from ..filehelper import explore_folder
from .notebook_runner import NotebookRunner, NotebookKernelError
from .notebook_exception import NotebookException
from .notebook_helper import writes


try:
    from nbformat.reader import reads
    from nbformat.reader import NotJSONError
except ImportError:  # pragma: no cover
    from IPython.nbformat.reader import reads
    from IPython.nbformat.reader import NotJSONError


def _cache_url_to_file(cache_urls, folder, fLOG=noLOG):
    """
    Downloads file corresponding to url stored in *cache_urls*.

    @param      cache_urls      list of urls
    @param      folder          where to store the cached files
    @param      fLOG            logging function
    @return                     dictionary { url: file }

    The function detects if the file was already downloaded.
    In that case, it does not do it a second time.
    """
    if cache_urls is None:
        return None
    if folder is None:
        raise FileNotFoundError(  # pragma: no cover
            "folder cannot be None")
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
                 detailed_log=None, startup_timeout=300):
    """
    Runs a notebook end to end,
    it is inspired from module `runipy <https://github.com/paulgb/runipy/>`_.

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
    @param      startup_timeout     wait for this long for the kernel to be ready,
                                    see `wait_for_ready
                                    <https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/blocking/client.py#L84>`_
    @return                         tuple (statistics, output)

    @warning The function calls `basicConfig
    <https://docs.python.org/3/library/logging.html#logging.basicConfig>`_.

    .. exref::
        :title: Run a notebook end to end

        ::

            from pyquickhelper.ipythonhelper import run_notebook
            run_notebook("source.ipynb", working_dir="temp",
                        outfilename="modified.ipynb",
                        additional_path=["custom_path"] )

    The function adds the local variable ``theNotebook`` with
    the absolute file name of the notebook.

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionchanged:: 1.8
        Parameters *detailed_log*, *startup_timeout* were added.
    """
    cached_rep = _cache_url_to_file(cache_urls, working_dir, fLOG=fLOG)
    if replacements is None:
        replacements = cached_rep
    elif cached_rep is not None:
        cached_rep.update(replacements)
    else:
        cached_rep = replacements

    with open(filename, "r", encoding=encoding) as payload:
        try:
            nbc = payload.read()
        except UnicodeDecodeError as e:  # pragma: no cover
            raise NotebookException(
                "(2) Unable to read file '{0}' encoding='{1}'.".format(filename, encoding)) from e
    try:
        nb = reads(nbc)
    except NotJSONError as e:  # pragma: no cover
        raise NotebookException(
            "(1) Unable to read file '{0}' encoding='{1}'.".format(filename, encoding)) from e

    out = StringIO()

    def flogging(*args, **kwargs):
        if len(args) > 0:
            out.write(" ".join(args))
        if len(kwargs) > 0:
            out.write(str(kwargs))
        out.write("\n")
        fLOG(*args, **kwargs)

    try:
        nb_runner = NotebookRunner(nb, profile_dir, working_dir, fLOG=flogging, filename=filename,
                                   theNotebook=os.path.abspath(filename),
                                   code_init=code_init, log_level=log_level,
                                   extended_args=extended_args, kernel_name=kernel_name,
                                   replacements=cached_rep, kernel=True, detailed_log=detailed_log,
                                   startup_timeout=startup_timeout)
    except NotebookKernelError:  # pragma: no cover
        # It fails. We try again once.
        nb_runner = NotebookRunner(nb, profile_dir, working_dir, fLOG=flogging, filename=filename,
                                   theNotebook=os.path.abspath(filename),
                                   code_init=code_init, log_level=log_level,
                                   extended_args=extended_args, kernel_name=kernel_name,
                                   replacements=cached_rep, kernel=True, detailed_log=detailed_log,
                                   startup_timeout=startup_timeout)

    try:
        stat = nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
                                      valid=valid, clean_function=clean_function)

        if outfilename is not None:
            with open(outfilename, 'w', encoding=encoding) as f:
                try:
                    s = writes(nb_runner.nb)
                except NotebookException as e:  # pragma: no cover
                    raise NotebookException(
                        "issue with notebook: '{}'".format(filename)) from e
                if isinstance(s, bytes):
                    s = s.decode('utf8')
                f.write(s)

    finally:
        nb_runner.shutdown_kernel()

    return stat, out.getvalue()


def execute_notebook_list(folder, notebooks, clean_function=None, valid=None, fLOG=noLOG,
                          additional_path=None, deepfLOG=noLOG, kernel_name="python",
                          log_level="30", extended_args=None, cache_urls=None,
                          replacements=None, detailed_log=None, startup_timeout=300):
    """
    Executes a list of notebooks.

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
    @param      startup_timeout     wait for this long for the kernel to be ready,
                                    see `wait_for_ready
                                    <https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/blocking/client.py#L84>`_
    @return                         dictionary of dictionaries ``{ notebook_name: {  } }``

    If *isSuccess* is False, *statistics* contains the execution time, *output* is the exception
    raised during the execution.

    The signature of function ``valid_cell`` is::

        def valid_cell(cell):
            return True or False or None to stop execution of the notebook before this cell

    The signature of function ``clean_function`` is::

        def clean_function(cell):
            return new_cell_content

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionchanged:: 1.8
        Parameters *detailed_log*, *startup_timeout* were added.
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
        fLOG("[execute_notebook_list] {0}/{1} - {2}".format(i + 1,
                                                            len(notebooks), os.path.split(note)[-1]))
        outfile = os.path.join(folder, "out_" + os.path.split(note)[-1])
        cl = time.perf_counter()
        try:
            stat, out = run_notebook(note, working_dir=folder, outfilename=outfile,
                                     additional_path=additional_path, valid=valid,
                                     clean_function=clean_function, fLOG=deepfLOG,
                                     code_init=code_init, kernel_name=kernel_name,
                                     log_level=log_level, extended_args=extended_args,
                                     cache_urls=cache_urls, replacements=replacements,
                                     detailed_log=detailed_log, startup_timeout=startup_timeout)
            if not os.path.exists(outfile):
                raise FileNotFoundError(outfile)  # pragma: no cover
            etime = time.perf_counter() - cl
            results[note] = dict(success=True, output=out, name=note, etime=etime,
                                 date=datetime.now())
            results[note].update(stat)
        except Exception as e:
            etime = time.perf_counter() - cl
            results[note] = dict(success=False, etime=etime, error=e, name=note,
                                 date=datetime.now())
    return results


def _get_dump_default_path(dump):
    """
    Proposes a default location to dump results about notebooks execution.

    @param      dump        location of the dump or module.
    @return                 location of the dump

    The result might be equal to the input if *dump* is already path.
    """
    if hasattr(dump, '__file__') and hasattr(dump, '__name__'):
        # Default value. We check it is none travis or appveyor.
        from ..pycode import is_travis_or_appveyor
        if is_travis_or_appveyor():
            dump = None
        if dump is not None:
            # We guess the package name.
            name = dump.__name__.split('.')[-1]
            loc = os.path.dirname(dump.__file__)
            src_loc = os.path.split(loc)
            if src_loc[-1] == 'src':
                # We choose a path for the dumps in a way
                fold = os.path.join(loc, "..", "..", "..", "_notebook_dumps")
            else:
                src_loc_loc = os.path.split(src_loc[0])
                if src_loc_loc[-1] == 'src':
                    # We choose a path for the dumps in a way
                    fold = os.path.join(
                        loc, "..", "..", "..", "_notebook_dumps")
                else:
                    # This should be a parameter.
                    fold = os.path.join(loc, "..", "..", "_notebook_dumps")
            if not os.path.exists(fold):
                os.mkdir(fold)
            dump = os.path.join(fold, "notebook.{0}.txt".format(name))
            return dump
    return dump


def _existing_dump(dump):
    """
    Loads an existing dump.

    @param      dump    filename
    @return             :epkg:`pandas:DataFrame`
    """
    import pandas
    from pandas.errors import ParserError

    def read_file(dump):
        try:
            df = pandas.read_csv(dump, sep="\t", encoding="utf-8")
        except ParserError:  # pragma: no cover
            df = pandas.read_csv(
                dump, sep="\t", encoding="utf-8", error_bad_lines=False, warn_bad_lines=True)
        return df

    if os.path.exists(dump):
        # There might be some risk here to see another process writing the
        # file at the same time.
        try:
            df = read_file(dump)
        except PermissionError:  # pragma: no cover
            # We try again once.
            time.sleep(10)
            try:
                df = read_file(dump)
            except Exception as e:
                raise RuntimeError(
                    "Unable to read '{0}' due to '{1}'".format(dump, e)) from e
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Unable to read '{0}' due to '{1}'".format(dump, e)) from e
    else:
        df = None

    return df


def execute_notebook_list_finalize_ut(res, dump=None, fLOG=noLOG):
    """
    Checks the list of results and raises an exception if one failed.
    This is meant to be used in unit tests.

    @param      res     output of @see fn execute_notebook_list
    @param      dump    if not None, dump the results of the execution in a flat file
    @param      fLOG    logging function

    The dump relies on :epkg:`pandas` and append the results a previous dump.
    If *dump* is a module, the function stores the output of the execution in a default
    location only if the process does not run on :epkg:`travis` or :epkg:`appveyor`.
    The default location is something like:

    .. runpython::

        from pyquickhelper.ipythonhelper.run_notebook import _get_dump_default_path
        import pyquickhelper
        print(_get_dump_default_path(pyquickhelper))
    """
    if len(res) == 0:
        raise RuntimeError("No notebook was run.")  # pragma: no cover

    def fail_note(v):
        return "error" in v
    fails = [(os.path.split(k)[-1], v)
             for k, v in sorted(res.items()) if fail_note(v)]
    for f in fails:
        fLOG(f)
    for k, v in sorted(res.items()):
        name = os.path.split(k)[-1]
        fLOG(name, v.get("success", None), v.get("etime", None))
    if len(fails) > 0:
        raise fails[0][1]["error"]

    dump = _get_dump_default_path(dump)
    if dump is not None:
        import pandas
        df = _existing_dump(dump)
        new_df = pandas.DataFrame(data=list(res.values()))

        # We replace every EOL.
        def eol_replace(t):
            return t.replace("\r", "").replace("\n", "\\n")

        subdf = new_df.select_dtypes(include=['object']).applymap(eol_replace)
        for c in subdf.columns:
            new_df[c] = subdf[c]

        if df is None:
            df = new_df
        else:
            df = pandas.concat([df, new_df]).copy()

        # There could be a conflict while several
        # processes in parallel could overwrite the same file.
        if not os.path.exists(dump):
            df.to_csv(dump, sep="\t", encoding="utf-8", index=False)
        else:
            # There might be some risk here to see another process
            # writing or reading the file at the same time.
            # Module filelock does not work in this case.
            # locket (https://github.com/mwilliamson/locket.py) was not tried.
            try:
                df.to_csv(dump, sep="\t", encoding="utf-8", index=False)
            except PermissionError:  # pragma: no cover
                time.sleep(7)
                df.to_csv(dump, sep="\t", encoding="utf-8", index=False)


def notebook_coverage(module_or_path, dump=None, too_old=30):
    """
    Extracts a list of notebooks and merges with a list of runs dumped by
    function @see fn execute_notebook_list_finalize_ut.

    @param      module_or_path      a module or a path
    @param      dump                dump (or None to get the location by default)
    @param      too_old             drop executions older than *too_old* days from now
    @return                         dataframe

    If *module_or_path* is a module, the function will get a list notebooks
    assuming it follows the same design as :epkg:`pyquickhelper`.
    """
    if dump is None:
        dump = _get_dump_default_path(module_or_path)
    else:
        dump = _get_dump_default_path(dump)

    # Create the list of existing notebooks.
    if isinstance(module_or_path, list):
        nbs = [_[1] if isinstance(_, tuple) else _ for _ in module_or_path]
    elif hasattr(module_or_path, '__file__') and hasattr(module_or_path, '__name__'):
        fold = os.path.dirname(module_or_path.__file__)
        _doc = os.path.join(fold, "..", "..", "_doc")
        if not os.path.exists(_doc):
            raise FileNotFoundError(  # pragma: no cover
                "Unable to find path '{0}' for module '{1}'".format(
                    _doc, module_or_path))
        nbpath = os.path.join(_doc, "notebooks")
        if not os.path.exists(nbpath):
            raise FileNotFoundError(  # pragma: no cover
                "Unable to find path '{0}' for module '{1}'".format(
                    nbpath, module_or_path))
        nbs = explore_folder(nbpath, ".*[.]ipynb$")[1]
    else:
        nbpath = module_or_path
        nbs = explore_folder(nbpath, ".*[.]ipynb$")[1]

    import pandas
    dfnb = pandas.DataFrame(data=dict(notebooks=nbs))
    dfnb["notebooks"] = dfnb["notebooks"].apply(lambda x: os.path.normpath(x))
    dfnb = dfnb[~dfnb.notebooks.str.contains(".ipynb_checkpoints")].copy()
    dfnb["key"] = dfnb["notebooks"].apply(lambda x: "/".join(os.path.normpath(
        x).replace("\\", "/").split("/")[-3:]) if isinstance(x, str) else x)
    dfnb["key"] = dfnb["key"].apply(
        lambda x: x.lower() if isinstance(x, str) else x)

    # There might be some risk here to see another process writing the
    # file at the same time.
    try:
        dfall = pandas.read_csv(dump, sep="\t", encoding="utf-8")
    except PermissionError:  # pragma: no cover
        # We try again once.
        time.sleep(10)
        dfall = pandas.read_csv(dump, sep="\t", encoding="utf-8")

    # We drop too old execution.
    old = datetime.now() - timedelta(too_old)
    old = "%04d-%02d-%02d" % (old.year, old.month, old.day)
    dfall = dfall[dfall.date > old].copy()

    # We add a key to merge.
    dfall["name"] = dfall["name"].apply(lambda x: os.path.normpath(x))
    dfall["key"] = dfall["name"].apply(lambda x: "/".join(os.path.normpath(
        x).replace("\\", "/").split("/")[-3:]) if isinstance(x, str) else x)
    dfall["key"] = dfall["key"].apply(
        lambda x: x.lower() if isinstance(x, str) else x)

    # We keep the last execution.
    gr = dfall.sort_values("date", ascending=False).groupby(
        "key", as_index=False).first().reset_index(drop=True).copy()
    gr = gr.drop("name", axis=1)

    # Folders might be different so we merge on the last part of the path.
    merged = dfnb.merge(gr, left_on="key", right_on="key", how="outer")
    merged = merged[merged.notebooks.notnull()]
    merged = merged.sort_values("key").reset_index(drop=True).copy()

    if "last_name" not in merged.columns:
        merged["last_name"] = merged["key"].apply(
            lambda x: os.path.split(x)[-1])

    # We check there is no duplicates in merged.
    for c in ["key", "last_name"]:
        names = [_ for _ in merged[c] if isinstance(_, str)]
        if len(names) > len(set(names)):
            raise ValueError(  # pragma: no cover
                "Unexpected duplicated names in column '{1}'\n{0}".format(
                    "\n".join(sorted(names)), c))

    return merged


def badge_notebook_coverage(df, image_name):
    """
    Builds a badge reporting on the notebook coverage.
    It gives the proportion of run cells.

    @param      df          output of @see fn notebook_coverage
    @param      image_name  image to produce
    @return                 coverage estimation

    The function relies on module :epkg:`Pillow`.
    """
    cell = df["nbcell"].sum()
    run = df["nbrun"].sum()
    valid = df["nbvalid"].sum()
    cov = run * 100.0 / cell if cell > 0 else 1.0
    dcov = min(100., cov)
    val = valid * 100.0 / cell if cell > 0 else 1.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ImportWarning)
        from PIL import Image, ImageFont, ImageDraw
    if cov <= 60:
        color = (200, 87, 51)
    elif cov <= 70:
        color = (200, 156, 18)
    elif cov <= 75:
        color = (140, 140, 140)
    elif cov <= 80:
        color = (88, 171, 171)
    elif cov <= 85:
        color = (88, 140, 86)
    elif cov <= 90:
        color = (80, 155, 86)
    elif cov <= 95:
        color = (80, 190, 73)
    else:
        color = (20, 190, 50)
    img = Image.new(mode='RGB', size=(70, 20), color=color)
    im = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    try:
        cov = int(cov)
        cov = min(cov, 100)
    except ValueError:  # pragma: no cover
        cov = "?"
    try:
        val = int(val)
        val = min(val, 100)
    except ValueError:  # pragma: no cover
        val = "?"
    if cov != val:
        im.text((3, 4), "NB:{0}%-{1}%          ".format(cov, val),
                (255, 255, 255), font=font)
    else:
        im.text((3, 4), "NB: {0}%          ".format(
            cov), (255, 255, 255), font=font)
    img.save(image_name)
    return dcov


def get_additional_paths(modules):
    """
    Returns a list of paths to add before running the notebooks
    for a given a list of modules.

    @return             list of paths
    """
    addpath = [os.path.dirname(mod.__file__) for mod in modules]
    addpath = [os.path.normpath(os.path.join(_, "..")) for _ in addpath]
    return addpath


def retrieve_notebooks_in_folder(folder, posreg=".*[.]ipynb$", negreg=None):
    """
    Retrieves notebooks in a test folder.

    @param      folder      folder
    @param      regex       regular expression
    @return                 list of found notebooks
    """
    pos = re.compile(posreg)
    neg = re.compile(negreg) if negreg is not None else None
    res = []
    for name in os.listdir(folder):
        if pos.search(name):
            if neg is None or not neg.search(name):
                res.append(os.path.join(folder, name))
    if len(res) == 0:
        raise FileNotFoundError(  # pragma: no cover
            "No notebook found in '{0}'.".format(folder))
    return res
