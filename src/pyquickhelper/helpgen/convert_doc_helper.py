"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""
import sys
import re
import textwrap
from docutils import core
# from docutils import nodes
from docutils.parsers.rst import directives as doc_directives

from .utils_sphinx_doc import migrating_doxygen_doc
from ..loghelper.flog import noLOG
from . helpgen_exceptions import HelpGenConvertError
# from .sphinx_blog_extension import blogpostagg_node, blogpost_node
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_runpython_extension import RunPythonDirective
# from .sphinx_runpython_extension import runpython_node
from .convert_doc_sphinx_helper import HTMLWriterWithCustomDirectives

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


# -- HELP BEGIN EXCLUDE --

from .utils_sphinx_doc import private_migrating_doxygen_doc

# -- HELP END EXCLUDE --


def rst2html(s, fLOG=noLOG, writer="sphinx", keep_warnings=False,
             directives=None):
    """
    converts a string into HTML format

    @param      s               string to converts
    @param      fLOG            logging function (warnings will be logged)
    @param      writer          *None* or an instance such as ``HTMLWriterWithCustomDirectives()`` or
                                ``custom`` or ``sphinx``
    @param      keep_warnings   keep_warnings in the final HTML
    @param      directives      new directives to add (see below)
    @return                     HTML format

    *directives* is None or a list of 5-uple:

    * a directive name
    * a directive class: see `Sphinx Directive <http://sphinx-doc.org/extdev/tutorial.html>`_, see also @see cl RunPythonDirective as an example
    * a docutils node: see @see cl runpython_node as an example
    * two functions: see @see fn visit_runpython_node, @see fn depart_runpython_node as an example

    @example(How to test a Sphinx directive?)

    The following code defines a simple directive defined based on an existing one.
    It also defined what to do if a new node is inserted in the documentation.

    ::

        from docutils import nodes
        from pyquickhelper import rst2html

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_node(self, node):
            self.body.append("<p><b>visit_node</b></p>")
        def depart_node(self, node):
            self.body.append("<p><b>depart_node</b></p>")

        content = '''
                    test a directive
                    ================

                    .. runpythonthis::

                        print("this code shoud appear" + "___")
                    '''.replace("                    ", "")
                    # to remove spaces at the beginning of the line

        tives = [ ("runpythonthis", RunPythonThisDirective,
                  runpythonthis_node,
                  visit_node, depart_node) ]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)


    @endexample

    .. versionadded:: 1.0

    .. versionchanged:: 1.3
        Parameters *writer*, *keep_warnings* were added to specifiy a custom writer
        and to keep the warnings. By default, the function now interprets *Sphinx*
        directives and not only *docutils* ones.
        Parameter *directives* was added to add a directive before parsing the RST.
    """

    if writer in ["custom", "sphinx"]:
        doc_directives.register_directive("blogpost", BlogPostDirective)
        doc_directives.register_directive("blogpostagg", BlogPostDirectiveAgg)
        doc_directives.register_directive("runpython", RunPythonDirective)
        writer = HTMLWriterWithCustomDirectives()
        writer_name = 'pseudoxml'
        # not necessary
        #for cl in [blogpost_node, blogpostagg_node, runpython_node]:
        #    nodes._add_node_class_names([cl.__name__])
    else:
        writer_name = 'html'

    if writer is None and directives is not None and len(directives) > 0:
        raise NotImplementedError(
            "the writer must not be null if custom directives will be added, check the documentation of the fucntion")

    if directives is not None:
        for tu in directives:
            if len(tu) != 5:
                raise ValueError(
                    "directives is a list of tuple with 5 elements, check the documentation")
            name, cl, node, f1, f2 = tu
            doc_directives.register_directive(name, cl)
            # not necessary
            #nodes._add_node_class_names([node.__name__])
            writer.connect_directive_node(node.__name__, f1, f2)

    settings_overrides = {'output_encoding': 'unicode',
                          'doctitle_xform': True,
                          'initial_header_level': 2,
                          'warning_stream': StringIO(),
                          'input_encoding': 'utf8',
                          'out_blogpostlist': [],
                          'out_runpythonlist': [],
                          'blog_background': False,
                          }

    parts = core.publish_parts(source=s, source_path=None,
                               destination_path=None, writer=writer,
                               writer_name=writer_name,
                               settings_overrides=settings_overrides)

    fLOG(settings_overrides["warning_stream"].getvalue())

    if not keep_warnings:
        exp = re.sub(
            '(<div class="system-message">(.|\\n)*?</div>)', "", parts["whole"])
    else:
        exp = parts["whole"]

    return exp


def correct_indentation(text):
    """
    tries to improve the indentation before running docutil

    @param      text        text to correct
    @return                 corrected text

    .. versionadded:: 1.0
    """
    title = {}
    rows = text.split("\n")
    for row in rows:
        row = row.replace("\t", "    ")
        cr = row.lstrip()
        ind = len(row) - len(cr)

        tit = cr.strip("\r\n\t ")
        if len(tit) > 0 and tit[0] in "-+=*^" and tit == tit[0] * len(tit):
            title[ind] = title.get(ind, 0) + 1

    mint = min(title.keys())
    if mint > 0:
        newrows = []
        for row in rows:
            i = 0
            while i < len(row) and row[i] == ' ':
                i += 1

            rem = min(i, mint)
            if rem > 0:
                newrows.append(row[rem:])
            else:
                newrows.append(row)

        return "\n".join(newrows)
    else:
        return text


def docstring2html(function_or_string, format="html", fLOG=noLOG, writer="sphinx"):
    """
    converts a docstring into a HTML format

    @param      function_or_string      function, class, method or doctring
    @param      format                  output format
    @param      fLOG                    logging function
    @param      writer                  *None* or an instance such as ``HTMLWriterWithCustomDirectives()``
    @return                             (str) HTML format or (IPython.core.display.HTML)

    @example(Produce HTML documentation for a function or class)

    The following code can display the dosstring in HTML format
    to display it in a notebook.

    @code
    from pyquickhelper import docstring2html
    import sklearn.linear_model
    docstring2html(sklearn.linear_model.LogisticRegression)
    @endcode

    @endexample

    The output format is defined by:

        * html: IPython HTML object
        * rawhtml: HTML as text + style
        * rst: rst
        * text: raw text

    .. versionadded:: 1.0

    .. versionchanged:: 1.3
        Parameter *writer* was added to specifiy a custom writer.
    """
    if not isinstance(function_or_string, str):
        doc = function_or_string.__doc__
    else:
        doc = function_or_string

    if format == "text":
        return doc

    stats, javadoc = migrating_doxygen_doc(doc, "None", log=False)
    rows = javadoc.split("\n")
    rst = private_migrating_doxygen_doc(
        rows, index_first_line=0, filename="None")
    rst = "\n".join(rst)
    ded = textwrap.dedent(rst)

    if format == "rst":
        return ded

    try:
        html = rst2html(ded, fLOG=fLOG, writer=writer)
    except Exception:
        # we check the indentation
        ded = correct_indentation(ded)
        try:
            html = rst2html(ded, fLOG=fLOG, writer=writer)
        except Exception as e:
            lines = ded.split("\n")
            lines = ["%04d  %s" % (i + 1, _.strip("\n\r"))
                     for i, _ in enumerate(lines)]
            raise HelpGenConvertError(
                "unable to process:\n{0}".format("\n".join(lines))) from e

    if format == "html":
        from IPython.core.display import HTML
        return HTML(html)
    elif format == "rawhtml":
        return html
    else:
        raise ValueError(
            "unexected format: " + format + ", should be html, rawhtml, text, rst")
