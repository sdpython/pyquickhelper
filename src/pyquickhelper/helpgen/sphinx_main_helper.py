# -*- coding: utf-8 -*-
"""
@file
@brief Contains helpers for the main function @see fn generate_help_sphinx.

"""
import os
import sys
import datetime
import shutil
import subprocess
import re

from ..loghelper import run_cmd, RunCmdException, fLOG
from ..loghelper.run_cmd import parse_exception_message
from ..loghelper.pyrepo_helper import SourceRepository
from ..pandashelper.tblformat import df2rst
from ..filehelper import explore_folder_iterfile
from .utils_sphinx_doc_helpers import HelpGenException
from .post_process import post_process_latex_output
from .process_notebooks import find_pdflatex


template_examples = """

List of programs
++++++++++++++++

.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst

Another list
++++++++++++

"""


def setup_environment_for_help(fLOG=fLOG):
    """
    Modifies environment variables to be able to use external tools
    such as :epkg:`Inkscape`.
    """
    if sys.platform.startswith("win"):
        prog = os.environ["ProgramFiles"]
        inkscape = os.path.join(prog, "Inkscape")
        if not os.path.exists(inkscape):
            raise FileNotFoundError(
                "Inkscape is not installed, expected at: {0}".format(inkscape))
        path = os.environ["PATH"]
        if inkscape not in path:
            fLOG("SETUP: add path to %path%", inkscape)
            os.environ["PATH"] = path + ";" + inkscape
    else:
        pass


def get_executables_path():
    """
    Returns the paths to :epkg:`Python`,
    :epkg:`Python` Scripts.

    @return     a list of paths
    """
    res = [os.path.split(sys.executable)[0]]
    res.extend([os.path.join(res[-1], "Scripts"),
                os.path.join(res[-1], "bin")])
    return res


def my_date_conversion(sdate):
    """
    Converts a date into a datetime.

    @param      sdate       string
    @return                 date
    """
    first = sdate.split(" ")[0]
    trois = first.replace(".", "-").replace("/", "-").split("-")
    return datetime.datetime(int(trois[0]), int(trois[1]), int(trois[2]))


def produce_code_graph_changes(df):
    """
    Returns the code for a graph which counts the number
    of changes per week over the last year.

    @param      df      dataframe (has a column date with format ``YYYY-MM-DD``)
    @return             graph

    The call to :epkg:`datetime.datetime.strptime`
    introduced exceptions::

        File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
        File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
        File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
        File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
        File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

    when generating the documentation for another project. The reason
    is still unclear. It was replaced by a custom function.
    """
    def year_week(x):
        dt = datetime.datetime(x.year, x.month, x.day)
        return dt.isocalendar()[:2]

    def to_str(x):
        year, week = year_week(x)
        return "%d-w%02d" % (year, week)

    df = df.copy()
    df["dt"] = df.apply(lambda r: my_date_conversion(r["date"]), axis=1)
    df = df[["dt"]]
    now = datetime.datetime.now()
    last = now - datetime.timedelta(365)
    df = df[df.dt >= last]
    df["week"] = df['dt'].apply(to_str)
    df["commits"] = 1

    val = []
    for alldays in range(0, 365):
        a = now - datetime.timedelta(alldays)
        val.append({"dt": a, "week": to_str(a), "commits": 0})

    # we move pandas here because it imports matplotlib
    # which is not always wise when you need to modify the backend
    import pandas
    df = pandas.concat([df, pandas.DataFrame(val)], sort=True)

    gr = df[["week", "commits"]].groupby("week", as_index=False).sum()
    xl = list(gr["week"])
    x = list(range(len(xl)))
    y = list(gr["commits"])

    typstr = str

    code = """
            import matplotlib.pyplot as plt
            x = __X__
            y = __Y__
            xl = __XL__
            plt.close('all')
            plt.style.use('ggplot')
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
            ax.bar(x, y)
            tig = ax.get_xticks()
            labs = []
            for t in tig:
                if t in x:
                    labs.append(xl[x.index(t)])
                else:
                    labs.append("")
            ax.set_xticklabels(labs)
            ax.grid(True)
            ax.set_title("commits")
            plt.show()
            """.replace("            ", "") \
               .replace("__X__", typstr(x)) \
               .replace("__XL__", typstr(xl)) \
               .replace("__Y__", typstr(y))

    return code


