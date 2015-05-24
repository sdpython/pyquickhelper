# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""

import os
import sys
import shutil

from ..loghelper.flog import run_cmd, fLOG
from .utils_sphinx_doc_helpers import HelpGenException, find_latex_path, find_pandoc_path
from ..filehelper.synchelper import has_been_updated
from .post_process import post_process_latex_output, post_process_latex_output_any, post_process_rst_output, post_process_html_output, post_process_slides_output
from ..ipythonhelper import read_nb

if sys.version_info[0] == 2:
    from codecs import open


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


def get_ipython_program(exe=None, pandoc_path=None):
    """
    get ipython executable + fix an issue with PANDOC

    @param      exe             path to python executable
    @param      pandoc_path     if None, call @see fn find_pandoc_path
    @return                     ipython executable
    """
    if exe is None:
        exe = os.path.dirname(sys.executable)
    if pandoc_path is None:
        pandoc_path = find_pandoc_path()
    if sys.platform.startswith("win"):
        user = os.environ["USERPROFILE"]
        path = pandoc_path.replace("%USERPROFILE%", user)
        p = os.environ["PATH"]
        if path not in p:
            p += ";%WINPYDIR%\DLLs;" + path
            os.environ["WINPYDIR"] = exe
            os.environ["PATH"] = p

        if not exe.endswith("Scripts"):
            ipy = os.path.join(exe, "Scripts", "ipython3.exe")
            if not os.path.exists(ipy):
                # Anaconda is different
                ipy = os.path.join(exe, "Scripts", "ipython.exe")
                if not os.path.exists(ipy):
                    raise FileNotFoundError(ipy)
        else:
            ipy = os.path.join(exe, "ipython3.exe")
            if not os.path.exists(ipy):
                # Anaconda is different
                ipy = os.path.join(exe, "ipython.exe")
                if not os.path.exists(ipy):
                    raise FileNotFoundError(ipy)
    else:
        ipy = os.path.join(exe, "ipython")

    return ipy


