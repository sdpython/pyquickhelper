# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""

import os
import sys
import shutil

from ..loghelper.flog import run_cmd, fLOG, noLOG
from .utils_sphinx_doc_helpers import HelpGenException
from .conf_path_tools import find_latex_path, find_pandoc_path
from ..filehelper.synchelper import has_been_updated, explore_folder
from .post_process import post_process_latex_output, post_process_latex_output_any, post_process_rst_output
from .post_process import post_process_html_output, post_process_slides_output, post_process_python_output
from .helpgen_exceptions import NotebookConvertError
from .install_js_dep import install_javascript_tools
from .style_css_template import THUMBNAIL_TEMPLATE
from ..ipythonhelper import read_nb, notebook_coverage, badge_notebook_coverage
from ..pandashelper import df2rst


if sys.version_info[0] == 2:
    from codecs import open
    FileNotFoundError = Exception
    from StringIO import StringIO
else:
    from io import StringIO


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


def process_notebooks(notebooks, outfold, build, latex_path=None, pandoc_path=None,
                      formats=("ipynb", "html", "python", "rst",
                               "slides", "pdf", "present", "github"), fLOG=fLOG, exc=True,
                      nblinks=None):
    """
    Converts notebooks into html, rst, latex, pdf, python, docx using
    :epkg:`nbconvert`.

    @param      notebooks   list of notebooks
    @param      outfold     folder which will contains the outputs
    @param      build       temporary folder which contains all produced files
    @param      pandoc_path path to pandoc
    @param      formats     list of formats to convert into (pdf format means latex then compilation)
    @param      latex_path  path to the latex compiler
    @param      fLOG        logging function
    @param      exc         raises an exception (True) or a warning (False) if an error happens
    @param      nblinks     dictionary ``{ref: url}``
    @return                 list of tuple *[(file, created or skipped)]*

    This function relies on :epkg:`pandoc`.
    It also needs modules :epkg:`pywin32`,
    :epkg:`pygments`.

    :epkg:`pywin32` might have some issues
    to find its DLL, look @see fn import_pywin32.

    The latex compilation uses :epkg:`MiKTeX`.
    The conversion into Word document directly uses pandoc.
    It still has an issue with table.

    Some latex templates (for nbconvert) uses ``[commandchars=\\\\\\{\\}]{\\|}`` which allows commands ``\\\\`` and it does not compile.
    The one used here is ``report``.
    Some others bugs can be found at: `schlichtanders/latex_test.html <https://gist.github.com/schlichtanders/e108ed0be80108178af2>`_.
    For example, you must not let spaces between symbol ``$`` and the
    formulas it indicates.

    If *pandoc_path* is None, uses @see fn find_pandoc_path to guess it.
    If *latex_path* is None, uses @see fn find_latex_path to guess it.

    .. exref::
        :title: Convert a notebook into multiple formats

        ::

            from pyquickhelper.ipythonhelper import process_notebooks
            process_notebooks("td1a_correction_session7.ipynb",
                            "dest_folder",
                            "dest_folder",
                            formats=("ipynb", "html", "python", "rst", "slides", "pdf", "docx", "present", "github")])

    .. versionchanged:: 1.4
        Add another format for the slides (with :epkg:`nbpresent`).
        Replace command line by direct call to
        :epkg:`nbconvert`, :epkg:`nbpresent`.

    .. versionchanged:: 1.5
        For latex and pdf, a custom processor was added to handle raw data
        and add ``\\begin{verbatim}`` and ``\\end{verbatim}``.
        Parameter *exc*, *nblinks* were added.
        Format *github* was added, it adds a link to file on github.

    .. todoext::
        :title: Allow hidden rst instructions in notebook (for references)
        :tag: enhancement
        :issue: 10

        We should be able to add references to the documentation in the documentation
        without referencing the absolute path of the referenced page. One option
        is to add hidden HTML or comments and to publish it when converting the
        notebook to RST.

    .. todoext::
        :title: check differences between _process_notebooks_in_private and _process_notebooks_in_private_cmd
        :tag: bug

        For Latex and PDF, the custom preprocessor is not taken into account.
        by function _process_notebooks_in_private.
    """
    res = _process_notebooks_in(notebooks=notebooks, outfold=outfold, build=build,
                                latex_path=latex_path, pandoc_path=pandoc_path,
                                formats=formats, fLOG=fLOG, exc=exc, nblinks=nblinks)
    if "slides" in formats:
        # we copy javascript dependencies, reveal.js
        reveal = os.path.join(outfold, "reveal.js")
        if not os.path.exists(reveal):
            install_javascript_tools(None, dest=outfold)
        reveal = os.path.join(build, "reveal.js")
        if not os.path.exists(reveal):
            install_javascript_tools(None, dest=build)
    return res


