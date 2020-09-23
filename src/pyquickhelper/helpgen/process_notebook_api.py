# -*- coding: utf-8 -*-
"""
@file
@brief Direct calls to IPython API without running a command line
"""
import os
from .utils_sphinx_doc_helpers import HelpGenException


def get_exporter(format, add_writer=False):
    """
    Returns the :epkg:`IPython` exporter associated to a format.

    @param      format      string (see below)
    @param      add_writer  add writer as well
    @return                 class

    Available formats: *slides*, *pdf*, *latex*, *markdown*, *html*,
    *rst*, *python*, *notebook*, *template*.

    ..versionchanged:: 1.7
        Add parameter *add_writer*.
    """
    if format == "python":
        from nbconvert import PythonExporter
        exp = PythonExporter
    elif format == "slides":
        from nbconvert import SlidesExporter
        exp = SlidesExporter
    elif format == "html":
        from nbconvert import HTMLExporter
        exp = HTMLExporter
    elif format == "pdf":
        from nbconvert import PDFExporter
        exp = PDFExporter
    elif format == "template":
        from nbconvert import TemplateExporter
        exp = TemplateExporter
    elif format == "markdown":
        from nbconvert import MarkdownExporter
        exp = MarkdownExporter
    elif format == "notebook":
        from nbconvert import NotebookExporter
        exp = NotebookExporter
    elif format == "rst":
        from .notebook_exporter import UpgradedRSTExporter
        exp = UpgradedRSTExporter
    elif format == "lagex":
        from nbconvert import LatexExporter
        exp = LatexExporter
    else:
        form = "slides, pdf, latex, markdown, html, rst, python, notebook, template"
        raise ValueError(
            "unexpected format: {0}, it should be in:\n{1}".format(format, form))

    if add_writer:
        from nbconvert.writers import FilesWriter
        return exp, FilesWriter
    return exp


def nb2slides(nb_file, outfile, add_tag=True):
    """
    Converts a notebook into slides, it copies
    :epkg:`reveal.js` if not present in the folder of the output.

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @param      add_tag         call @see me add_tag_slide
    @return                     impacted files

    See `How do I convert a IPython Notebook into a Python file via commandline?
    <http://stackoverflow.com/questions/17077494/how-do-i-convert-a-ipython-notebook-into-a-python-file-via-commandline>`_

    .. exref::
        :title: Convert a notebook into slides

        By default, the function automatically adds sections if there is none
        and it copies the javascript from reveal.js at the right place.

        ::

            from pyquickhelper.helpgen import nb2slides
            nb2slides("nb.ipynb", "convert.slides.html")
    """
    from ..ipythonhelper import NotebookRunner, read_nb
    from .post_process import post_process_slides_output

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
    source = exporter.from_notebook_node(nb)[0]

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    post_process_slides_output(outfile, False, False, False, False)
    res = [outfile]

    # we copy javascript dependencies, reveal.js
    dirname = os.path.dirname(outfile)
    reveal = os.path.join(dirname, "reveal.js")
    if not os.path.exists(reveal):
        from .install_js_dep import install_javascript_tools
        cp = install_javascript_tools(None, dest=dirname)
        res.extend(cp)

    return res


def nb2html(nb_file, outfile, exc=True):
    """
    Converts a notebook into HTML.

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @param      exc             raises an exception (True) or a warning (False)
    @return                     impacted files
    """
    from ..ipythonhelper import NotebookRunner, read_nb

    if isinstance(nb_file, NotebookRunner):
        nb = nb_file.nb
    else:
        nbr = read_nb(nb_file, kernel=False)
        nb = nbr.nb

    exporter = get_exporter("html")()
    source = exporter.from_notebook_node(nb)[0]

    with open(outfile, 'w+', encoding="utf8") as fh:
        fh.writelines(source)

    # post_processing
    from .post_process import post_process_html_output
    post_process_html_output(outfile, False, False, False, exc=exc)
    res = [outfile]
    return res


def nb2rst(nb_file, outfile, exc=True, post_process=True):
    """
    Converts a notebook into :epkg:`RST`.

    @param      nb_file         notebook file or a stream or a @see fn read_nb
    @param      outfile         output file (a string)
    @param      exc             raises an exception (True) or a warning (False)
    @param      post_process    calls @see fn post_process_rst_output
    @return                     impacted files
    """
    from ..ipythonhelper import NotebookRunner, read_nb

    if isinstance(nb_file, NotebookRunner):
        nb = nb_file.nb
    else:
        nbr = read_nb(nb_file, kernel=False)
        nb = nbr.nb

    exp_class, writer_class = get_exporter("rst", add_writer=True)
    exporter = exp_class()
    writer = writer_class()
    unique_key = os.path.splitext(os.path.split(outfile)[-1])[0]
    source, meta = exporter.from_notebook_node(
        nb, resources=dict(unique_key=unique_key))

    name, ext = os.path.splitext(outfile)
    if ext != '.rst':
        raise ValueError("'{0}' should have extension '.rst'".format(outfile))
    writer.build_directory = os.path.dirname(outfile)
    writer.write(source, meta, notebook_name=name)

    # post_processing
    if post_process:
        from .post_process import post_process_rst_output
        try:
            post_process_rst_output(outfile, False, False,
                                    False, False, False, exc=exc)
        except HelpGenException as e:
            raise HelpGenException(  # pragma: no cover
                "Unable to postprocess notebook '{}' with writer '{}' and "
                "exporter '{}'".format(
                    getattr(nb_file, '_filename', nb_file),
                    type(writer), type(exporter))) from e

    res = [outfile]
    return res