def process_notebooks(notebooks,
                      outfold,
                      build,
                      latex_path=None,
                      pandoc_path=None,
                      formats=[
                          "ipynb", "html", "python", "rst", "slides", "pdf"]
                      ):
    """
    Converts notebooks into html, rst, latex, pdf, python, docx using
    `nbconvert <http://ipython.org/ipython-doc/rel-1.0.0/interactive/nbconvert.html>`_.

    @param      notebooks   list of notebooks
    @param      outfold     folder which will contains the outputs
    @param      build       temporary folder which contains all produced files
    @param      pandoc_path path to pandoc
    @param      formats     list of formats to convert into (pdf format means latex then compilation)
    @param      latex_path  path to the latex compiler
    @return                 list of tuple *[(file, created or skipped)]*

    This function relies on `pandoc <http://johnmacfarlane.net/pandoc/index.html>`_.
    It also needs modules `pywin32 <http://sourceforge.net/projects/pywin32/>`_,
    `pygments <http://pygments.org/>`_.

    `pywin32 <http://sourceforge.net/projects/pywin32/>`_ might have some issues
    to find its DLL, look @see fn import_pywin32.

    The latex compilation uses `MiKTeX <http://miktex.org/>`_.
    The conversion into Word document directly uses pandoc.
    It still has an issue with table.

    Some latex templates (for nbconvert) uses ``[commandchars=\\\\\\{\\}]{\\|}`` which allows commands ``\\\\`` and it does not compile.
    The one used here is ``report``.
    Some others bugs can be found at: `schlichtanders/latex_test.html <https://gist.github.com/schlichtanders/e108ed0be80108178af2>`_.
    For example, you must not let spaces between symbol ``$`` and the
    formulas it indicates.

    If *pandoc_path* is None, uses @see fn find_pandoc_path to guess it.
    If *latex_path* is None, uses @see fn find_latex_path to guess it.

    @example(convert a notebook into multiple formats)
    @code
    process_notebooks("td1a_correction_session7.ipynb",
                      "dest_folder",
                      "dest_folder",
                      formats=["ipynb", "html", "python", "rst", "slides", "pdf", "docx"])
    @endcode
    @endexample

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.
        Add defaults values for *pandoc_path*, *latex_path*.

    .. versionchanged:: 1.0
        Assumes IPython 3 is installed. It might no work for earlier versions.

    .. versionchanged:: 1.1
        Add format slides. Return type was changed.
    """
    if pandoc_path is None:
        pandoc_path = find_pandoc_path()

    if latex_path is None:
        latex_path = find_latex_path()

    if isinstance(notebooks, str):
        notebooks = [notebooks]

    if "PANDOCPY" in os.environ and sys.platform.startswith("win"):
        exe = os.environ["PANDOCPY"]
        exe = exe.rstrip("\\/")
        if exe.endswith("\\Scripts"):
            exe = exe[:len(exe) - len("Scripts") - 1]
        if not os.path.exists(exe):
            raise FileNotFoundError(exe)
        fLOG("** using PANDOCPY", exe)
    else:
        if sys.platform.startswith("win"):
            from .utils_pywin32 import import_pywin32
            import_pywin32()
        exe = os.path.split(sys.executable)[0]

    extensions = {"ipynb": ".ipynb",
                  "latex": ".tex",
                  "pdf": ".pdf",
                  "html": ".html",
                  "rst": ".rst",
                  "python": ".py",
                  "docx": ".docx",
                  "word": ".docx",
                  "slides": ".slides.html",
                  }

    ipy = get_ipython_program(exe, pandoc_path)

    cmd = '{0} nbconvert --to {1} "{2}"{5} --output="{3}/{4}"'
    files = []
    skipped = []

    if "slides" in formats:
        build_slide = os.path.join(build, "bslides")
        if not os.path.exists(build_slide):
            os.mkdir(build_slide)

    if "WinPython" in sys.executable:
        # pip, or any program in Scripts cannot find python.exe
        # for the distribution WinPython
        keep_path = os.environ["PATH"]
        os.environ["PATH"] = os.path.dirname(sys.executable) + ";" + keep_path
        path_modified = True
    else:
        path_modified = False

    for notebook in notebooks:
        thisfiles = []

        nbout = os.path.split(notebook)[-1]
        if " " in nbout:
            raise HelpGenException(
                "spaces are not allowed in notebooks file names: {0}".format(notebook))
        nbout = os.path.splitext(nbout)[0]
        for format in formats:

            # output
            trueoutputfile = os.path.join(build, nbout + extensions[format])
            fLOG("--- produce ", trueoutputfile)
            pandoco = "docx" if format in ["word", "docx"] else None

            # we chech it was not done before
            if os.path.exists(trueoutputfile):
                dto = os.stat(trueoutputfile).st_mtime
                dtnb = os.stat(notebook).st_mtime
                if dtnb < dto:
                    fLOG("-- skipping notebook", format,
                         notebook, "(", trueoutputfile, ")")
                    if trueoutputfile not in thisfiles:
                        thisfiles.append(trueoutputfile)
                    if pandoco is None:
                        skipped.append(trueoutputfile)
                        continue
                    else:
                        out2 = os.path.splitext(
                            trueoutputfile)[0] + "." + pandoco
                        if os.path.exists(out2):
                            skipped.append(trueoutputfile)
                            continue

            # if the format is slides, we update the metadata
            if format == "slides":
                nb_slide = add_tag_for_slideshow(notebook, build_slide)
                fLOG("NB SLIDE: run add_tag_for_slideshow", nb_slide)
            else:
                nb_slide = None

            # next
            options = ""
            if format == "pdf":
                title = os.path.splitext(
                    os.path.split(notebook)[-1])[0].replace("_", " ")
                options = ' --SphinxTransformer.author="" --SphinxTransformer.overridetitle="{0}"'.format(
                    title)
                format = "latex"
                compilation = True
            elif format in ["word", "docx"]:
                format = "html"
                compilation = False
            elif format in ["slides"]:
                options += " --reveal-prefix reveal.js"
                compilation = False
            else:
                compilation = False

            # output
            outputfile = os.path.join(build, nbout + extensions[format])
            fLOG("--- produce ", outputfile)

            templ = "full" if format != "latex" else "article"
            fLOG("### convert into ", format, " NB: ", notebook,
                 " ### ", os.path.exists(outputfile), ":", outputfile)

            if format == "html":
                fmttpl = " --template {0}".format(templ)
            else:
                fmttpl = ""

            c = cmd.format(ipy,  format,
                           notebook if nb_slide is None else nb_slide,
                           build, nbout, fmttpl)

            c += options
            fLOG("NB:", c)

            #
            if format not in ["ipynb"]:
                # for latex file
                if format == "latex":
                    cwd = os.getcwd()
                    os.chdir(build)

                if not sys.platform.startswith("win"):
                    c = c.replace('"', '')
                # , shell = sys.platform.startswith("win"))
                out, err = run_cmd(
                    c, wait=True, do_not_log=True, log_error=False)

                if format == "latex":
                    os.chdir(cwd)

                if "raise ImportError" in err:
                    raise ImportError(err)
                if len(err) > 0:
                    if format == "latex":
                        # there might be some errors because the latex script needs to be post-processed
                        # sometimes (wrong characters such as " or formulas not
                        # captured as formulas)
                        pass
                    else:
                        err = err.lower()
                        if "error" in err or "critical" in err or "bad config" in err:
                            raise HelpGenException(err)

            format = extensions[format].strip(".")

            # we add the file to the list of generated files
            if outputfile not in thisfiles:
                thisfiles.append(outputfile)

            fLOG("******", format, compilation, outputfile)

            if compilation:
                # compilation latex
                if os.path.exists(latex_path):
                    if sys.platform.startswith("win"):
                        lat = os.path.join(latex_path, "pdflatex.exe")
                    else:
                        lat = "pdflatex"

                    tex = [
                        _ for _ in thisfiles if os.path.splitext(_)[-1] == ".tex"]
                    if len(tex) != 1:
                        raise FileNotFoundError(
                            "no latex file was generated or more than one (={0}), nb={1}".format(len(tex), notebook))
                    tex = tex[0]
                    post_process_latex_output_any(tex)
                    # -interaction=batchmode
                    c = '"{0}" "{1}" -output-directory="{2}"'.format(
                        lat, tex, os.path.split(tex)[0])
                    fLOG("   ** LATEX compilation (b)", c)
                    if not sys.platform.startswith("win"):
                        c = c.replace('"', '')
                    out, err = run_cmd(
                        c, wait=True, do_not_log=False, log_error=False, shell=sys.platform.startswith("win"))
                    if len(err) > 0:
                        raise HelpGenException(
                            "CMD:\n{0}\nERR:\n{1}".format(c, err))
                    f = os.path.join(build, nbout + ".pdf")
                    if not os.path.exists(f):
                        raise HelpGenException(
                            "missing file: {0}\nERR:\n{1}".format(f, err))
                    thisfiles.append(f)
                else:
                    fLOG("unable to find latex in", latex_path)

            elif pandoco is not None:
                # compilation pandoc
                fLOG("   ** pandoc compilation (b)", pandoco)
                outfilep = os.path.splitext(outputfile)[0] + "." + pandoco

                # for some files, the following error might appear:
                # Stack space overflow: current size 33692 bytes.
                # Use `+RTS -Ksize -RTS' to increase it.
                # it usually means there is something wrong (circular
                # reference, ...)
                if sys.platform.startswith("win"):
                    c = r'"{0}\pandoc.exe" -f html -t {1} "{2}" -o "{3}"'.format(
                        pandoc_path, pandoco, outputfile, outfilep)
                else:
                    c = r'pandoc -f html -t {1} "{2}" -o "{3}"'.format(
                        pandoc_path, pandoco, outputfile, outfilep)

                if not sys.platform.startswith("win"):
                    c = c.replace('"', '')
                out, err = run_cmd(
                    c, wait=True, do_not_log=False, log_error=False, shell=sys.platform.startswith("win"))
                if len(err) > 0:
                    raise HelpGenException(
                        "issue with cmd: %s\nERR:\n%s" % (c, err))

            if format == "html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\nERR:\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "pdf" in formats, False, "python" in formats,
                                                  "slides" in formats)

            elif format == "slides.html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\nERR:\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "pdf" in formats, False, "python" in formats,
                                                  "slides" in formats)

            elif format == "ipynb":
                # we just copy the notebook
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "ipynb" in formats, False, "python" in formats,
                                                  "slides" in formats)

            elif format == "rst":
                # we add a link to the notebook
                thisfiles += add_link_to_notebook(
                    outputfile, notebook, "pdf" in formats, "html" in formats, "python" in formats,
                    "slides" in formats)

            elif format in ("tex", "latex", "pdf"):
                thisfiles += add_link_to_notebook(outputfile,
                                                  notebook, False, False, False, False)

            elif format == "py":
                pass

            elif format in ["docx", "word"]:
                pass

            else:
                raise HelpGenException("unexpected format " + format)

            files.extend(thisfiles)

    copy = []
    for f in files:
        dest = os.path.join(outfold, os.path.split(f)[-1])
        if not f.endswith(".tex"):

            if sys.version_info >= (3, 4):
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ", f, " to ", outfold, "[", dest, "]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else:
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ", f, " to ", outfold, "[", dest, "]")
                except shutil.Error as e:
                    if "are the same file" in str(e):
                        fLOG("w,file ", dest, "already exists")
                    else:
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
        copy.append((dest, True))

    # image
    for image in os.listdir(build):
        if image.endswith(".png") or image.endswith(
                ".html") or image.endswith(".pdf"):
            image = os.path.join(build, image)
            dest = os.path.join(outfold, os.path.split(image)[-1])

            if sys.version_info >= (3, 4):
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ", image, " to ", outfold, "[", dest, "]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else:
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ", image, " to ", outfold, "[", dest, "]")
                except shutil.Error as e:
                    if "are the same file" in str(e):
                        fLOG("w,file ", dest, "already exists")
                    else:
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
            copy.append((dest, True))

    # for the distribution WinPython
    if path_modified:
        os.environ["PATH"] = keep_path

    return copy + [(_, False) for _ in skipped]


