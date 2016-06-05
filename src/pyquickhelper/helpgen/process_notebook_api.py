# -*- coding: utf-8 -*-
"""
@file
@brief Direct calls to IPython API without running a command line

.. versionadded:: 1.1
"""
import os
import sys
from .install_js_dep import install_javascript_tools
from .post_process import post_process_slides_output, post_process_html_output

if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
else:
    from io import StringIO


def get_exporter(format):
    """
    return the IPython exporter associated to a format

    @param      format      string (see below)
    @return                 class

    available formats: slides, pdf, latex, markdown, html, rst, python, notebook, template
    """
    if format == "python":
        try:
            from nbconvert import PythonExporter
        except ImportError:
            from IPython.nbconvert import PythonExporter
        return PythonExporter
    elif format == "slides":
        try:
            from nbconvert import SlidesExporter
        except ImportError:
            from IPython.nbconvert import SlidesExporter
        return SlidesExporter
    elif format == "html":
        try:
            from nbconvert import HTMLExporter
        except ImportError:
            from IPython.nbconvert import HTMLExporter
        return HTMLExporter
    elif format == "pdf":
        try:
            from nbconvert import PDFExporter
        except ImportError:
            from IPython.nbconvert import PDFExporter
        return PDFExporter
    elif format == "template":
        try:
            from nbconvert import TemplateExporter
        except ImportError:
            from IPython.nbconvert import TemplateExporter
        return TemplateExporter
    elif format == "markdown":
        try:
            from nbconvert import MarkdownExporter
        except ImportError:
            from IPython.nbconvert import MarkdownExporter
        return MarkdownExporter
    elif format == "notebook":
        try:
            from nbconvert import NotebookExporter
        except ImportError:
            from IPython.nbconvert import NotebookExporter
        return NotebookExporter
    elif format == "rst":
        try:
            from nbconvert import RSTExporter
        except ImportError:
            from IPython.nbconvert import RSTExporter
        return RSTExporter
    elif format == "lagex":
        try:
            from nbconvert import LatexExporter
        except ImportError:
            from IPython.nbconvert import LatexExporter
        return LatexExporter
    else:
        form = "slides, pdf, latex, markdown, html, rst, python, notebook, template"
        raise ValueError(
            "unexpected format: {0}, it should be in:\n{1}".format(format, form))


def nb2slides(nb_file, outfile, add_tag=True):
    """
    convert a notebooks into slides, it copies
    reveal.js if not present in the folder of the output

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @param      add_tag         call @see me add_tag_slide
    @return                     impacted files

    See `How do I convert a IPython Notebook into a Python file via commandline? <http://stackoverflow.com/questions/17077494/how-do-i-convert-a-ipython-notebook-into-a-python-file-via-commandline>`_

    @example(Convert a notebook into slides)
    By default, the function automatically adds sections if there is none
    and it copies the javascript from reveal.js at the right place.
    @code
    from pyquickhelper import nb2slides
    nb2slides("nb.ipynb", "convert.slides.html")
    @endcode
    @endexample
    """
    from ..ipythonhelper import NotebookRunner, read_nb

    if isinstance(nb_file, NotebookRunner):
        nb = nb_file.nb
    else:
        nbr = read_nb(nb_file, kernel=False)
        nb = nbr.nb

    if add_tag:
        run = NotebookRunner(nb, kernel=False)
        run.add_tag_slide()
        nb = run.nb

    exporter = get_exporter("slides")()
    source, meta = exporter.from_notebook_node(nb)

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    post_process_slides_output(outfile, False, False, False, False)
    res = [outfile]

    # we copy javascript dependencies, reveal.js
    dirname = os.path.dirname(outfile)
    reveal = os.path.join(dirname, "reveal.js")
    if not os.path.exists(reveal):
        cp = install_javascript_tools(None, dest=dirname)
        res.extend(cp)

    return res


def _nbpresent_export(ipynb=None, outfile=None, out_format=None, verbose=None):
    if out_format in ["pdf"]:
        raise NotImplementedError(
            "format {0} is not allowed".format(out_format))
    elif out_format in ["html"]:
        from nbpresent.exporters.html import PresentExporter as Exporter

    from nbpresent.exporters import APP_ROOT

    exp = Exporter(
        template_file="nbpresent",
        template_path=[os.path.join(APP_ROOT, "templates")]
    )

    output, resources = exp.from_file(ipynb)
    if outfile is None:
        return output
    else:
        with open(outfile, "w", encoding="utf-8") as fp:
            fp.write(output)
    return output


def nb2present(nb_file, outfile, add_tag=True):
    """
    convert a notebooks into slides, it copies
    reveal.js if not present in the folder of the output

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @param      add_tag         call @see me add_tag_slide
    @return                     impacted files

    .. versionadded:: 1.4
    """
    from ..ipythonhelper import NotebookRunner, read_nb

    if isinstance(nb_file, NotebookRunner):
        nb = nb_file.nb
    else:
        nbr = read_nb(nb_file, kernel=False)
        nb = nbr.nb

    run = NotebookRunner(nb, kernel=False)
    if add_tag:
        run.add_tag_slide()

    # to be implemented
    js = run.to_json()
    st = StringIO(js)
    content = _nbpresent_export(st, outfile, out_format="html")
    if outfile is None:
        outfile = content

    # post_processing
    post_process_slides_output(outfile, False, False, False, False)
    res = [outfile]
    return res


def nb2html(nb_file, outfile):
    """
    convert a notebooks into html

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @return                     impacted files
    """
    from ..ipythonhelper import NotebookRunner, read_nb

    if isinstance(nb_file, NotebookRunner):
        nb = nb_file.nb
    else:
        nbr = read_nb(nb_file, kernel=False)
        nb = nbr.nb

    exporter = get_exporter("html")()
    source, meta = exporter.from_notebook_node(nb)

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    post_process_html_output(outfile, False, False, False, False)
    res = [outfile]
    return res
