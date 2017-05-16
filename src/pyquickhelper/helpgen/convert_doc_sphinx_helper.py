"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.3
"""
import sys
# from docutils import nodes
from sphinx.locale import _
from docutils.parsers.rst import directives, roles
from docutils.languages import en as docutils_en
from sphinx.writers.html import HTMLWriter
from sphinx.builders.html import SingleFileHTMLBuilder, SerializingHTMLBuilder
from sphinx.util.docutils import is_html5_writer_available, directive_helper
from sphinx.application import Sphinx
from collections import deque
from ..sphinxext.sphinx_bigger_extension import visit_bigger_node as ext_visit_bigger_node, depart_bigger_node as ext_depart_bigger_node
from ..sphinxext.sphinx_blocref_extension import visit_blocref_node as ext_visit_blocref_node, depart_blocref_node as ext_depart_blocref_node
from ..sphinxext.sphinx_blog_extension import visit_blogpost_node as ext_visit_blogpost_node, depart_blogpost_node as ext_depart_blogpost_node
from ..sphinxext.sphinx_blog_extension import visit_blogpostagg_node as ext_visit_blogpostagg_node, depart_blogpostagg_node as ext_depart_blogpostagg_node
from ..sphinxext.sphinx_exref_extension import visit_exref_node as ext_visit_exref_node, depart_exref_node as ext_depart_exref_node
from ..sphinxext.sphinx_faqref_extension import visit_faqref_node as ext_visit_faqref_node, depart_faqref_node as ext_depart_faqref_node
from ..sphinxext.sphinx_mathdef_extension import visit_mathdef_node as ext_visit_mathdef_node, depart_mathdef_node as ext_depart_mathdef_node
from ..sphinxext.sphinx_nbref_extension import visit_nbref_node as ext_visit_nbref_node, depart_nbref_node as ext_depart_nbref_node
from ..sphinxext.sphinx_runpython_extension import visit_runpython_node as ext_visit_runpython_node, depart_runpython_node as ext_depart_runpython_node
from ..sphinxext.sphinx_sharenet_extension import visit_sharenet_node as ext_visit_sharenet_node, depart_sharenet_node as ext_depart_sharenet_node
from ..sphinxext.sphinx_todoext_extension import visit_todoext_node as ext_visit_todoext_node, depart_todoext_node as ext_depart_todoext_node

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO

if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
else:
    from sphinx.writers.html import HTMLTranslator


def update_docutils_languages(values=None):
    """
    update ``docutils/languages/en.py`` with missing labels

    does that for languages:

    * en

    @param      values      consider values in this dictionaries first
    """
    if values is None:
        values = dict()
    lab = docutils_en.labels
    if 'versionmodified' not in lab:
        lab['versionmodified'] = values.get('versionmodified', '')


class HTMLTranslatorWithCustomDirectives(HTMLTranslator):
    """
    @see cl HTMLWriterWithCustomDirectives
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        HTMLTranslator.__init__(self, builder, *args, **kwds)
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)

    def visit_blogpost_node(self, node):
        """
        @see fn visit_blogpost_node
        """
        ext_visit_blogpost_node(self, node)

    def depart_blogpost_node(self, node):
        """
        @see fn depart_blogpost_node
        """
        ext_depart_blogpost_node(self, node)

    def visit_blogpostagg_node(self, node):
        """
        @see fn visit_blogpostagg_node
        """
        ext_visit_blogpostagg_node(self, node)

    def depart_blogpostagg_node(self, node):
        """
        @see fn depart_blogpostagg_node
        """
        ext_depart_blogpostagg_node(self, node)

    def visit_runpython_node(self, node):
        """
        @see fn visit_runpython_node
        """
        ext_visit_runpython_node(self, node)

    def depart_runpython_node(self, node):
        """
        @see fn depart_runpython_node
        """
        ext_depart_runpython_node(self, node)

    def visit_sharenet_node(self, node):
        """
        @see fn visit_sharenet_node
        """
        ext_visit_sharenet_node(self, node)

    def depart_sharenet_node(self, node):
        """
        @see fn depart_sharenet_node
        """
        ext_depart_sharenet_node(self, node)

    def visit_bigger_node(self, node):
        """
        @see fn visit_bigger_node
        """
        ext_visit_bigger_node(self, node)

    def depart_bigger_node(self, node):
        """
        @see fn depart_bigger_node
        """
        ext_depart_bigger_node(self, node)

    def visit_todoext_node(self, node):
        """
        @see fn visit_todoext_node
        """
        ext_visit_todoext_node(self, node)

    def depart_todoext_node(self, node):
        """
        @see fn depart_todoext_node
        """
        ext_depart_todoext_node(self, node)

    def visit_mathdef_node(self, node):
        """
        @see fn visit_mathdef_node
        """
        ext_visit_mathdef_node(self, node)

    def depart_mathdef_node(self, node):
        """
        @see fn depart_mathdef_node
        """
        ext_depart_mathdef_node(self, node)

    def visit_blocref_node(self, node):
        """
        @see fn visit_blocref_node
        """
        ext_visit_blocref_node(self, node)

    def depart_blocref_node(self, node):
        """
        @see fn depart_blocref_node
        """
        ext_depart_blocref_node(self, node)

    def visit_faqref_node(self, node):
        """
        @see fn visit_faqref_node
        """
        ext_visit_faqref_node(self, node)

    def depart_faqref_node(self, node):
        """
        @see fn depart_faqref_node
        """
        ext_depart_faqref_node(self, node)

    def visit_nbref_node(self, node):
        """
        @see fn visit_nbref_node
        """
        ext_visit_nbref_node(self, node)

    def depart_nbref_node(self, node):
        """
        @see fn depart_nbref_node
        """
        ext_depart_nbref_node(self, node)

    def visit_exref_node(self, node):
        """
        @see fn visit_exref_node
        """
        ext_visit_exref_node(self, node)

    def depart_exref_node(self, node):
        """
        @see fn depart_exref_node
        """
        ext_depart_exref_node(self, node)

    def add_secnumber(self, node):
        """
        overwrites this method to catch errors due when
        it is a single document being processed
        """
        if node.get('secnumber'):
            HTMLTranslator.add_secnumber(self, node)
        elif len(node.parent['ids']) > 0:
            HTMLTranslator.add_secnumber(self, node)
        else:
            n = len(self.builder.secnumbers)
            node.parent['ids'].append("custom_label_%d" % n)
            HTMLTranslator.add_secnumber(self, node)