def generate_changes_repo(chan, source, exception_if_empty=True,
                          filter_commit=lambda c: c.strip() != "documentation",
                          fLOG=fLOG, modify_commit=None):
    """
    Generates a :epkg:`RST` tables containing the changes stored
    by a :epkg:`SVN` or :epkg:`GIT` repository,
    the outcome is stored in a file.
    The log comment must start with ``*`` to be taken into account.

    @param          chan                filename to write (or None if you don't need to)
    @param          source              source folder to get changes for
    @param          exception_if_empty  raises an exception if empty
    @param          filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @param          fLOG                logging function
    @param          modify_commit       function which rewrite the commit text (see below)
    @return                             string (rst tables with the changes)

    :epkg:`pandas` is not imported in the function itself but at the beginning of the module. It
    seemed to cause soe weird exceptions when generating the documentation for another module::

        File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
        File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
        File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
        File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
        File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

    Doing that helps. The cause still remains obscure.
    If not None, function *modify_commit* is called the following way (see below).
    *nbch* is the commit number. *date* can be returned as a datetime or a string.

    ::

        nbch, date, author, comment = modify_commit(nbch, date, author, comment)
    """
    # builds the changes files
    try:
        src = SourceRepository(commandline=True)
        logs = src.log(path=source)
    except Exception as eee:
        if exception_if_empty:
            fLOG("[sphinxerror]-9 unable to retrieve log from " + source)
            raise HelpGenException(
                "unable to retrieve log in " + source + "\n" + str(eee)) from eee
        logs = [("none", 0, datetime.datetime.now(), "-")]
        fLOG("[sphinxerror]-8", eee)

    if len(logs) == 0:
        fLOG("[sphinxerror]-7 unable to retrieve log from " + source)
        if exception_if_empty:
            raise HelpGenException("retrieved logs are empty in " + source)
    else:
        fLOG("info, retrieved ", len(logs), " commits")

    rows = []
    rows.append(
        """\n.. _l-changes:\n\n\nChanges\n=======\n\n__CODEGRAPH__\n\nList of recent changes:\n""")

    typstr = str

    values = []
    for i, row in enumerate(logs):
        n = len(logs) - i
        author, nbch, date, comment = row[:4]
        last = row[-1]
        if last.startswith("http"):
            nbch = "`%s <%s>`_" % (typstr(nbch), last)

        if filter_commit(comment):
            if modify_commit is not None:
                nbch, date, author, comment = modify_commit(
                    nbch, date, author, comment)
            if isinstance(date, datetime.datetime):
                ds = "%04d-%02d-%02d" % (date.year, date.month, date.day)
            else:
                ds = date
            if isinstance(nbch, int):
                values.append(
                    ["%d" % n, "%04d" % nbch, "%s" % ds, author, comment.strip("*")])
            else:
                values.append(
                    ["%d" % n, "%s" % nbch, "%s" % ds, author, comment.strip("*")])

    if len(values) == 0 and exception_if_empty:
        raise HelpGenException(
            "Logs were not empty but there was no comment starting with '*' from '{0}'\n".format(source) +
            "\n".join([typstr(_) for _ in logs]))

    if len(values) > 0:
        import pandas
        tbl = pandas.DataFrame(
            columns=["#", "change number", "date", "author", "comment"], data=values)
        rows.append(
            "\n\n" + df2rst(tbl, list_table=True) + "\n\n")

    final = "\n".join(rows)

    if len(values) > 0:
        code = produce_code_graph_changes(tbl)
        code = code.split("\n")
        code = ["    " + _ for _ in code]
        code = "\n".join(code)
        code = ".. plot::\n" + code + "\n"
        final = final.replace("__CODEGRAPH__", code)

    if chan is not None:
        with open(chan, "w", encoding="utf8") as f:
            f.write(final)
    return final


