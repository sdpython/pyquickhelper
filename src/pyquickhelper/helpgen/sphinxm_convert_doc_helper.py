"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""
from .utils_sphinx_doc import migrating_doxygen_doc
from ..texthelper.texts_language import TITLES
from ..loghelper.flog import noLOG
from . helpgen_exceptions import HelpGenConvertError
from .conf_path_tools import find_graphviz_dot, find_latex_path
from .sphinxm_mock_app import MockSphinxApp

import sys
import re
import textwrap
import os
from docutils import core, languages
from docutils.io import StringInput, StringOutput
from sphinx.environment import default_settings
from sphinx.util.logging import getLogger


if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


def default_sphinx_options(fLOG=noLOG, **options):
    """
    Define or override default options for Sphinx, listed below.

    .. runpython::

        from pyquickhelper.helpgen.sphinxm_convert_doc_helper import default_sphinx_options
        options = default_sphinx_options()
        for k, v in sorted(options.items()):
            print("{0} = {1}".format(k, v))

    .. versionadded:: 1.4
    """
    res = {  # 'output_encoding': options.get('output_encoding', 'unicode'),
        # 'doctitle_xform': options.get('doctitle_xform', True),
        # 'initial_header_level': options.get('initial_header_level', 2),
        # 'input_encoding': options.get('input_encoding', 'utf-8-sig'),
        'blog_background': options.get('blog_background', False),
        'sharepost': options.get('sharepost', None),
        'todoext_link_only': options.get('todoext_link_only', False),
        'mathdef_link_only': options.get('mathdef_link_only', True),
        'blocref_link_only': options.get('blocref_link_only', False),
        'faqref_link_only': options.get('faqref_link_only', False),
        'nbref_link_only': options.get('nbref_link_only', False),
        'todo_link_only': options.get('todo_link_only', False),
        'language': options.get('language', 'en'),
        # 'outdir': options.get('outdir', '.'),
        # 'imagedir': options.get('imagedir', '.'),
        # 'confdir': options.get('confdir', '.'),
        # 'doctreedir': options.get('doctreedir', '.'),
        'math_number_all': options.get('math_number_all', False),
        # graphviz
        'graphviz_output_format': options.get('graphviz_output_format', 'png'),
        'graphviz_dot': options.get('graphviz_dot', find_graphviz_dot(exc=False)),
        # latex
        'imgmath_image_format': options.get('imgmath_image_format', 'png'),
        # containers
        'out_blogpostlist': [],
        'out_runpythonlist': [],
        # 'warning_stream': StringIO(),
    }

    if res['imgmath_image_format'] == 'png':
        res['imgmath_latex'] = options.get(
            'imgmath_latex', find_latex_path(exc=False))
        res['imgmath_dvipng'] = options.get(
            'imgmath_dvipng', os.path.join(res['imgmath_latex'], "dvipng.exe") if res['imgmath_latex'] is not None else None)
        if res['imgmath_dvipng'] is not None and not os.path.exists(res['imgmath_dvipng']):
            logger = getLogger("default_sphinx_options")
            logger.warning("[warning], unable to find: " +
                           str(res['imgmath_dvipng']))
            # we pass as latex is not necessarily installed or needed
        env_path = os.environ.get("PATH", "")
        sep = ";" if sys.platform.startswith("win") else ":"
        if res['imgmath_latex'] is not None and res['imgmath_latex'] not in env_path:
            if len(env_path) > 0:
                env_path += sep
            env_path += res['imgmath_latex']

        if res['imgmath_latex'] is not None:
            if sys.platform.startswith("win"):
                res['imgmath_latex'] = os.path.join(
                    res['imgmath_latex'], "latex.exe")
            else:
                res['imgmath_latex'] = os.path.join(
                    res['imgmath_latex'], "latex")

    for k, v in options.items():
        if k not in res:
            res[k] = v

    return res


