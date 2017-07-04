"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""
from ..sphinxext.sphinx_bigger_extension import setup as setup_bigger
from ..sphinxext.sphinx_githublink_extension import setup as setup_githublink
from ..sphinxext.sphinx_blocref_extension import setup as setup_blocref
from ..sphinxext.sphinx_blog_extension import setup as setup_blog
from ..sphinxext.sphinx_docassert_extension import setup as setup_docassert
from ..sphinxext.sphinx_exref_extension import setup as setup_exref
from ..sphinxext.sphinx_faqref_extension import setup as setup_faqref
from ..sphinxext.sphinx_mathdef_extension import setup as setup_mathdef
from ..sphinxext.sphinx_nbref_extension import setup as setup_nbref
from ..sphinxext.sphinx_runpython_extension import setup as setup_runpython
from ..sphinxext.sphinx_sharenet_extension import setup as setup_sharenet
from ..sphinxext.sphinx_todoext_extension import setup as setup_todoext
from .sphinxm_convert_doc_sphinx_helper import HTMLWriterWithCustomDirectives
from docutils import nodes
from docutils.parsers.rst.directives import directive as rst_directive
from docutils.parsers.rst import directives as doc_directives, roles as doc_roles
from sphinx.config import Config
from sphinx.ext.autodoc import setup as setup_autodoc
# from sphinx.ext.imgmath import setup as setup_imgmath
from sphinxcontrib.imagesvg import setup as setup_imagesvg
# from sphinx.ext.autosummary import setup as setup_autosummary
from sphinx.ext import autodoc
# from sphinx.events import EventManager
# from sphinx.registry import SphinxComponentRegistry
# from sphinx.domains.python import setup as setup_python
from sphinx import __display_version__ as sphinx__display_version__
from sphinx.application import VersionRequirementError
from sphinx.util.logging import getLogger


try:
    from sphinx.util.docutils import is_html5_writer_available
except ImportError:
    # Available only after Sphinx >= 1.6.1.
    def is_html5_writer_available():
        return False


