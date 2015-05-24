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


def get_exporter(format):
    """
    return the IPython exporter associated to a format

    @param      format      string (see below)
    @return                 class

    available formats: slides, pdf, latex, markdown, html, rst, python, notebook, template
    """
    if format == "python":
        from IPython.nbconvert import PythonExporter
        return PythonExporter
    elif format == "slides":
        from IPython.nbconvert import SlidesExporter
        return SlidesExporter
    elif format == "html":
        from IPython.nbconvert import HTMLExporter
        return HTMLExporter
    elif format == "pdf":
        from IPython.nbconvert import PDFExporter
        return PDFExporter
    elif format == "template":
        from IPython.nbconvert import TemplateExporter
        return TemplateExporter
    elif format == "markdown":
        from IPython.nbconvert import MarkdownExporter
        return MarkdownExporter
    elif format == "notebook":
        from IPython.nbconvert import NotebookExporter
        return NotebookExporter
    elif format == "rst":
        from IPython.nbconvert import RSTExporter
        return RSTExporter
    elif format == "lagex":
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
        nbr = read_nb(nb_file)
        nb = nbr.nb

    if add_tag:
        run = NotebookRunner(nb)
        run.add_tag_slide()
        nb = run.nb

    exporter = get_exporter("slides")()
    source, meta = exporter.from_notebook_node(nb)

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    post_process_slides_output(outfile, False, False, False)
    res = [outfile]

    # we copy javascript dependencies, reveal.js
    dirname = os.path.dirname(outfile)
    reveal = os.path.join(dirname, "reveal.js")
    if not os.path.exists(reveal):
        cp = install_javascript_tools(None, dest=dirname)
        res.extend(cp)

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
        nbr = read_nb(nb_file)
        nb = nbr.nb

    exporter = get_exporter("html")()
    source, meta = exporter.from_notebook_node(nb)

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    post_process_html_output(outfile, False, False, False)
    res = [outfile]
    return res
