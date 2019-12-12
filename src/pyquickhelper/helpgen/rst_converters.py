"""
@file
@brief Helpers to convert docstring to various format.
"""
import re
import textwrap
import os
from io import StringIO
from docutils import core, languages
from docutils.io import StringInput, StringOutput
from .utils_sphinx_doc import migrating_doxygen_doc
from .helpgen_exceptions import HelpGenConvertError
from ..texthelper.texts_language import TITLES
from ..loghelper.flog import noLOG


def default_sphinx_options(fLOG=noLOG, **options):
    """
    Defines or overrides default options for :epkg:`Sphinx`, listed below.

    .. runpython::

        from pyquickhelper.helpgen.rst_converters import default_sphinx_options
        options = default_sphinx_options()
        for k, v in sorted(options.items()):
            print("{0} = {1}".format(k, v))

    .. versionchanged:: 1.8
        Disables :epkg:`latex` if not available on :epkg:`Windows`.
    """
    # delayed import to speed up time
    from .conf_path_tools import find_graphviz_dot, find_dvipng_path

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
        try:
            imgmath_latex, imgmath_dvipng, imgmath_dvisvgm = find_dvipng_path(
                exc=False)
            has_latex = True
        except FileNotFoundError:
            # miktex is not available,
            has_latex = False

        if has_latex:
            res['imgmath_latex'] = imgmath_latex
            res['imgmath_dvipng'] = imgmath_dvipng
            res['imgmath_dvisvgm'] = imgmath_dvisvgm

    for k, v in options.items():
        if k not in res:
            res[k] = v

    return res