class MockSphinxApp:
    """
    Mock Sphinx application.
    In memory Sphinx application.
    """

    def __init__(self, writer, app):
        """
        Constructor

        @param      writer      see static method create
        @param      app         see static method create
        """
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
        self.config = Config(None, None, overrides={}, tags=None)
        self.confdir = "."
        self.doctreedir = "."
        self.srcdir = "."
        self.builder = writer.builder
        # self.domains = {}
        # self._events = {}
        # self.events = EventManager()
        # self.registry = SphinxComponentRegistry()
        # self.extensions = {}
        # self._setting_up_extension = ['?']

    def add_directive(self, name, cl, *args, **options):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        doc_directives.register_directive(name, cl)
        self.mapping[str(cl)] = name
        self.app.add_directive(name, cl, *args, **options)
        self.writer.app.add_directive(name, cl, *args, **options)

    def add_role(self, name, cl):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        doc_roles.register_canonical_role(name, cl)
        self.mapping[str(cl)] = name
        self.app.add_role(name, cl)
        self.writer.app.add_role(name, cl)

    def add_mapping(self, name, cl):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        self.mapping[str(cl)] = name

    def add_config_value(self, name, default, rebuild, types=()):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        if name in self.config.values:
            # We do not add it a second time.
            return
        if rebuild in (False, True):
            rebuild = rebuild and 'env' or ''
        self.new_options[name] = (default, rebuild, types)
        self.config.values[name] = (default, rebuild, types)

    def get_default_values(self):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        return {k: v[0] for k, v in self.new_options.items()}

    def add_node(self, node, **kwds):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        # type: (nodes.Node, Any) -> None
        if sphinx__display_version__ >= "1.6":
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
        else:
            self.app.add_node(node, **kwds)

    def finalize(self, doctree):
        """
        Finalize the documentation after it was parsed.

        @param      doctree     doctree (or pub.document), available after publication
        """
        self.app.finalize(doctree)

    def setup_extension(self, extname):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py>`_.
        """
        self.app.registry.load_extension(self, extname)

    def emit(self, event, *args):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        return self.app.emit(event, *args)

    def emit_firstresult(self, event, *args):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py>`_.
        """
        return self.app.events.emit_firstresult(event, self, *args)

    def add_autodocumenter(self, cls):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py>`_.
        """
        autodoc.add_documenter(cls)
        self.app.add_directive('auto' + cls.objtype, autodoc.AutoDirective)

    def connect(self, node, func):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        self.mapping_connect[node] = func
        self.app.connect(node, func)
        self.writer.app.connect(node, func)

    def add_domain(self, domain):
        """
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
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
        See class `Sphinx <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107>`_.
        """
        if name in self.app._events:
            # We do not raise an exception if already present.
            return
        self.app._events[name] = ''

    @staticmethod
    def create(writer="sphinx", directives=None, fLOG=None):
        """
        Create a MockApp

        @param      writer          ``'sphinx'`` is the only allowed value
        @param      directives      new directives to add (see below)
        @param      fLOG            logging function
        @return                     mockapp, writer, list of added nodes

        *directives* is None or a list of 5-uple:

        * a directive name
        * a directive class: see `Sphinx Directive <http://sphinx-doc.org/extdev/tutorial.html>`_,
          see also @see cl RunPythonDirective as an example
        * a docutils node: see @see cl runpython_node as an example
        * two functions: see @see fn visit_runpython_node,
          @see fn depart_runpython_node as an example

        .. versionchanged:: 1.5
            Parameter *fLOG* was added.
            The class supports more extensions.
        """
        if writer not in ("sphinx", "custom", "HTMLWriterWithCustomDirectives"):
            raise NotImplementedError("writer must be 'sphinx' or 'custom'")

        writer = HTMLWriterWithCustomDirectives()
        mockapp = MockSphinxApp(writer, writer.app)

        from sphinx.ext.graphviz import setup as setup_graphviz
        from sphinx.ext.imgmath import setup as setup_math
        from sphinx.ext.todo import setup as setup_todo
        from matplotlib.sphinxext.plot_directive import setup as setup_plot
        from matplotlib.sphinxext.only_directives import setup as setup_only

        # directives from pyquickhelper
        for app in [mockapp, writer.app]:
            setup_blog(app)
            setup_runpython(app)
            setup_sharenet(app)
            setup_todoext(app)
            setup_bigger(app)
            setup_githublink(app)
            setup_runpython(app)
            setup_mathdef(app)
            setup_blocref(app)
            setup_faqref(app)
            setup_exref(app)
            setup_nbref(app)
            setup_docassert(app)

            # directives from sphinx
            setup_graphviz(app)
            setup_math(app)
            setup_todo(app)

            setup_autodoc(app)
            try:
                from sphinxcontrib.images import setup as setup_images
                setup_images(app)
            except ImportError:
                # Probably a mismatch between versions.
                logger = getLogger("MockSphinxApp")
                logger.warning(
                    "[MockSphinxApp] unable to import 'sphinxcontrib.images'.")
            setup_imagesvg(app)

            # don't move this import to the beginning of file
            # it changes matplotlib backend
            setup_plot(app)
            setup_only(app)

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
                if len(tu) != 5:
                    raise ValueError(
                        "directives is a list of tuple with 5 elements, check the documentation")
                name, cl, node, f1, f2 = tu
                doc_directives.register_directive(name, cl)
                mockapp.add_directive(name, cl)
                mockapp.add_node(node, html=(f1, f2))
                # not necessary
                # nodes._add_node_class_names([node.__name__])
                writer.connect_directive_node(node.__name__, f1, f2)

        if fLOG:
            for app in [mockapp, writer.app]:
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
                def info(*l, line=0):
                    fLOG("[MockSphinxApp]   -- ", *l)

            class aa:
                def __init__(self):
                    self.reporter = bb()
                    self.current_line = 0
            from docutils.parsers.rst.languages import en
            for dir_check in ['py:function']:
                res = rst_directive(dir_check, en, aa())

        return mockapp, writer, title_names