class HTMLWriterWithCustomDirectives(HTMLWriter):
    """
    This docutils writer extends the HTML writer with
    custom directives implemented in this module,
    @see cl RunPythonDirective, @see cl BlogPostDirective

    See `Write your own ReStructuredText-Writer <http://www.arnebrodowski.de/blog/write-your-own-restructuredtext-writer.html>`_.

    This class needs to tell *docutils* to calls the added function
    when directives *RunPython* or *BlogPost* are met.
    """

    def __init__(self):
        """
        constructor
        """
        self.app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                 buildername='html')
        builder = self.app.builder
        builder.fignumbers = {}
        HTMLWriter.__init__(self, builder)
        self.translator_class = HTMLTranslatorWithCustomDirectives
        self.translator_class = self.translator_class
        self.builder.secnumbers = {}
        self.builder._function_node = []
        self.builder.current_docname = None

    def connect_directive_node(self, name, f_visit, f_depart):
        """
        add custom node to the translator

        @param      name        name of the directive
        @param      f_visit     visit function
        @param      f_depart    depart function
        """
        self.builder._function_node.append((name, f_visit, f_depart))

    def add_configuration_options(self, new_options):
        """
        add new options

        @param      new_options     new options
        """
        for k, v in new_options.items():
            self.builder.config.values[k] = new_options[k]