def _process_notebooks_in_private(fnbcexe, list_args, options_args):
    out = StringIO()
    err = StringIO()
    memo_out = sys.stdout
    memo_err = sys.stderr
    sys.stdout = out
    sys.stderr = err
    try:
        if list_args:
            fnbcexe(argv=list_args, **options_args)
        else:
            fnbcexe(**options_args)
        exc = None
    except SystemExit as e:
        exc = e
    except IndentationError as e:
        # This is change in IPython 6.0.0. The conversion fails on IndentationError.
        # We switch to another one.
        i = list_args.index("--template")
        format = list_args[i + 1]
        if format == "python":
            i = list_args.index("--output")
            dest = list_args[i + 1]
            if not dest.endswith(".py"):
                dest += ".py"
            src = list_args[-1]
            nb = read_nb(src)
            code = nb.to_python()
            with open(dest, "w", encoding="utf-8") as f:
                f.write(code)
            exc = None
        else:
            # We do nothing in this case.
            exc = e
    sys.stdout = memo_out
    sys.stderr = memo_err
    out = out.getvalue()
    err = err.getvalue()
    if exc:
        env = "\n".join("{0}={1}".format(k, v)
                        for k, v in sorted(os.environ.items()))
        raise Exception("Notebook conversion failed.\nARGS:\n{0}\nOUT\n{1}\nERR\n{2}\nENVIRON\n{3}".format(
            list_args, out, err, env)) from exc
    return out, err


def _process_notebooks_in_private_cmd(fnbcexe, list_args, options_args, fLOG):
    this = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "process_notebooks_cmd.py")
    res = []
    for c in list_args:
        if c[0] == '"' or c[-1] == '"' or ' ' not in c:
            res.append(c)
        else:
            res.append('"{0}"'.format(c))
    sargs = " ".join(res)
    cmd = '"{0}" "{1}" {2}'.format(
        sys.executable.replace("w.exe", ".exe"), this, sargs)
    fLOG("    ", cmd)
    return run_cmd(cmd, wait=True, fLOG=fLOG)


