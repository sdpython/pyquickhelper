"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""
import logging
from docutils import nodes
from docutils.parsers.rst.directives import directive as rst_directive
from docutils.parsers.rst import directives as doc_directives, roles as doc_roles
from sphinx.config import Config
from sphinx.ext import autodoc
from sphinx import __display_version__ as sphinx__display_version__
from sphinx.application import VersionRequirementError
from sphinx.util.docutils import is_html5_writer_available
from sphinx.errors import ExtensionError
from .sphinxm_convert_doc_sphinx_helper import HTMLWriterWithCustomDirectives, _CustomSphinx
from .sphinxm_convert_doc_sphinx_helper import MDWriterWithCustomDirectives, RSTWriterWithCustomDirectives
from ..sphinxext import get_default_extensions


class MockSphinxApp:
    """
    Mocks :epkg:`Sphinx` application.
    In memory :epkg:`Sphinx` application.
    """

    def __init__(self, writer, app, confoverrides, new_extensions=None):
        """
        @param      writer          see static method create
        @param      app             see static method create
        @param      confoverrides   default options
        @param      new_extensions  additional extensions

        .. versionchanged:: 1.5
            Parameters *confoverrides*, *new_extensions* were added.
        """
        if confoverrides is None:
            confoverrides = {}
        self.app = app
        self.env = app.env
        self.new_options = {}
        self.writer = writer
        self.mapping = {"<class 'sphinx.ext.todo.todo_node'>": "todo",
                        "<class 'sphinx.ext.graphviz.graphviz'>": "graphviz",
                        "<class 'sphinx.ext.mathbase.math'>": "math",
                        "<class 'sphinx.ext.mathbase.displaymath'>": "displaymath",
                        "<class 'sphinx.ext.mathbase.eqref'>": "eqref",
                        "<class 'matplotlib.sphinxext.only_directives.html_only'>": "only",
                        "<class 'matplotlib.sphinxext.only_directives.latex_only'>": "only",
                        }
        self.mapping_connect = {}
        self.config = Config(None, None, overrides=confoverrides, tags=None)
        self.confdir = "."
        self.doctreedir = "."
        self.srcdir = "."
        self.builder = writer.builder
        self._new_extensions = new_extensions
        # self.domains = {}
        # self._events = {}
        # self.events = EventManager()
        # self.registry = SphinxComponentRegistry()
        # self.extensions = {}
        # self._setting_up_extension = ['?']
        # setup_rst(self)
        # setup_rst(app)

    def add_directive(self, name, cl, *args, **options):
        """
        See :epkg:`class Sphinx`.
        """
        doc_directives.register_directive(name, cl)
        self.mapping[str(cl)] = name
        self.app.add_directive(name, cl, *args, **options)
        self.writer.app.add_directive(name, cl, *args, **options)

    def add_role(self, name, cl):
        """
        See :epkg:`class Sphinx`.
        """
        doc_roles.register_canonical_role(name, cl)
        self.mapping[str(cl)] = name
        self.app.add_role(name, cl)
        self.writer.app.add_role(name, cl)

    def add_builder(self, name, cl):
        """
        See :epkg:`class Sphinx`.
        """
        self.mapping[str(cl)] = name
        self.app.add_builder(name, cl)
        self.writer.app.add_builder(name, cl)

    def add_mapping(self, name, cl):
        """
        See :epkg:`class Sphinx`.
        """
        self.mapping[str(cl)] = name

    def add_config_value(self, name, default, rebuild, types=()):
        """
        See :epkg:`class Sphinx`.
        """
        if name in self.config.values:
            # We do not add it a second time.
            return
        if rebuild in (False, True):
            rebuild = 'env' if rebuild else ''
        self.new_options[name] = (default, rebuild, types)
        self.config.values[name] = (default, rebuild, types)

    def get_default_values(self):
        """
        See :epkg:`class Sphinx`.
        """
        return {k: v[0] for k, v in self.new_options.items()}

    def add_node(self, node, **kwds):
        """
        See :epkg:`class Sphinx`.
        """
        # type: (nodes.Node, Any) -> None
        nodes._add_node_class_names([node.__name__])
        for key, val in kwds.items():
            if not isinstance(val, tuple):
                continue
            visit, depart = val
            translator = self.writer.app.registry.translators.get(key)
            translators = []
            if translator is not None:
                translators.append(translator)
            elif key == 'html':
                from sphinx.writers.html import HTMLTranslator
                translators.append(HTMLTranslator)
                if is_html5_writer_available():
                    from sphinx.writers.html5 import HTML5Translator
                    translators.append(HTML5Translator)
            elif key == 'latex':
                try:
                    from sphinx.writers.latex import LaTeXTranslator
                except ImportError:
                    # Since sphinx 1.7.3 (circular reference).
                    import sphinx.builders.latex.transforms
                    from sphinx.writers.latex import LaTeXTranslator
                translators.append(LaTeXTranslator)
            elif key == 'text':
                from sphinx.writers.text import TextTranslator
                translators.append(TextTranslator)
            elif key == 'man':
                from sphinx.writers.manpage import ManualPageTranslator
                translators.append(ManualPageTranslator)
            elif key == 'texinfo':
                from sphinx.writers.texinfo import TexinfoTranslator
                translators.append(TexinfoTranslator)

            for translator in translators:
                setattr(translator, 'visit_' + node.__name__, visit)
                if depart:
                    setattr(translator, 'depart_' +
                            node.__name__, depart)

    def finalize(self, doctree, external_docnames=None):
        """
        Finalize the documentation after it was parsed.

        @param      doctree             doctree (or pub.document), available after publication
        @param      external_docnames   other docnames the doctree references
        """
        self.app.finalize(doctree, external_docnames=external_docnames)

    def setup_extension(self, extname):
        """
        See :epkg:`class Sphinx`.
        """
        self.app.setup_extension(extname)

    def emit(self, event, *args):
        """
        See :epkg:`class Sphinx`.
        """
        return self.app.emit(event, *args)

    def emit_firstresult(self, event, *args):
        """
        See :epkg:`class Sphinx`.
        """
        return self.app.events.emit_firstresult(event, self, *args)

    def add_autodocumenter(self, cls):
        """
        See :epkg:`class Sphinx`.
        """
        autodoc.add_documenter(cls)
        self.app.add_directive('auto' + cls.objtype, autodoc.AutoDirective)

    def connect(self, node, func):
        """
        See :epkg:`class Sphinx`.
        """
        self.mapping_connect[node] = func
        self.app.connect(node, func)
        self.writer.app.connect(node, func)

    def add_domain(self, domain):
        """
        See :epkg:`class Sphinx`.
        """
        if domain.name in self.app.domains:
            # We do not register it a second time.
            return
        self.app.domains[domain.name] = domain

    def require_sphinx(self, version):
        # type: (unicode) -> None
        # check the Sphinx version if requested
        if version > sphinx__display_version__[:3]:
            raise VersionRequirementError(version)

    def add_event(self, name):
        """
        See :epkg:`class Sphinx`.
        """
        if name in self.app._events:
            # We do not raise an exception if already present.
            return
        self.app._events[name] = ''

    def add_env_collector(self, collector):
        """
        See :epkg:`class Sphinx`.
        """
        self.app.add_env_collector(collector)

    def add_javascript(self, jsfile):
        """
        See :epkg:`class Sphinx`.
        """
        self.app.add_javascript(jsfile)

    def add_stylesheet(self, css):
        """
        See :epkg:`class Sphinx`.
        """
        self.app.add_stylesheet(css)

    def add_source_parser(self, ext, parser, exc=False):
        """
        Registers a parser for a specific file extension.

        @param      ext     file extension
        @param      parser  parser
        @param      exc     raises an exception if already done

        Example:

        ::

            app.add_source_parser(self, ext, parser)
        """
        try:
            self.app.add_source_parser(ext, parser)
        except ExtensionError as e:
            if exc:
                raise
            else:
                logger = logging.getLogger("MockSphinxApp")
                logger.warning('[MockSphinxApp] {0}'.format(e))

    def disconnect_env_collector(self, clname):
        """
        Disconnects a collector given its class name.

        @param      cl      name
        @return             found collector
        """
        self.app.disconnect_env_collector(clname)

    @staticmethod
    def create(writer="html", directives=None, confoverrides=None, new_extensions=None, fLOG=None):
        """
        Creates a MockApp for :epkg:`Sphinx`.

        @param      writer          ``'sphinx'`` is the only allowed value
        @param      directives      new directives to add (see below)
        @param      confoverrides   initial options
        @param      new_extensions  additional extensions to setup
        @param      fLOG            logging function
        @return                     mockapp, writer, list of added nodes

        *directives* is None or a list of 2 or 5-uple:

        * a directive name (mandatory)
        * a directive class: see `Sphinx Directive <http://sphinx-doc.org/extdev/tutorial.html>`_,
          see also @see cl RunPythonDirective as an example (mandatory)
        * a docutils node: see @see cl runpython_node as an example
        * two functions: see @see fn visit_runpython_node,
          @see fn depart_runpython_node as an example

        .. versionchanged:: 1.5
            Parameters *fLOG*, *confoverrides*, *new_extensions* were added.
            The class supports more extensions.

        .. versionchanged:: 1.8
            New nodes are now optional in *directives*.
        """
        if confoverrides is None:
            confoverrides = {}
        if "extensions" not in confoverrides:
            confoverrides["extensions"] = get_default_extensions()

        if writer in ("sphinx", "custom", "HTMLWriterWithCustomDirectives", "html"):
            app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                buildername='memoryhtml', confoverrides=confoverrides,
                                new_extensions=new_extensions)
            writer = HTMLWriterWithCustomDirectives(
                builder=app.builder, app=app)
            mockapp = MockSphinxApp(writer, writer.app, confoverrides=confoverrides,
                                    new_extensions=new_extensions)
        elif writer == "rst":
            app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                buildername='memoryrst', confoverrides=confoverrides,
                                new_extensions=new_extensions)
            writer = RSTWriterWithCustomDirectives(
                builder=app.builder, app=app)
            mockapp = MockSphinxApp(writer, writer.app, confoverrides=confoverrides,
                                    new_extensions=new_extensions)
        elif writer == "md":
            app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                buildername='memorymd', confoverrides=confoverrides,
                                new_extensions=new_extensions)
            writer = MDWriterWithCustomDirectives(
                builder=app.builder, app=app)
            mockapp = MockSphinxApp(writer, writer.app, confoverrides=confoverrides,
                                    new_extensions=new_extensions)
        elif isinstance(writer, tuple):
            # We expect ("builder_name", builder_class)
            app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                buildername=writer, confoverrides=confoverrides,
                                new_extensions=new_extensions)
            if not hasattr(writer[1], "_writer_class"):
                raise AttributeError(
                    "Class '{0}' does not have any attribute '_writer_class'.".format(writer[1]))
            writer = writer[1]._writer_class(  # pylint: disable=E1101
                builder=app.builder, app=app)  # pylint: disable=E1101
            mockapp = MockSphinxApp(writer, app, confoverrides=confoverrides,
                                    new_extensions=new_extensions)
        else:
            raise ValueError(
                "Writer must be 'html', 'rst' pr 'md', not '{0}'.".format(writer))

        # titles
        title_names = []
        title_names.append("todoext_node")
        title_names.append("todo_node")
        title_names.append("mathdef_node")
        title_names.append("blocref_node")
        title_names.append("faqref_node")
        title_names.append("nbref_node")
        title_names.append("exref_node")

        if directives is not None:
            for tu in directives:
                if len(tu) < 2:
                    raise ValueError(
                        "directives is a list of tuple with at least two elements, check the documentation")
                name, cl = tu[:2]
                doc_directives.register_directive(name, cl)
                mockapp.add_directive(name, cl)
                if len(tu) == 5:
                    name, cl, node, f1, f2 = tu
                    mockapp.add_node(node, html=(f1, f2))
                    # not necessary
                    # nodes._add_node_class_names([node.__name__])
                    writer.connect_directive_node(node.__name__, f1, f2)
                elif len(tu) != 2:
                    raise ValueError(
                        "directives is a list of tuple with 2 or 5 elements, check the documentation")

        if fLOG:
            apps = [mockapp]
            if hasattr(writer, "app"):
                apps.append(writer.app)
            for app in apps:
                if hasattr(app, "_added_objects"):
                    fLOG("[MockSphinxApp] list of added objects")
                    for el in app._added_objects:
                        fLOG("[MockSphinxApp]", el)
                        if el[0] == "domain":
                            fLOG("[MockSphinxApp]    NAME", el[1].name)
                            for ro in el[1].roles:
                                fLOG("[MockSphinxApp]    ROLES", ro)
                            for ro in el[1].directives:
                                fLOG("[MockSphinxApp]    DIREC", ro)
            from docutils.parsers.rst.directives import _directives
            for res in sorted(_directives):
                fLOG("[MockSphinxApp] RST DIREC", res)

            class bb:
                def info(*args, line=0):  # pylint: disable=E0211
                    fLOG("[MockSphinxApp]   -- ", *args)

            class aa:
                def __init__(self):
                    self.reporter = bb()
                    self.current_line = 0
            from docutils.parsers.rst.languages import en
            for dir_check in ['py:function']:
                res = rst_directive(dir_check, en, aa())

        return mockapp, writer, title_names