def compile_latex_output_final(root, latex_path, doall, afile=None, latex_book=False, fLOG=fLOG,
                               custom_latex_processing=None, remove_unicode=False):
    """
    Compiles the :epkg:`latex` documents.

    @param      root                        root
    @param      latex_path                  path to the compiler
    @param      doall                       do more transformation of the latex file before compiling it
    @param      afile                       process a specific file
    @param      latex_book                  do some customized transformation for a book
    @param      fLOG                        logging function
    @param      custom_latex_processing     function which does some post processing of the full latex file
    @param      remove_unicode              remove unicode characters before compiling it

    .. faqreq:
        :title: The PDF is corrupted, SVG are not there

        :epkg:`SVG` graphs are not well processed by the latex compilation.
        It usually goes through the following instruction:

        ::

            \\sphinxincludegraphics{{seance4_projection_population_correction_51_0}.svg}

        And produces the following error:

        ::

            ! LaTeX Error: Unknown graphics extension: .svg.

        This function does not stop if the latex compilation but if the PDF
        is corrupted, the log should be checked to see the errors.
    """
    latex_exe = find_pdflatex(latex_path)
    processed = 0
    tried = []
    for subfolder in ['latex', 'elatex']:
        build = os.path.join(root, "_doc", "sphinxdoc", "build", subfolder)
        if not os.path.exists(build):
            build = root
        tried.append(build)
        for tex in os.listdir(build):
            if tex.endswith(".tex") and (afile is None or afile in tex):
                processed += 1
                file = os.path.join(build, tex)
                if doall:
                    # -interaction=batchmode
                    c = '"{0}" "{1}" -max-print-line=900 -buf-size=10000000 -output-directory="{2}"'.format(
                        latex_exe, file, build)
                else:
                    c = '"{0}" "{1}" -max-print-line=900 -buf-size=10000000 -interaction=nonstopmode -output-directory="{2}"'.format(
                        latex_exe, file, build)
                fLOG("[compile_latex_output_final] LATEX compilation (c)", c)
                post_process_latex_output(file, doall, latex_book=latex_book, fLOG=fLOG,
                                          custom_latex_processing=custom_latex_processing,
                                          remove_unicode=remove_unicode)
                if sys.platform.startswith("win"):
                    change_path = None
                else:
                    # On Linux the parameter --output-directory is sometimes ignored.
                    # And it only works from the current directory.
                    change_path = os.path.split(file)[0]
                try:
                    out, err = run_cmd(c, wait=True, log_error=False, catch_exit=True, communicate=False,
                                       tell_if_no_output=120, fLOG=fLOG, prefix_log="[latex] ", change_path=change_path)
                except Exception as e:
                    # An exception is raised when the return code is an error. We
                    # check that PDF file was written.
                    out, err = parse_exception_message(e)
                    if err is not None and len(err) == 0 and out is not None and "Output written" in out:
                        # The output was produced. We ignore the return code.
                        fLOG("WARNINGS: Latex compilation had warnings:", c)
                    else:
                        raise OSError(
                            "Unable to execute\n{0}".format(c)) from e

                if len(err) > 0 and "Output written on " not in out:
                    raise HelpGenException(
                        "CMD:\n{0}\n[sphinxerror]-6\n{1}\n---OUT:---\n{2}".format(c, err, out))

                # second compilation
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                fLOG("~~~~ LATEX compilation (d)", c)
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                try:
                    out, err = run_cmd(
                        c, wait=True, log_error=False, communicate=False, fLOG=fLOG,
                        tell_if_no_output=600, prefix_log="[latex] ", change_path=change_path)
                except (subprocess.CalledProcessError, RunCmdException):
                    fLOG("[sphinxerror]-5 LATEX ERROR: check the logs")
                    err = ""
                    out = ""
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                if len(err) > 0 and "Output written on " not in out:
                    raise HelpGenException(err)
    if processed == 0:
        raise FileNotFoundError("Unable to find any latex file in folders\n{0}".format(
                                "\n".join(tried)))