def add_link_to_notebook(file, nb, pdf, html, python, slides):
    """
    add a link to the notebook in HTML format and does a little bit of cleaning
    for various format

    @param      file        notebook.html
    @param      nb          notebook (.ipynb)
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
    @param      slides      if True, add a link to the HTML slides
    @return                 list of generated files

    The function does some cleaning too in the files.

    .. versionadded:: 1.1
        Parameter slides was added.
    """
    core, ext = os.path.splitext(file)
    if core.endswith(".slides"):
        ext = ".slides" + ext
    fLOG("    add_link_to_notebook", ext, " file ", file)

    fold, name = os.path.split(file)
    res = [os.path.join(fold, os.path.split(nb)[-1])]
    newr, reason = has_been_updated(nb, res[-1])
    if newr:
        shutil.copy(nb, fold)

    if ext == ".ipynb":
        return res
    elif ext == ".pdf":
        return res
    elif ext == ".html":
        post_process_html_output(file, pdf, python, slides)
        return res
    elif ext == ".slides.html":
        post_process_slides_output(file, pdf, python, slides)
        return res
    elif ext == ".tex":
        post_process_latex_output(file, True)
        return res
    elif ext == ".rst":
        post_process_rst_output(
            file, html, pdf, python, slides, is_notebook=True)
        return res
    else:
        raise HelpGenException(
            "unable to add a link to this extension: " + ext)