def _process_notebooks_in(notebooks, outfold, build, latex_path=None, pandoc_path=None,
                          formats=("ipynb", "html", "python", "rst",
                                   "slides", "pdf", "present", "github"),
                          fLOG=fLOG, exc=True, nblinks=None):
    """
    The notebook conversion does not handle image from url
    for PDF and docx. They could be downloaded first
    and replaced by local files.
    """
    from nbconvert.nbconvertapp import main as nbconvert_main
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

    extensions = {"ipynb": ".ipynb", "latex": ".tex", "pdf": ".pdf", "html": ".html", "rst": ".rst",
                  "python": ".py", "docx": ".docx", "word": ".docx", "slides": ".slides.html",
                  "present": ".slides2p.html"}

    files = []
    skipped = []

    # main(argv=None, **kwargs)
    fnbc = nbconvert_main

    if "slides" in formats:
        build_slide = os.path.join(build, "bslides")
        if not os.path.exists(build_slide):
            os.mkdir(build_slide)

    if "present" in formats:
        build_present = os.path.join(build, "bslides_present")
        if not os.path.exists(build_present):
            os.mkdir(build_present)
        from nbpresent.export import export as nbpresent_main
        # def export(ipynb=None, outfile=None, out_format=None, verbose=None):
        fnbp = nbpresent_main

    copied_images = dict()

    for notebook in notebooks:
        thisfiles = []

        # we copy available images (only notebook folder) in case they are used
        # in latex
        currentdir = os.path.dirname(notebook)
        for curfile in os.listdir(currentdir):
            ext = os.path.splitext(curfile)[1]
            if ext in {'.png', '.jpg', '.bmp', '.gif', '.jpeg', '.svg'}:
                src = os.path.join(currentdir, curfile)
                if src not in copied_images:
                    dest = os.path.join(build, curfile)
                    shutil.copy(src, build)
                    fLOG("copy ", src, " to ", build)
                    copied_images[src] = dest

        # next
        nbout = os.path.split(notebook)[-1]
        if " " in nbout:
            raise HelpGenException(
                "spaces are not allowed in notebooks file names: {0}".format(notebook))
        nbout = os.path.splitext(nbout)[0]
        for format in formats:

            if format == "github":
                # we add a link on the rst page in that case
                continue

            if format not in extensions:
                raise NotebookConvertError("unable to find format: {} in {}".format(
                    format, ", ".join(extensions.keys())))

            # output
            format_ = format
            outputfile_noext = os.path.join(build, nbout)
            outputfile = outputfile_noext + extensions[format]
            trueoutputfile = outputfile
            pandoco = "docx" if format in ("word", "docx") else None

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
            options_args = {}
            if format == "slides":
                nb_slide = add_tag_for_slideshow(notebook, build_slide)
                fnbcexe = fnbc
            elif format == "present":
                nb_slide = add_tag_for_slideshow(notebook, build_present)
                fnbcexe = fnbp
                options_args["ipynb"] = notebook
            else:
                nb_slide = None
                fnbcexe = fnbc

            # compilation
            list_args = []
            custom_config = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), "_nbconvert_config.py")
            if format == "pdf":
                if not os.path.exists(custom_config):
                    raise FileNotFoundError(custom_config)
                title = os.path.splitext(
                    os.path.split(notebook)[-1])[0].replace("_", " ")
                list_args.extend(['--config', '"%s"' % custom_config,
                                  '--SphinxTransformer.author=""',
                                  '--SphinxTransformer.overridetitle="{0}"'.format(title)])
                format = "latex"
                compilation = True
                thisfiles.append(os.path.splitext(outputfile)[0] + ".tex")
            elif format == "latex":
                if not os.path.exists(custom_config):
                    raise FileNotFoundError(custom_config)
                list_args.extend(['--config', '"%s"' % custom_config])
                compilation = False
            elif format in ("word", "docx"):
                format = "html"
                compilation = False
            elif format in ("slides", ):
                list_args.extend(["--reveal-prefix", "reveal.js"])
                compilation = False
            elif format in ("present", ):
                options_args["out_format"] = "html"
                compilation = False
            else:
                compilation = False

            # output
            templ = {'html': 'full', 'latex': 'article'}.get(format, format)
            fLOG("### convert into ", format_, " NB: ", notebook,
                 " ### ", os.path.exists(outputfile), ":", outputfile)

            if format in ('present', ):
                options_args["outfile"] = outputfile
            else:
                list_args.extend(["--output", outputfile_noext])
                if templ is not None and format != "slides":
                    list_args.extend(["--template", templ])

            # execution
            if format not in ("ipynb", ):
                # arguments
                if options_args:
                    fLOG("NBp:", format, options_args)
                else:
                    list_args.extend(["--to", format,
                                      notebook if nb_slide is None else nb_slide])
                    fLOG("NBc:", format, list_args)
                    fLOG(os.getcwd())

                # nbconvert is messing up with static variables in sphinx or
                # docutils if format is slides, not sure about the others
                if nbconvert_main != fnbcexe or format not in {"slides", "latex", "pdf"}:
                    out, err = _process_notebooks_in_private(
                        fnbcexe, list_args, options_args)
                else:
                    # conversion into slides alter Jinja2 environment
                    # jinja2.exceptions.TemplateNotFound: rst
                    out, err = _process_notebooks_in_private_cmd(
                        fnbcexe, list_args, options_args, fLOG)

                if "raise ImportError" in err:
                    raise ImportError(err)
                if len(err) > 0:
                    if format == "latex":
                        # there might be some errors because the latex script needs to be post-processed
                        # sometimes (wrong characters such as " or formulas not
                        # captured as formulas)
                        fLOG("LATEX ERR\n" + err)
                        fLOG("LATEX OUT\n" + out)
                    else:
                        err = err.lower()
                        if "critical" in err or "bad config" in err:
                            raise HelpGenException(
                                "CMD:\n{0}\n[nberror]\n{1}".format(list_args, err))
            else:
                # format ipynb
                # we do nothing
                pass

            format = extensions[format].strip(".")

            # we add the file to the list of generated files
            if outputfile not in thisfiles:
                thisfiles.append(outputfile)

            fLOG("    -", format, compilation, outputfile)

            if compilation:
                # compilation latex
                if os.path.exists(latex_path):
                    if sys.platform.startswith("win"):
                        lat = os.path.join(latex_path, "pdflatex.exe")
                    else:
                        lat = "pdflatex"

                    tex = set(_ for _ in thisfiles if os.path.splitext(
                        _)[-1] == ".tex")
                    if len(tex) != 1:
                        raise FileNotFoundError(
                            "no latex file was generated or more than one (={0}), nb={1}\nthisfile=\n{2}".format(len(tex), notebook, "\n".join(thisfiles)))
                    tex = list(tex)[0]
                    post_process_latex_output_any(
                        tex, custom_latex_processing=None, nblinks=nblinks, fLOG=fLOG)
                    # -interaction=batchmode
                    c = '"{0}" "{1}" -max-print-line=900 -output-directory="{2}"'.format(
                        lat, tex, os.path.split(tex)[0])
                    fLOG("   ** LATEX compilation (b)", c)
                    if not sys.platform.startswith("win"):
                        c = c.replace('"', '')
                    out, err = run_cmd(
                        c, wait=True, log_error=False, shell=sys.platform.startswith("win"),
                        catch_exit=True, prefix_log="[latex] ")
                    if err is not None and len(err) == 0 and out is not None and "Output written" in out:
                        # The output was produced. We ignore the return code.
                        fLOG("WARNINGS: Latex compilation had warnings:", c)
                        out += "\nERR\n" + err
                        err = ""
                    if len(err) > 0:
                        raise HelpGenException(
                            "CMD:\n{0}\n[nberror]\n{1}\nOUT:\n{2}".format(c, err, out))
                    f = os.path.join(build, nbout + ".pdf")
                    if not os.path.exists(f):
                        raise HelpGenException(
                            "missing file: {0}\nOUT:\n{2}\n[nberror]\n{1}".format(f, err, out))
                    thisfiles.append(f)
                else:
                    fLOG("unable to find latex in", latex_path)

            elif pandoco is not None:
                # compilation pandoc
                fLOG("   ** pandoc compilation (b)", pandoco)
                inputfile = os.path.splitext(outputfile)[0] + ".html"
                outfilep = os.path.splitext(outputfile)[0] + "." + pandoco

                # for some files, the following error might appear:
                # Stack space overflow: current size 33692 bytes.
                # Use `+RTS -Ksize -RTS' to increase it.
                # it usually means there is something wrong (circular
                # reference, ...)
                if sys.platform.startswith("win"):
                    c = '"{0}\\pandoc.exe" +RTS -K32m -RTS -f html -t {1} "{2}" -o "{3}"'.format(
                        pandoc_path, pandoco, inputfile, outfilep)
                else:
                    c = 'pandoc +RTS -K32m -RTS -f html -t {0} "{1}" -o "{2}"'.format(
                        pandoco, outputfile, outfilep)

                if not sys.platform.startswith("win"):
                    c = c.replace('"', '')
                out, err = run_cmd(
                    c, wait=True, log_error=False, shell=sys.platform.startswith("win"))
                if len(err) > 0:
                    lines = err.strip("\r\n").split("\n")
                    # we filter out the message
                    # pandoc.exe: Could not find image `https://
                    left = [
                        _ for _ in lines if _ and "Could not find image `http" not in _]
                    if len(left) > 0:
                        raise HelpGenException(
                            "issue with cmd: %s\n[nberror]\n%s" % (c, err))
                    else:
                        for _ in lines:
                            fLOG("w, pandoc issue: {0}".format(
                                _.strip("\n\r")))
                outputfile = outfilep
                format = "docx"

            if format == "html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\n[nberror]\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "pdf" in formats, False, "python" in formats,
                                                  "slides" in formats, "present" in formats, exc=exc,
                                                  nblinks=nblinks, fLOG=fLOG)

            elif format == "slides.html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\n[nberror]\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + str(list_args))
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "pdf" in formats, False, "python" in formats,
                                                  "slides" in formats, "present" in formats, exc=exc,
                                                  nblinks=nblinks, fLOG=fLOG)

            elif format == "slides2p.html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\n[nberror]\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "pdf" in formats, False, "python" in formats,
                                                  "slides" in formats, "present" in formats, exc=exc,
                                                  nblinks=nblinks, fLOG=fLOG)

            elif format == "ipynb":
                # we just copy the notebook
                thisfiles += add_link_to_notebook(outputfile, notebook,
                                                  "ipynb" in formats, False, "python" in formats,
                                                  "slides" in formats, "present" in formats, exc=exc,
                                                  nblinks=nblinks, fLOG=fLOG)

            elif format == "rst":
                # we add a link to the notebook
                thisfiles += add_link_to_notebook(
                    outputfile, notebook, "pdf" in formats, "html" in formats, "python" in formats,
                    "slides" in formats, "present" in formats, exc=exc, github="github" in formats,
                    notebook=notebook, nblinks=nblinks, fLOG=fLOG)

            elif format in ("tex", "latex", "pdf"):
                thisfiles += add_link_to_notebook(outputfile, notebook, False, False,
                                                  False, False, False, exc=exc, nblinks=nblinks,
                                                  fLOG=fLOG)

            elif format in ("py", "python"):
                post_process_python_output(
                    outputfile, True, nblinks=nblinks, fLOG=fLOG)

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
        if image.endswith(".png") or image.endswith(".html") or \
           image.endswith(".pdf") or image.endswith(".svg") or \
           image.endswith(".jpg") or image.endswith(".gif") or \
           image.endswith(".xml") or image.endswith(".jpeg"):
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

    return copy + [(_, False) for _ in skipped]