def replace_placeholder_by_recent_blogpost(all_tocs, plist, placeholder, nb_post=5, fLOG=fLOG):
    """
    Replaces a place holder by a list of blog post.

    @param      all_tocs        list of files to look into
    @param      plist           list of blog post
    @param      placeholder     place holder to replace
    @param      nb_post         number of blog post to display
    @param      fLOG            logging function
    """
    def make_link(post):
        name = os.path.splitext(os.path.split(post.FileName)[-1])[0]
        s = """<a href="{{ pathto('',1) }}/blog/%s/%s.html">%s - %s</a>""" % (
            post.Year, name, post.Date, post.Title)
        return s

    end = min(nb_post, len(plist))
    for toc in all_tocs:
        with open(toc, "r", encoding="utf8") as f:
            content = f.read()
        if placeholder in content:
            fLOG("  *** update", toc)
            links = [make_link(post) for post in plist[:end]]
            content = content.replace(placeholder, "\n<br />".join(links))
            with open(toc, "w", encoding="utf8") as f:
                f.write(content)


_pattern_images = ".*(([.]png)|([.]gif])|([.]jpeg])|([.]jpg])|([.]svg]))$"


def enumerate_copy_images_for_slides(src, dest, pattern=_pattern_images):
    """
    Copies images, initial intent was for slides,
    once converted into html, link to images are relative to
    the folder which contains them, we copy the images from
    ``_images`` to ``_downloads``.

    @param      src     sources
    @param      dest    destination
    @param      pattern see @see fn explore_folder_iterfile
    @return             enumerator of copied files
    """
    iter = explore_folder_iterfile(src, pattern=pattern)
    for img in iter:
        d = os.path.join(dest, os.path.split(img)[-1])
        if os.path.exists(d):
            os.remove(d)
        shutil.copy(img, dest)
        yield d


def format_history(src, dest, format="basic"):
    """
    Formats history based on module
    `releases <https://github.com/bitprophet/releases>`_.

    @param      src     source history (file)
    @param      dest    destination (file)

    .. versionchanged:: 1.7
        Parameter *format* was added. :epkg:`Sphinx` extension *release*
        is no longer used but the formatting is still available.
    """
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    if format == "release":

        tag = None
        for i in range(0, len(lines)):
            line = lines[i].rstrip("\r\t\n ")
            if line.startswith("===") and i > 0:
                rel = lines[i - 1].rstrip("\r\t\n ")
                if "." in rel:
                    del new_lines[-1]
                    res = "* :release:`{0}`".format(rel)
                    res = res.replace("(", "<").replace(")", ">")
                    if new_lines[-1].startswith("==="):
                        new_lines.append("")
                    new_lines.append(res)
                    tag = None
                else:
                    new_lines.append(line)
            elif len(line) > 0:
                if line.startswith("**"):
                    ll = line.lower().strip("*")
                    if ll in ('bug', 'bugfix', 'bugfixes'):
                        tag = "bug"
                    elif ll in ('features', 'feature'):
                        tag = "feature"
                    elif ll in ('support', 'support'):
                        tag = "support"
                    else:
                        raise ValueError(
                            "Line {0}, unable to infer tag from '{1}'".format(i, line))
                else:
                    nline = line.lstrip("* ")
                    if nline.startswith("`"):
                        if tag is None:
                            tag = 'issue'
                        res = "* :{0}:{1}".format(tag, nline)
                        if new_lines[-1].startswith("==="):
                            new_lines.append("")
                        new_lines.append(res)
                    else:
                        new_lines.append(line)
                        if line.startswith(".. _"):
                            new_lines.append("")
    elif format == "basic":
        reg = re.compile("(.*?)`([0-9]+)`:(.*?)[(]([-0-9]{10})[)]")
        for line in lines:
            match = reg.search(line)
            if match:
                gr = match.groups()
                new_line = "{0}:issue:`{1}`:{2}({3})".format(*gr)
                new_lines.append(new_line)
            else:
                new_lines.append(line.strip("\n\r"))
    else:
        raise ValueError("Unexpected value for format '{0}'".format(format))

    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