def add_notebook_page(nbs, fileout):
    """
    creates a rst page with links to all notebooks

    @param      nbs             list of notebooks to consider
    @param      fileout         file to create
    @return                     created file name
    """
    rst = [_ for _ in nbs if _.endswith(".rst")]

    rows = ["", ".. _l-notebooks:", "", "", "Notebooks", "=========", ""]

    # exp = re.compile("[.][.] _([-a-zA-Z0-9_]+):")
    rst = sorted(rst)

    rows.append("")
    rows.append(".. toctree::")
    rows.append("    :maxdepth: 2")
    rows.append("")
    for file in rst:
        rows.append(
            "    notebooks/{0}".format(os.path.splitext(os.path.split(file)[-1])[0]))

    rows.append("")
    with open(fileout, "w", encoding="utf8") as f:
        f.write("\n".join(rows))
    return fileout


def add_tag_for_slideshow(ipy, folder, encoding="utf8"):
    """
    modifes a notebook to add tag for a slideshow

    @param      ipy         notebook file
    @param      folder      where to write the new notebook
    @param      encoding    encoding
    @return                 written file
    """
    filename = os.path.split(ipy)[-1]
    output = os.path.join(folder, filename)
    nb = read_nb(ipy, encoding=encoding)
    nb.add_tag_slide()
    nb.to_json(output)
    return output