def rst2html(s, fLOG=noLOG, writer="html", keep_warnings=False,
             directives=None, language="en",
             layout='docutils', document_name="<<string>>",
             external_docnames=None, filter_nodes=None,
             new_extensions=None, update_builder=None, **options):
    """
    Converts a string into HTML format.

    @param      s                   string to converts
    @param      fLOG                logging function (warnings will be logged)
    @param      writer              ``'html'`` for HTML format, ``'rst'`` for RST format,
                                    ``'doctree'`` to get the doctree, *writer* can also be a tuple
                                    for custom formats and must be like ``('buider_name', builder_class)``.
    @param      keep_warnings       keep_warnings in the final HTML
    @param      directives          new directives to add (see below)
    @param      language            language
    @param      layout              ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    @param      document_name       document name, not really important since the input is a string
    @param      options             Sphinx options see `Render math as images <http://www.sphinx-doc.org/en/stable/ext/math.html#module-sphinx.ext.imgmath>`_,
                                    a subset of options is used, see @see fn default_sphinx_options.
                                    By default, the theme (option *html_theme*) will ``'basic'``.
    @param      external_docnames   if the string to parse makes references to other documents,
                                    if one is missing, an exception is raised.
    @param      filter_nodes        transforms the doctree before writing the results (layout must be 'sphinx'),
                                    the function takes a doctree as a single parameter
    @param      new_extensions      additional extension to setup
    @param      update_builder      update the builder after it is instantiated
    @return                         HTML format

    *directives* is None or a list of 5-uple:

    * a directive name
    * a directive class: see `Sphinx Directive <http://sphinx-doc.org/extdev/tutorial.html>`_, see also @see cl RunPythonDirective as an example
    * a docutils node: see @see cl runpython_node as an example
    * two functions: see @see fn visit_runpython_node, @see fn depart_runpython_node as an example

    The parameter *layout* specify the kind of HTML you need.

    * ``'docutils'``: very simple HTML, style is not included, recursive
      directives are not processed (recursive means they modify the doctree).
      The produced HTML only includes the body (no HTML header).
    * ``'sphinx'``: in memory sphinx, the produced HTML includes the header, it is also recursive
      as directives can modify the doctree.
    * ``'sphinx_body'``: same as ``'sphinx'`` but only the body is returned.

    if the writer is a tuple, it must be a 2-uple ``(builder_name, builder_class)``.
    However, the builder class must contain an attribute ``_writer_class`` with
    the associated writer. The builcer class must also implement a method
    ``iter_pages`` which enumerates all written pages:
    ``def iter_pages(self) -> Dict[str,str]`` where the key is the document name
    and the value is its content.

    .. exref::
        :title: How to test a Sphinx directive?

        The following code defines a simple directive defined based on an existing one.
        It also defined what to do if a new node is inserted in the documentation.

        ::

            from docutils import nodes
            from pyquickhelper.helpgen import rst2html

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
                            writer="html", keep_warnings=True,
                            directives=tives)

        Unfortunately, this functionality is only tested on Python 3.
        It might only work on Python 2.7.
        The function produces files if the document contains latex
        converted into image.

    .. faqref::
       :title: How to get more about latex errors?
       :index: latex

        Sphinx is not easy to use when it comes to debug latex expressions.
        I did not find an easy way to read the error returned by latex about
        a missing bracket or an unknown command. I finally added a short piece
        of code in ``sphinx.ext.imgmath.py`` just after the call to
        the executable indicated by *imgmath_latex*

        ::

            if b'...' in stdout or b'LaTeX Error' in stdout:
                print(self.builder.config.imgmath_latex_preamble)
                print(p.returncode)
                print("################")
                print(latex)
                print("..........")
                print(stdout.decode("ascii").replace("\\r", ""))
                print("-----")
                print(stderr)

        It displays the output if an error happened.

    .. faqref::
        :title: How to hide command line window while compiling latex?
        :lid: command line window

        Sphinx calls latex through command line. On Windows, a command line window
        can annoyingly show up anytime a formula is compile. The following
        line can be added to hide it:

        ::

            startupinfo = STARTUPINFO()
            startupinfo.dwFlags |= STARTF_USESHOWWINDOW

        And ``, startupinfo=startupinfo`` must be added to lines ``p = Popen(...``.

    .. versionadded:: 1.0

    .. versionchanged:: 1.3
        Parameters *writer*, *keep_warnings* were added to specifiy a custom writer
        and to keep the warnings. By default, the function now interprets *Sphinx*
        directives and not only *docutils* ones.
        Parameter *directives* was added to add a directive before parsing the RST.

    .. versionchanged:: 1.4
        Add directives *todoext*, *todo*, *mathdef*, *blocref*, *faqref*, *nbref*, *exref*.
        Parameter *language* was added.
        Add directives *graphviz*, *math*.
        Parse more extensive Sphinx syntax.

    .. versionchanged:: 1.5
        More logging is done, the function is more consistent.
        Parameters *layout*, *document_name*, *external_docnames*, *filter_nodes*, *update_builder*,
        *new_extensions* were added. Format ``rst`` was added. Custom builders is supported.
    """
    if 'html_theme' not in options:
        options['html_theme'] = 'basic'
    defopt = default_sphinx_options(**options)
    if "master_doc" not in defopt:
        defopt["master_doc"] = document_name

    ret_doctree = writer == "doctree"
    if ret_doctree:
        writer = "rst"

    if writer in ["custom", "sphinx", "HTMLWriterWithCustomDirectives", "html"]:
        mockapp, writer, title_names = MockSphinxApp.create("sphinx", directives,
                                                            confoverrides=defopt, new_extensions=new_extensions, fLOG=fLOG)
        writer_name = "HTMLWriterWithCustomDirectives"
    elif writer == "rst":
        writer_name = writer
        mockapp, writer, title_names = MockSphinxApp.create(writer, directives,
                                                            confoverrides=defopt, new_extensions=new_extensions, fLOG=fLOG)
    elif isinstance(writer, tuple):
        # We extect something like ("builder_name", builder_class)
        writer_name = writer
        mockapp, writer, title_names = MockSphinxApp.create(writer, directives,
                                                            confoverrides=defopt, new_extensions=new_extensions, fLOG=fLOG)
    else:
        raise ValueError(
            "Unexpected writer '{0}', should be 'rst' or 'html'.".format(writer))

    if writer is None and directives is not None and len(directives) > 0:
        raise NotImplementedError(
            "The writer must not be null if custom directives will be added, check the documentation of the fucntion.")

    settings_overrides = default_settings.copy()
    settings_overrides["warning_stream"] = StringIO()
    settings_overrides["master_doc"] = document_name
    settings_overrides.update({k: v[0]
                               for k, v in mockapp.new_options.items()})

    # next
    settings_overrides.update(defopt)

    config = mockapp.config
    config.blog_background = False
    config.sharepost = None

    if hasattr(writer, "add_configuration_options"):
        writer.add_configuration_options(mockapp.new_options)
    for k in {'outdir', 'imagedir', 'confdir', 'doctreedir'}:
        setattr(writer.builder, k, settings_overrides.get(k, ''))
    if update_builder:
        update_builder(writer.builder)

    env = mockapp.env
    if env is None:
        raise ValueError("No environment was built.")

    env.temp_data["docname"] = document_name
    mockapp.builder.env.temp_data["docname"] = document_name
    settings_overrides["env"] = env

    lang = languages.get_language(language)
    for name in title_names:
        if name not in lang.labels:
            lang.labels[name] = TITLES[language][name]

    for k, v in sorted(settings_overrides.items()):
        fLOG("[rst2html] {0}={1}{2}".format(
            k, v, " --- added" if hasattr(config, k) else ""))
    for k, v in sorted(settings_overrides.items()):
        if hasattr(writer.builder.config, k) and writer.builder.config[k] != v:
            writer.builder.config[k] = v

    output, pub = core.publish_programmatically(source=s, source_path=None, destination_path=None, writer=writer,
                                                writer_name=writer_name, settings_overrides=settings_overrides,
                                                source_class=StringInput, destination_class=StringOutput,
                                                destination=None, reader=None, reader_name='standalone',
                                                parser=None, parser_name='restructuredtext', settings=None,
                                                settings_spec=None, config_section=None, enable_exit_status=False)

    doctree = pub.document

    if filter_nodes is not None:
        if layout == "docutils" and writer != "doctree":
            raise ValueError(
                "filter_nodes is not None, layout must not be 'docutils'")
        filter_nodes(doctree)

    mockapp.finalize(doctree, external_docnames=external_docnames)
    parts = pub.writer.parts

    if not keep_warnings:
        exp = re.sub(
            '(<div class="system-message">(.|\\n)*?</div>)', "", parts["whole"])
    else:
        exp = parts["whole"]

    if ret_doctree:
        return doctree

    if layout == "docutils":
        return exp
    else:
        page = None
        pages = []
        main = ("/{0}.m.html".format(document_name),
                "/{0}.m.{1}".format(document_name, writer_name)),
        if not hasattr(writer.builder, "iter_pages"):
            raise AttributeError(
                "Class '{0}' must have a method 'iter_pages' which returns a dictionary.".format(writer.builder))
        contents = []
        for k, v in writer.builder.iter_pages():
            pages.append(k)
            contents.append(v)
            if k == main:
                page = v
                break
        if page is None and len(contents) == 1:
            page = contents[0]
        if page is None:
            raise ValueError(
                "No page contents was produced only '{0}'.".format(", ".join(pages)))
        if layout == "sphinx":
            return page
        elif layout == "sphinx_body":
            lines = page.split("\n")
            keep = []
            begin = False
            for line in lines:
                s = line.strip(" \n\r")
                if s == "</body>":
                    begin = False
                if begin:
                    keep.append(line)
                if s == "<body>":
                    begin = True
            return "\n".join(keep)
        else:
            raise ValueError(
                "unexpected value for layout '{0}'".format(layout))


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

    if len(title) > 0:
        mint = min(title.keys())
    else:
        mint = 0
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