def rst2html(s, fLOG=noLOG, writer="html", keep_warnings=False,
             directives=None, language="en",
             layout='docutils', document_name="<<string>>",
             external_docnames=None, filter_nodes=None,
             new_extensions=None, update_builder=None,
             ret_doctree=False, load_bokeh=False,
             destination=None, destination_path=None,
             **options):
    """
    Converts a string from :epkg:`RST`
    into :epkg:`HTML` format or transformed :epkg:`RST`.

    @param      s                   string to convert
    @param      fLOG                logging function (warnings will be logged)
    @param      writer              ``'html'`` for :epkg:`HTML` format,
                                    ``'rst'`` for :epkg:`RST` format,
                                    ``'md'`` for :epkg:`MD` format,
                                    ``'elatex'`` for :epkg:`latex` format,
                                    ``'doctree'`` to get the doctree, *writer* can also be a tuple
                                    for custom formats and must be like ``('buider_name', builder_class)``.
    @param      keep_warnings       keep_warnings in the final HTML
    @param      directives          new directives to add (see below)
    @param      language            language
    @param      layout              ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    @param      document_name       document name, not really important since the input is a string
    @param      external_docnames   if the string to parse makes references to other documents,
                                    if one is missing, an exception is raised.
    @param      filter_nodes        transforms the doctree before writing the results (layout must be 'sphinx'),
                                    the function takes a doctree as a single parameter
    @param      new_extensions      additional extension to setup
    @param      update_builder      update the builder after it is instantiated
    @param      ret_doctree         returns the doctree
    @param      load_bokeh          load :epkg:`bokeh` extensions,
                                    disabled by default as it takes a few seconds
    @param      destination         set a destination (requires for some extension)
    @param      destination_path    set a destination path (requires for some extension)
    @param      options             :epkg:`Sphinx` options see
                                    `Render math as images <http://www.sphinx-doc.org/en/stable/ext/math.html#module-sphinx.ext.imgmath>`_,
                                    a subset of options is used, see @see fn default_sphinx_options.
                                    By default, the theme (option *html_theme*) will ``'basic'``.
    @return                         HTML format

    *directives* is None or a list of 2 or 5-uple:

    * a directive name (mandatory)
    * a directive class: see `Sphinx Directive <http://sphinx-doc.org/extdev/tutorial.html>`_,
      see also @see cl RunPythonDirective as an example (mandatory)
    * a docutils node: see @see cl runpython_node as an example
    * two functions: see @see fn visit_runpython_node, @see fn depart_runpython_node as an example

    The parameter *layout* specify the kind of HTML you need.

    * ``'docutils'``: very simple :epkg:`HTML`, style is not included, recursive
      directives are not processed (recursive means they modify the doctree).
      The produced :epkg:`HTML` only includes the body (no :epkg:`HTML` header).
    * ``'sphinx'``: in memory :epkg:`sphinx`, the produced :epkg:`HTML` includes the header, it is also recursive
      as directives can modify the doctree.
    * ``'sphinx_body'``: same as ``'sphinx'`` but only the body is returned.

    If the writer is a tuple, it must be a 2-uple ``(builder_name, builder_class)``.
    However, the builder class must contain an attribute ``_writer_class`` with
    the associated writer. The builcer class must also implement a method
    ``iter_pages`` which enumerates all written pages:
    ``def iter_pages(self) -> Dict[str,str]`` where the key is the document name
    and the value is its content.

    .. exref::
        :title: How to test a Sphinx directive?

        The following code defines a simple directive
        definedbased on an existing one.
        It also defined what to do if a new node
        is inserted in the documentation.

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
                       runpythonthis_node, visit_node, depart_node) ]

            html = rst2html(content, writer="html", keep_warnings=True,
                            directives=tives)

        Unfortunately, this functionality is only tested on :epkg:`Python` 3.
        It might not work on :epkg:`Python` 2.7.
        The function produces files if the document contains latex
        converted into image.

    .. faqref::
       :title: How to get more about latex errors?
       :index: latex

        :epkg:`Sphinx` is not easy to use when it comes to debug latex expressions.
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

        :epkg:`Sphinx` calls :epkg:`latex` through command line.
        On :epkg:`Windows`, a command line window
        can annoyingly show up anytime a formula is compiled.
        The following can be added to hide it:

        ::

            startupinfo = STARTUPINFO()
            startupinfo.dwFlags |= STARTF_USESHOWWINDOW

        And ``, startupinfo=startupinfo`` must be added to lines ``p = Popen(...``.

    By default, the function now interprets :epkg:`Sphinx`
    directives and not only *docutils* ones.
    Parameter *directives* adds a directive
    before parsing the :epkg:`RST`.
    The function is more consistent.
    Format ``rst`` is available as well as
    custom builders.

    .. versionchanged:: 1.8
        New nodes are now optional in *directives*.
        Markdown format was added.
        Parameters *ret_doctree*, *load_bokeh* were added.
    """
    # delayed import to speed up time
    def _get_MockSphinxApp():
        from .sphinxm_mock_app import MockSphinxApp
        return MockSphinxApp
    MockSphinxApp = _get_MockSphinxApp()

    if 'html_theme' not in options:
        options['html_theme'] = 'basic'
    defopt = default_sphinx_options(**options)
    if "master_doc" not in defopt:
        defopt["master_doc"] = document_name
    if writer in ('latex', 'elatex') and 'latex_documents' not in defopt:
        latex_documents = [(document_name, ) * 5]
        defopt['latex_documents'] = latex_documents

    if writer in ["custom", "sphinx", "HTMLWriterWithCustomDirectives", "html"]:
        mockapp, writer, title_names = MockSphinxApp.create(
            "sphinx", directives, confoverrides=defopt,
            new_extensions=new_extensions,
            load_bokeh=load_bokeh, fLOG=fLOG,
            destination_path=destination_path)
        writer_name = "HTMLWriterWithCustomDirectives"
    elif writer in ("rst", "md", "latex", "elatex", 'text', 'doctree'):
        writer_name = writer
        mockapp, writer, title_names = MockSphinxApp.create(
            writer, directives, confoverrides=defopt,
            new_extensions=new_extensions,
            load_bokeh=load_bokeh, fLOG=fLOG,
            destination_path=destination_path)
    elif isinstance(writer, tuple):
        # We extect something like ("builder_name", builder_class)
        writer_name = writer
        mockapp, writer, title_names = MockSphinxApp.create(
            writer, directives, confoverrides=defopt,
            new_extensions=new_extensions,
            load_bokeh=load_bokeh, fLOG=fLOG,
            destination_path=destination_path)
    else:
        raise ValueError(
            "Unexpected writer '{0}', should be 'rst' or 'html' or 'md' or 'elatex' or 'text'.".format(writer))

    if writer is None and directives is not None and len(directives) > 0:
        raise NotImplementedError(
            "The writer must not be null if custom directives will be added, check the documentation of the fucntion.")

    # delayed import to speed up time
    from sphinx.environment import default_settings
    settings_overrides = default_settings.copy()
    settings_overrides["warning_stream"] = StringIO()
    settings_overrides["master_doc"] = document_name
    settings_overrides["source"] = document_name
    settings_overrides["contentsname"] = document_name
    settings_overrides.update({k: v[0]
                               for k, v in mockapp.new_options.items()})

    # next
    settings_overrides.update(defopt)
    config = mockapp.config
    config.blog_background = True
    config.blog_background_page = False
    config.sharepost = None

    if hasattr(writer, "add_configuration_options"):
        writer.add_configuration_options(mockapp.new_options)
    for k in {'outdir', 'imagedir', 'confdir', 'doctreedir'}:
        setattr(writer.builder, k, settings_overrides.get(k, ''))
    if destination_path is not None:
        writer.builder.outdir = destination_path
    if update_builder:
        update_builder(writer.builder)

    env = mockapp.env
    if env is None:
        raise ValueError("No environment was built.")

    env.temp_data["docname"] = document_name
    env.temp_data["source"] = document_name
    mockapp.builder.env.temp_data["docname"] = document_name
    mockapp.builder.env.temp_data["source"] = document_name
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

    _, pub = core.publish_programmatically(
        source=s, source_path=None, destination_path=destination_path, writer=writer,
        writer_name=writer_name, settings_overrides=settings_overrides,
        source_class=StringInput, destination_class=StringOutput,
        destination=destination, reader=None, reader_name='standalone',
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
        if isinstance(parts["whole"], list):
            # Not html.
            exp = "".join(parts["whole"])
        else:
            exp = re.sub(
                '(<div class="system-message">(.|\\n)*?</div>)', "", parts["whole"])
    else:
        if isinstance(parts["whole"], list):
            exp = "".join(parts["whole"])
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
                "/{0}.m.{1}".format(document_name, writer_name),
                document_name)
        if not hasattr(writer.builder, "iter_pages"):
            raise AttributeError(
                "Class '{0}' must have a method 'iter_pages' which returns a dictionary.".format(writer.builder))
        contents = []
        for k, v in writer.builder.iter_pages():
            pages.append(k)
            contents.append(v)
            if k in main:
                page = v
                break
        if page is None and len(contents) == 1:
            page = contents[0]
        if page is None:
            raise ValueError(
                "No page contents was produced, only '{0}'.".format(pages))
        if layout == "sphinx":
            if isinstance(page, str):
                return page
            else:
                return "\n".join(page)
        elif layout == "sphinx_body":
            lines = page.replace('</head>', '</head>\n').split("\n")
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
            res = "\n".join(keep)
            return res
        else:
            raise ValueError(
                "Unexpected value for layout '{0}'".format(layout))