class _CustomSphinx(Sphinx):
    """
    custom sphinx application to avoid using disk
    """

    def __init__(self, srcdir, confdir, outdir, doctreedir, buildername,
                 confoverrides=None, status=None, warning=None,
                 freshenv=False, warningiserror=False, tags=None, verbosity=0,
                 parallel=0):
        '''
        constructor

        Some insights about domains:

        ::

            {'cpp': sphinx.domains.cpp.CPPDomain,
             'js': sphinx.domains.javascript.JavaScriptDomain,
             'std': sphinx.domains.std.StandardDomain,
             'py': sphinx.domains.python.PythonDomain,
             'rst': sphinx.domains.rst.ReSTDomain,
             'c': sphinx.domains.c.CDomain}

        And builders:

        ::

            {'epub': ('epub', 'EpubBuilder'),
            'singlehtml': ('html', 'SingleFileHTMLBuilder'),
            'qthelp': ('qthelp', 'QtHelpBuilder'),
            'epub3': ('epub3', 'Epub3Builder'),
            'man': ('manpage', 'ManualPageBuilder'),
            'dummy': ('dummy', 'DummyBuilder'),
            'json': ('html', 'JSONHTMLBuilder'),
            'html': ('html', 'StandaloneHTMLBuilder'),
            'xml': ('xml', 'XMLBuilder'),
            'texinfo': ('texinfo', 'TexinfoBuilder'),
            'devhelp': ('devhelp', 'DevhelpBuilder'),
            'web': ('html', 'PickleHTMLBuilder'),
            'pickle': ('html', 'PickleHTMLBuilder'),
            'htmlhelp': ('htmlhelp', 'HTMLHelpBuilder'),
            'applehelp': ('applehelp', 'AppleHelpBuilder'),
            'linkcheck': ('linkcheck', 'CheckExternalLinksBuilder'),
            'dirhtml': ('html', 'DirectoryHTMLBuilder'),
            'latex': ('latex', 'LaTeXBuilder'),
            'text': ('text', 'TextBuilder'),
            'changes': ('changes', 'ChangesBuilder'),
            'websupport': ('websupport', 'WebSupportBuilder'),
            'gettext': ('gettext', 'MessageCatalogBuilder'),
            'pseudoxml': ('xml', 'PseudoXMLBuilder')}
        '''
        from sphinx.application import bold, Tags, builtin_extensions
        from sphinx.application import Config, CONFIG_FILENAME, ConfigError, VersionRequirementError
        from sphinx import __display_version__
        from sphinx.registry import SphinxComponentRegistry
        from sphinx.events import EventManager
        from sphinx.extension import verify_required_extensions

        # from sphinx.domains.cpp import CPPDomain
        # from sphinx.domains.javascript import JavaScriptDomain
        # from sphinx.domains.python import PythonDomain
        # from sphinx.domains.std import StandardDomain
        # from sphinx.domains.rst import ReSTDomain
        # from sphinx.domains.c import CDomain

        if doctreedir is None:
            doctreedir = "."
        if srcdir is None:
            srcdir = "."
        update_docutils_languages()
        self.verbosity = verbosity

        # type: Dict[unicode, Extension]
        self.extensions = {}
        self._setting_up_extension = ['?']      # type: List[unicode]
        self.builder = None                     # type: Builder
        self.env = None                         # type: BuildEnvironment
        self.registry = SphinxComponentRegistry()
        self.enumerable_nodes = {}              # type: Dict[nodes.Node, Tuple[unicode, Callable]]  # NOQA
        self.post_transforms = []               # type: List[Transform]
        self.html_themes = {}                   # type: Dict[unicode, unicode]

        self.srcdir = srcdir
        self.confdir = confdir
        self.outdir = outdir
        self.doctreedir = doctreedir
        self.parallel = parallel

        if status is None:
            self._status = StringIO()      # type: IO
            self.quiet = True
        else:
            self._status = status
            self.quiet = False

        if warning is None:
            self._warning = StringIO()     # type: IO
        else:
            self._warning = warning
        self._warncount = 0
        self.warningiserror = warningiserror

        self.events = EventManager()

        # keep last few messages for traceback
        # This will be filled by sphinx.util.logging.LastMessagesWriter
        self.messagelog = deque(maxlen=10)  # type: deque

        # say hello to the world
        self.info(bold('Running Sphinx v%s' % "CUSTOM 1.6"))

        # status code for command-line application
        self.statuscode = 0

        # read config
        self.tags = Tags(tags)
        self.config = Config(confdir, CONFIG_FILENAME,
                             confoverrides or {}, self.tags)
        self.config.check_unicode()
        # defer checking types until i18n has been initialized

        # initialize some limited config variables before initialize i18n and loading
        # extensions
        self.config.pre_init_values()

        # set up translation infrastructure
        self._init_i18n()

        # check the Sphinx version if requested
        if self.config.needs_sphinx and self.config.needs_sphinx > __display_version__:
            raise VersionRequirementError(
                _('This project needs at least Sphinx v%s and therefore cannot '
                  'be built with this version.') % self.config.needs_sphinx)

        # set confdir to srcdir if -C given (!= no confdir); a few pieces
        # of code expect a confdir to be set
        if self.confdir is None:
            self.confdir = self.srcdir

        # load all built-in extension modules
        for extension in builtin_extensions[1:]:
            try:
                self.setup_extension(extension)
            except Exception as e:
                mes = "Unable to setup_extension '{0}'\nWHOLE LIST\n{1}".format(
                    extension, "\n".join(builtin_extensions))
                raise Exception(mes) from e

        # extension loading support for alabaster theme
        # self.config.html_theme is not set from conf.py at here
        # for now, sphinx always load a 'alabaster' extension.
        if 'alabaster' not in self.config.extensions:
            self.config.extensions.append('alabaster')

        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)

        # add default HTML builders
        self.add_builder(SingleFileHTMLBuilder)
        self.add_builder(SerializingHTMLBuilder)

        # preload builder module (before init config values)
        self.preload_builder(buildername)

        # the config file itself can be an extension
        if self.config.setup:
            # py31 doesn't have 'callable' function for below check
            if hasattr(self.config.setup, '__call__'):
                self.config.setup(self)
            else:
                raise ConfigError(
                    _("'setup' as currently defined in conf.py isn't a Python callable. "
                      "Please modify its definition to make it a callable function. This is "
                      "needed for conf.py to behave as a Sphinx extension.")
                )

        # now that we know all config values, collect them from conf.py
        self.config.init_values()

        # check extension versions if requested
        verify_required_extensions(self, self.config.needs_extensions)

        # check primary_domain if requested
        primary_domain = self.config.primary_domain
        if primary_domain and not self.registry.has_domain(primary_domain):
            self.warning(
                _('primary_domain %r not found, ignored.'), primary_domain)

        # create the builder
        self.builder = self.create_builder(buildername)
        # check all configuration values for permissible types
        self.config.check_types()
        # set up source_parsers
        self._init_source_parsers()
        # set up the build environment
        self._init_env(freshenv)
        # set up the builder
        self._init_builder()
        # set up the enumerable nodes
        self._init_enumerable_nodes()

    def add_builder(self, builder):
        # type: (Type[Builder]) -> None
        if builder.name not in self.registry.builders:
            self.debug('[app] adding builder: %r', builder)
            self.registry.add_builder(builder)
        else:
            self.debug('[app] already added builder: %r', builder)

    def setup_extension(self, extname):
        # type: (unicode) -> None
        """Import and setup a Sphinx extension module. No-op if called twice."""
        self.debug('[app] setting up extension: %r', extname)
        try:
            self.registry.load_extension(self, extname)
        except Exception as e:
            raise Exception(
                "Unable to setup extension '{0}'".format(extname)) from e

    def debug(self, message, *args, **kwargs):
        pass

    def warn(self, message, location=None, prefix=None,
             type=None, subtype=None, colorfunc=None):
        pass

    def info(self, message='', nonl=False):
        pass

    def warning(self, message='', nonl=False, name=None, type=None, subtype=None):
        pass

    def add_directive(self, name, obj, content=None, arguments=None, **options):
        # type: (unicode, Any, bool, Tuple[int, int, bool], Any) -> None
        self.debug('[app] adding directive: %r',
                   (name, obj, content, arguments, options))
        if name in directives._directives:
            self.warning(_('while setting up extension %s: directive %r is '
                           'already registered, it will be overridden'),
                         self._setting_up_extension[-1], name,
                         type='app', subtype='add_directive')
        directive = directive_helper(obj, content, arguments, **options)
        directives.register_directive(name, directive)

    def add_role(self, name, role):
        # type: (unicode, Any) -> None
        self.debug('[app] adding role: %r', (name, role))
        if name in roles._roles:
            self.warning(_('while setting up extension %s: role %r is '
                           'already registered, it will be overridden'),
                         self._setting_up_extension[-1], name,
                         type='app', subtype='add_role')
        roles.register_local_role(name, role)

    def add_generic_role(self, name, nodeclass):
        # type: (unicode, Any) -> None
        # don't use roles.register_generic_role because it uses
        # register_canonical_role
        self.debug('[app] adding generic role: %r', (name, nodeclass))
        if name in roles._roles:
            self.warning(_('while setting up extension %s: role %r is '
                           'already registered, it will be overridden'),
                         self._setting_up_extension[-1], name,
                         type='app', subtype='add_generic_role')
        role = roles.GenericRole(name, nodeclass)
        roles.register_local_role(name, role)