def add_link_to_notebook(file, nb, pdf, html, python, slides, present, exc=True,
                         github=False, notebook=None, nblinks=None, fLOG=None):
    """
    add a link to the notebook in HTML format and does a little bit of cleaning
    for various format

    @param      file        notebook.html
    @param      nb          notebook (.ipynb)
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
    @param      slides      if True, add a link to the HTML slides
    @param      present     if True, add a link to the HTML present
    @param      exc         raises an exception (True) or a warning (False)
    @param      github      add a link to the notebook on github
    @param      notebook    location of the notebook (file might be a copy)
    @param      nblinks     dictionary ``{ref: url}``
    @param      fLOG        logging function
    @return                 list of generated files

    The function does some cleaning too in the files.

    .. versionchanged:: 1.4
        Parameter *present* was added.

    .. versionchanged:: 1.5
        Parameters *exc*, *github*, *notebook* were added.
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
        post_process_html_output(
            file, pdf, python, slides, present, exc=exc, nblinks=nblinks, fLOG=fLOG)
        return res
    elif ext == ".slides.html":
        post_process_slides_output(
            file, pdf, python, slides, present, exc=exc, nblinks=nblinks, fLOG=fLOG)
        return res
    elif ext == ".slides2p.html":
        post_process_slides_output(
            file, pdf, python, slides, present, exc=exc, nblinks=nblinks, fLOG=fLOG)
        return res
    elif ext == ".tex":
        post_process_latex_output(
            file, True, exc=exc, nblinks=nblinks, fLOG=fLOG)
        return res
    elif ext == ".py":
        post_process_python_output(
            file, True, exc=exc, nblinks=nblinks, fLOG=fLOG)
        return res
    elif ext == ".rst":
        post_process_rst_output(
            file, html, pdf, python, slides, present, is_notebook=True, exc=exc,
            github=github, notebook=notebook, nblinks=nblinks, fLOG=fLOG)
        return res
    else:
        raise HelpGenException(
            "unable to add a link to this extension: " + ext)


def build_thumbail_in_gallery(nbfile, folder_snippet, relative, rst_link):
    """
    Returns RST code for a notebook.

    @param      nbfile          notebook file
    @param      folder_snippet  where to store the snippet
    @param      relative        the path to the snippet will be relative to this folder
    @param      rst_link        rst link
    @return                     RST
    """
    nb = read_nb(nbfile)
    title, desc = nb.get_description()
    image = nb.get_thumbnail()
    name = os.path.splitext(os.path.split(nbfile)[-1])[0]
    name += ".thumb"
    full = os.path.join(folder_snippet, name)

    dirname = os.path.dirname(full)
    if not os.path.exists(dirname):
        raise FileNotFoundError("Unable to find folder '{0}'\nfolder_snippet='{1}'\nrelative='{2}'\nnbfile='{3}'".format(
            dirname, folder_snippet, relative, nbfile))

    if isinstance(image, str):
        # SVG
        full += ".svg"
        name += ".svg"
        with open(full, "w", encoding="utf-8") as f:
            f.write(image)
    else:
        # Image
        full += ".png"
        name += ".png"
        image.save(full)

    rel = os.path.relpath(full, start=relative).replace("\\", "/")
    rst = THUMBNAIL_TEMPLATE.format(
        snippet=desc, thumbnail=rel, ref_name=rst_link)
    return rst


def add_tag_for_slideshow(ipy, folder, encoding="utf8"):
    """
    modifes a notebook to add tag for a slideshow

    @param      ipy         notebook file
    @param      folder      where to write the new notebook
    @param      encoding    encoding
    @return                 written file
    """
    from ..ipythonhelper import read_nb
    filename = os.path.split(ipy)[-1]
    output = os.path.join(folder, filename)
    nb = read_nb(ipy, encoding=encoding, kernel=False)
    nb.add_tag_slide()
    nb.to_json(output)
    return output


def build_notebooks_gallery(nbs, fileout, fLOG=noLOG):
    """
    Creates a rst page (gallery) with links to all notebooks.
    For each notebook, it creates a snippet.

    @param      nbs             list of notebooks to consider or tuple(full path, rst),
    @param      fileout         file to create
    @param      fLOG            logging function
    @return                     created file name

    Example for parameter *nbs*:

    ::

        ('challenges\\city_tour\\city_tour_1.ipynb', 'ensae_projects\\_doc\\notebooks\\challenges\\city_tour\\city_tour_1.ipynb')
        ('challenges\\city_tour\\city_tour_1_solution.ipynb', 'ensae_projects\\_doc\\notebooks\\challenges\\city_tour\\city_tour_1_solution.ipynb')
        ('challenges\\city_tour\\city_tour_data_preparation.ipynb', 'ensae_projects\\_doc\\notebooks\\challenges\\city_tour\\city_tour_data_preparation.ipynb')
        ('challenges\\city_tour\\city_tour_long.ipynb', 'ensae_projects\\_doc\\notebooks\\challenges\\city_tour\\city_tour_long.ipynb')
        ('cheat_sheets\\chsh_files.ipynb', 'ensae_projects\\_doc\\notebooks\\cheat_sheets\\chsh_files.ipynb')
        ('cheat_sheets\\chsh_geo.ipynb', 'ensae_projects\\_doc\\notebooks\\cheat_sheets\\chsh_geo.ipynb')

    *nbs* can be a folder, in that case, the function will build
    the list of all notebooks in that folder.

    .. todoext::
        :title: merge functionalities from sphinx_nbexamples
        :tag: done
        :hidden: true
        :date: 2016-12-25
        :cost: 2
        :issue: 40
        :release: 1.5

        See blog :ref:`Gallery of notebooks <blog-notebook-gallery>`.

    .. versionchanged:: 1.4
        *nbs* can be a list of tuple

    .. versionchanged:: 1.5
        Add a thumbnail, organize the list of notebook as a gallery.
        The function was renamed into *build_notebooks_gallery*
        (previous name *add_notebook_page*).
        Add a link on notebook coverage.
    """
    if not isinstance(nbs, list):
        fold = nbs
        nbs = explore_folder(fold, ".*[.]ipynb")[1]
        if len(nbs) == 0:
            raise FileNotFoundError(
                "Unable to find notebooks in folder '{0}'.".format(nbs))
        nbs = [(os.path.relpath(n, fold), n) for n in nbs]

    # Go through the list of notebooks.
    fLOG("[build_notebooks_gallery]", len(nbs), "notebooks")
    hier = set()
    rst = []
    containers = {}
    for tu in nbs:
        if isinstance(tu, (tuple, list)):
            if tu[0] is None or ("/" not in tu[0] and "\\" not in tu[0]):
                rst.append((tuple(), tu[1]))
            else:
                way = tuple(tu[0].replace("\\", "/").split("/")[:-1])
                hier.add(way)
                rst.append((way, tu[1]))
        else:
            rst.append((tuple(), tu))
        name = rst[-1][1]
        ext = os.path.splitext(name)[-1]
        if ext != ".ipynb":
            raise ValueError(
                "One file is not a notebook: {0}".format(rst[-1][1]))
        dirname, na = os.path.split(name)
        if dirname not in containers:
            containers[dirname] = []
        containers[dirname].append(na)
    rst.sort()

    folder_index = os.path.dirname(os.path.normpath(fileout))
    folder = os.path.join(folder_index, "notebooks")
    if not os.path.exists(folder):
        os.mkdir(folder)

    # reordering based on titles
    titles = {}
    reord = []
    for hi, nbf in rst:
        nb = read_nb(nbf)
        title, desc = nb.get_description()
        titles[nbf] = title
        reord.append((hi, title, nbf))
    reord.sort()
    rst = [_[:1] + _[-1:] for _ in reord]

    # containers
    containers = list(sorted((k, v) for k, v in containers.items()))

    # find root
    hi, rs = rst[0]
    if len(hi) == 0:
        root = os.path.dirname(rs)
    else:
        spl = rs.replace("\\", "/").split("/")
        ro = spl[:-len(hi) - 1]
        root = "/".join(ro)

    # look for README.txt
    fLOG("[build_notebooks_gallery] root", root)
    exp = os.path.join(root, "README.txt")
    if os.path.exists(exp):
        fLOG("[build_notebooks_gallery] found", exp)
        with open(exp, "r", encoding="utf-8") as f:
            rows = ["", ".. _l-notebooks:", "", f.read(), ""]
    else:
        fLOG("[build_notebooks_gallery] not found", exp)
        rows = ["", ".. _l-notebooks:", "", "", "Notebooks Gallery",
                "=================", ""]

    rows.extend(["", "", ".. contents::", "    :depth: 1",
                 "    :local:", "", "", "Gallery", "+++++++", ""])

    # produces the final files
    if len(hier) == 0:
        # case where there is no hierarchy
        fLOG("[build_notebooks_gallery] no hierarchy")
        rows.append(".. toctree::")
        rows.append("    :maxdepth: 1")
        for hi, file in rst:
            rs = os.path.splitext(os.path.split(file)[-1])[0]
            fLOG("[build_notebooks_gallery] adding",
                 rs, " title ", titles.get(file, None))
            rows.append("    notebooks/{0}".format(rs))

        for no, file in rst:
            link = os.path.splitext(os.path.split(file)[-1])[0]
            link = link.replace("_", "") + "rst"
            if not os.path.exists(file):
                raise FileNotFoundError("Unable to find: '{0}'\nRST=\n{1}".format(
                    file, "\n".join(str(_) for _ in rst)))
            r = build_thumbail_in_gallery(file, folder, folder_index, link)
            rows.append(r)
    else:
        # case where there are subfolders
        fLOG("[build_notebooks_gallery] subfolders")
        already = "\n".join(rows)
        level = "-+^"
        rows.append("")
        if ".. contents::" not in already:
            rows.append(".. contents::")
            rows.append("    :local:")
            rows.append("    :depth: 2")
            rows.append("")
        stack_file = []
        last = None
        for hi, r in rst:
            rs0 = os.path.splitext(os.path.split(r)[-1])[0]
            r0 = r
            if hi != last:
                fLOG("[build_notebooks_gallery] new level", hi)
                # we add the thumbnail
                for nbf in stack_file:
                    fLOG("[build_notebooks_gallery]     ", nbf)
                    rs = os.path.splitext(os.path.split(nbf)[-1])[0]
                    link = rs.replace("_", "") + "rst"
                    r = build_thumbail_in_gallery(
                        nbf, folder, folder_index, link)
                    rows.append(r)
                fLOG("[build_notebooks_gallery] saw {0} files".format(
                    len(stack_file)))
                stack_file = []

                # we swith to the next gallery
                rows.append(".. raw:: html")
                rows.append("")
                rows.append("   <div style='clear:both'></div>")
                rows.append("")

                # we add menus and subfolders
                for k in range(0, len(hi)):
                    if last is None or k >= len(last) or hi[k] != last[k]:
                        break

                while len(hi) > 0 and k < len(hi):
                    fo = [root] + list(hi[:k + 1])
                    readme = os.path.join(*(fo + ["README.txt"]))
                    if os.path.exists(readme):
                        fLOG("[build_notebooks_gallery] found", readme)
                        with open(readme, "r", encoding="utf-8") as f:
                            rows.extend(["", f.read(), ""])
                    else:
                        fLOG("[build_notebooks_gallery] not found", readme)
                        rows.append("")
                        rows.append(hi[k])
                        rows.append(level[min(k, len(level) - 1)] * len(hi[k]))
                        rows.append("")
                    k += 1

                # we start the next gallery
                last = hi
                rows.append(".. toctree::")
                rows.append("    :maxdepth: 1")
                rows.append("")

            # append a link to a notebook
            fLOG("[build_notebooks_gallery] adding",
                 rs0, " title ", titles.get(r0, None))
            rows.append("    notebooks/{0}".format(rs0))
            stack_file.append(r0)

        if len(stack_file) > 0:
            # we add the thumbnails
            for nbf in stack_file:
                rs = os.path.splitext(os.path.split(nbf)[-1])[0]
                link = rs.replace("_", "") + "rst"
                r = build_thumbail_in_gallery(nbf, folder, folder_index, link)
                rows.append(r)

    # done
    rows.append("")

    # links to coverage
    rows.extend(["", "Coverage", "++++++++", "", ".. toctree::",
                 "    all_notebooks_coverage", ""])

    with open(fileout, "w", encoding="utf8") as f:
        f.write("\n".join(rows))
    return fileout


def build_all_notebooks_coverage(nbs, fileout, module_name, dump=None, badge=True, fLOG=noLOG):
    """
    Creates a rst page (gallery) with links to all notebooks and
    information about coverage.
    It relies on function @see fn notebook_coverage.

    @param      nbs             list of notebooks to consider or tuple(full path, rst),
    @param      fileout         file to create
    @param      module_name     module name
    @param      dump            dump containing information about notebook execution (or None for the default one)
    @param      badge           builds an image with the notebook coverage
    @param      fLOG            logging function
    @return                     created file name
    """
    if dump is None:
        dump = os.path.normpath(os.path.join(os.path.dirname(fileout), "..", "..", "..", "..",
                                             "_notebook_dumps", "notebook.{0}.txt".format(module_name)))
    if not os.path.exists(dump):
        fLOG(
            "[notebooks-coverage] No execution report about notebook at '{0}'".format(dump))
        return
    report0 = notebook_coverage(nbs, dump)
    fLOG("[notebooks-coverage] report shape", report0.shape)

    from numpy import isnan

    # Fill nan values.
    for i in report0.index:
        nbcell = report0.loc[i, "nbcell"]
        if isnan(nbcell):
            # We load the notebook.
            nbfile = report0.loc[i, "notebooks"]
            nb = read_nb(nbfile)
            report0.loc[i, "nbcell"] = len(nb)
            report0.loc[i, "nbrun"] = 0

    # Add links.
    cols = ['notebooks', 'date', 'etime',
            'nbcell', 'nbrun', 'nbvalid', 'success', 'time']
    report = report0[cols].copy()
    report["notebooks"] = report["notebooks"].apply(
        lambda x: "/".join(os.path.normpath(x).replace("\\", "/").split("/")[-2:]) if isinstance(x, str) else x)
    report["last_name"] = report["notebooks"].apply(
        lambda x: os.path.split(x)[-1] if isinstance(x, str) else x)

    def clean_link(link):
        return link.replace("_", "").replace(".ipynb", ".rst").replace(".", "") if isinstance(link, str) else link

    report["notebooks"] = report.apply(lambda row: ':ref:`{0} <{1}>`'.format(
        row["notebooks"], clean_link(row["last_name"])), axis=1)
    report["title"] = report["last_name"].apply(
        lambda x: ':ref:`{0}`'.format(clean_link(x)))
    rows = ["", ".. _l-notebooks-coverage:", "", "", "Notebooks Coverage",
            "==================", "", "Report on last executions.", ""]

    # Badge
    if badge:
        img = os.path.join(os.path.dirname(fileout), "nbcov.png")
        badge_notebook_coverage(report0, img)
        badge = ["", ".. image:: nbcov.png", ""]
    else:
        badge = []
    rows.extend(badge)

    # Formatting
    report["date"] = report["date"].apply(
        lambda x: x.split()[0] if isinstance(x, str) else x)
    report["etime"] = report["etime"].apply(
        lambda x: "%1.3f" % x if isinstance(x, float) else x)
    report["time"] = report["time"].apply(
        lambda x: "%1.3f" % x if isinstance(x, float) else x)

    def int2str(x):
        if isnan(x):
            return ""
        else:
            return int(x)

    report["nbcell"] = report["nbcell"].apply(int2str)
    report["nbrun"] = report["nbrun"].apply(int2str)
    report["nbvalid"] = report["nbvalid"].apply(int2str)
    report = report[['notebooks', 'title', 'date', 'success', 'etime',
                     'nbcell', 'nbrun', 'nbvalid', 'time']].copy()
    report.columns = ['name', 'title', 'last execution', 'success', 'time',
                      'nb cells', 'nb runs', 'nb valid', 'exe time']

    # Add results
    text = df2rst(report.sort_values("name"), index=True)
    rows.append(text)

    fLOG("[notebooks-coverage] writing", fileout)
    with open(fileout, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