def correct_indentation(text):
    """
    Tries to improve the indentation before running :epkg:`docutils`.

    @param      text        text to correct
    @return                 corrected text
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
                   layout='docutils', document_name="<<string>>",
                   filter_nodes=None, **options):
    """
    Converts a docstring into a :epkg:`HTML` format.

    @param      function_or_string      function, class, method or doctring
    @param      format                  output format (``'html'`` or '``rawhtml``')
    @param      fLOG                    logging function
    @param      writer                  ``'html'`` for :epkg:`HTML` format,
                                        ``'rst'`` for :epkg:`RST` format,
                                        ``'md'`` for :epkg:`MD` format
    @param      keep_warnings           keep_warnings in the final :epkg:`HTML`
    @param      directives              new directives to add (see below)
    @param      language                language
    @param      layout                  ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    @param      document_name           document_name for this string
    @param      filter_nodes            transform the doctree before writing the results
                                        (layout must be 'sphinx')
    @param      options                 Sphinx options see `Render math as images
                                        <http://www.sphinx-doc.org/en/stable/ext/math.html#module-sphinx.ext.imgmath>`_,
                                        a subset of options is used, see @see fn default_sphinx_options.
                                        By default, the theme (option *html_theme*) will ``'basic'``.
    @return                             (str) :epkg:`HTML` format or (IPython.core.display.HTML)

    .. exref::
        :title: Produce HTML documentation for a function or class

        The following code can display the dosstring in :epkg:`HTML` format
        to display it in a :epkg:`notebook`.

        ::

            from pyquickhelper.helpgen import docstring2html
            import sklearn.linear_model
            docstring2html(sklearn.linear_model.LogisticRegression)

    The output format is defined by:

    * ``'html'``: IPython :epkg:`HTML` object
    * ``'rawhtml'``: :epkg:`HTML` as text + style
    * ``'rst'``: :epkg:`rst`
    * ``'text'``: raw text

    .. versionchanged:: 1.8
        Markdown format was added.
    """
    if not isinstance(function_or_string, str):
        doc = function_or_string.__doc__
    else:
        doc = function_or_string

    if format == "text":
        return doc

    if doc is None:
        return ""

    javadoc = migrating_doxygen_doc(doc, "None", log=False)[1]
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
                        document_name=document_name,
                        layout=layout, **options)
    except Exception:
        # we check the indentation
        ded = correct_indentation(ded)
        try:
            html = rst2html(ded, fLOG=fLOG, writer=writer,
                            keep_warnings=keep_warnings, directives=directives,
                            language=language, filter_nodes=filter_nodes,
                            document_name=document_name,
                            layout=layout, **options)
        except Exception as e:
            lines = ded.split("\n")
            lines = ["%04d  %s" % (i + 1, _.strip("\n\r"))
                     for i, _ in enumerate(lines)]
            raise HelpGenConvertError(
                "Unable to process:\n{0}".format("\n".join(lines))) from e

    ret_doctree = writer == "doctree"
    if ret_doctree:
        writer = "doctree"

    if writer in ('doctree', 'rst', 'md'):
        return html

    if format == "html":
        from IPython.core.display import HTML
        return HTML(html)
    elif format in ("rawhtml", 'rst', 'md', 'doctree'):
        return html
    else:
        raise ValueError(
            "Unexpected format: '" + format + "', should be html, rawhtml, text, rst, md, doctree.")


def rst2rst_folder(rststring, folder, document_name="index", **options):
    """
    Converts a :epkg:`RST` string into simplified :epkg:`RST`.

    @param      rststring       :epkg:`rst` string
    @param      folder          the builder needs to write the resuts in a
                                folder defined by this parameter
    @param      document_name   main document
    @param      options         additional options (same as *conf.py*)
    @return                     converted string
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(folder)

    new_options = {}
    new_options.update(options)

    def update_builder(builder):
        builder.outdir = folder

    rst = rst2html(rststring, writer="rst", document_name="example",
                   update_builder=update_builder, layout="sphinx",
                   **new_options)
    return rst