def docstring2html(function_or_string, format="html", fLOG=noLOG, writer="html",
                   keep_warnings=False, directives=None, language="en",
                   layout='docutils', document_name="<string>",
                   filter_nodes=None, **options):
    """
    Converts a docstring into a HTML format.

    @param      function_or_string      function, class, method or doctring
    @param      format                  output format (``'html'`` or '``rawhtml``')
    @param      fLOG                    logging function
    @param      writer                  ``'html'`` for HTML format or ``'rst'`` for RST format
    @param      keep_warnings           keep_warnings in the final HTML
    @param      directives              new directives to add (see below)
    @param      language                language
    @param      layout                  ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    @param      document_name           document_name for this string
    @param      filter_nodes            transform the doctree before writing the results (layout must be 'sphinx')
    @param      options                 Sphinx options see `Render math as images <http://www.sphinx-doc.org/en/stable/ext/math.html#module-sphinx.ext.imgmath>`_,
                                        a subset of options is used, see @see fn default_sphinx_options.
                                        By default, the theme (option *html_theme*) will ``'basic'``.
    @return                             (str) HTML format or (IPython.core.display.HTML)

    .. exref::
        :title: Produce HTML documentation for a function or class

        The following code can display the dosstring in HTML format
        to display it in a notebook.

        ::

            from pyquickhelper.helpgen import docstring2html
            import sklearn.linear_model
            docstring2html(sklearn.linear_model.LogisticRegression)

    The output format is defined by:

        * html: IPython HTML object
        * rawhtml: HTML as text + style
        * rst: rst
        * text: raw text

    .. versionadded:: 1.0

    .. versionchanged:: 1.3
        Parameter *writer* was added to specifiy a custom writer.

    .. versionchanged:: 1.4
        Does not crash anymore when the documentation is None.

    .. versionchanged:: 1.5
        Changed the signature to be like @see fn rst2html.
        Format ``rst`` was added.
    """
    if not isinstance(function_or_string, str):
        doc = function_or_string.__doc__
    else:
        doc = function_or_string

    if format == "text":
        return doc

    if doc is None:
        return ""

    stats, javadoc = migrating_doxygen_doc(doc, "None", log=False)
    rows = javadoc.split("\n")
    from .utils_sphinx_doc import _private_migrating_doxygen_doc
    rst = _private_migrating_doxygen_doc(
        rows, index_first_line=0, filename="None")
    rst = "\n".join(rst)
    ded = textwrap.dedent(rst)

    try:
        html = rst2html(ded, fLOG=fLOG, writer=writer,
                        keep_warnings=keep_warnings, directives=directives,
                        language=language, filter_nodes=filter_nodes,
                        layout=layout, **options)
    except Exception:
        # we check the indentation
        ded = correct_indentation(ded)
        try:
            html = rst2html(ded, fLOG=fLOG, writer=writer,
                            keep_warnings=keep_warnings, directives=directives,
                            language=language, filter_nodes=filter_nodes,
                            layout=layout, **options)
        except Exception as e:
            lines = ded.split("\n")
            lines = ["%04d  %s" % (i + 1, _.strip("\n\r"))
                     for i, _ in enumerate(lines)]
            raise HelpGenConvertError(
                "unable to process:\n{0}".format("\n".join(lines))) from e

    if writer in ('doctree', 'rst'):
        return html

    if format == "html":
        from IPython.core.display import HTML
        return HTML(html)
    elif format in ("rawhtml", 'rst'):
        return html
    else:
        raise ValueError(
            "Unexpected format: '" + format + "', should be html, rawhtml, text, rst.")
