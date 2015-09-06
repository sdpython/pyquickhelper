"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""
import sys
import io
import re
import textwrap
from docutils import core, nodes
from docutils.parsers.rst import directives
from sphinx.writers.html import HTMLWriter, HTMLTranslator
from sphinx.builders.html import SingleFileHTMLBuilder, SerializingHTMLBuilder
from sphinx.application import Sphinx
from collections import deque

from .utils_sphinx_doc import migrating_doxygen_doc
from ..loghelper.flog import noLOG
from . helpgen_exceptions import HelpGenConvertError
from .sphinx_blog_extension import visit_blogpost_node, depart_blogpost_node, visit_blogpostagg_node, depart_blogpostagg_node, blogpostagg_node, blogpost_node, BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_runpython_extension import visit_runpython_node, depart_runpython_node, runpython_node, RunPythonDirective

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


# -- HELP BEGIN EXCLUDE --

from .utils_sphinx_doc import private_migrating_doxygen_doc

# -- HELP END EXCLUDE --


def rst2html(s, fLOG=noLOG, writer="sphinx", keep_warnings=False):
    """
    converts a string into HTML format

    @param  s               string to converts
    @param  fLOG            logging function (warnings will be logged)
    @param  writer          *None* or an instance such as ``HTMLWriterWithCustomDirectives()`` or
                            ``custom`` or ``sphinx``
    @param  keep_warnings   keep_warnings in the final HTML
    @return                 HTML format

    .. versionadded:: 1.0

    .. versionchanged:: 1.3
        Parameters *writer*, *keep_warnings* were added to specifiy a custom writer
        and to keep the warnings. By default, the function now interprets *Sphinx*
        directives and not only *docutils* ones.
    """

    if writer in ["custom", "sphinx"]:
        directives.register_directive("blogpost", BlogPostDirective)
        directives.register_directive("blogpostagg", BlogPostDirectiveAgg)
        directives.register_directive("runpython", RunPythonDirective)
        writer = HTMLWriterWithCustomDirectives()
        writer_name = 'pseudoxml'
        for cl in [blogpost_node, blogpostagg_node, runpython_node]:
            nodes._add_node_class_names([cl.__name__])
    else:
        writer_name = 'html'

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


def docstring2html(function_or_string, format="html", fLOG=noLOG, writer=None):
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
            raise HelpGenConvertError(
                "unable to process:\n{0}".format(ded)) from e

    if format == "html":
        from IPython.core.display import HTML
        return HTML(html)
    elif format == "rawhtml":
        return html
    else:
        raise ValueError(
            "unexected format: " + format + ", should be html, rawhtml, text, rst")


class HTMLTranslatorWithCustomDirectives(HTMLTranslator):
    """
    @see cl HTMLWriterWithCustomDirectives
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        HTMLTranslator.__init__(self, builder, *args, **kwds)

    def visit_blogpost_node(self, node):
        """
        @see fn visit_blogpost_node
        """
        #ext_visit_blogpost_node(self, node)
        self.body.append("depart_runpython_node")

    def depart_blogpost_node(self, node):
        """
        @see fn depart_blogpost_node
        """
        #ext_depart_blogpost_node(self, node)
        self.body.append("depart_runpython_node")

    def visit_blogpostagg_node(self, node):
        """
        @see fn visit_blogpostagg_node
        """
        #ext_visit_blogpostagg_node(self, node)
        self.body.append("depart_runpython_node")

    def depart_blogpostagg_node(self, node):
        """
        @see fn depart_blogpostagg_node
        """
        #ext_depart_blogpostagg_node(self, node)
        self.body.append("depart_runpython_node")

    def visit_runpython_node(self, node):
        """
        @see fn visit_runpython_node
        """
        #ext_visit_runpython_node(self, node)
        self.body.append("depart_runpython_node")

    def depart_runpython_node(self, node):
        """
        @see fn depart_runpython_node
        """
        # ext_depart_runpython_node(self, node)
        self.body.append("depart_runpython_node")


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
                                 buildername='SerializingHTMLBuilder')
        builder = self.app.builder
        HTMLWriter.__init__(self, builder)
        self.translator_class = HTMLTranslatorWithCustomDirectives
        self.builder.translator_class = self.translator_class
        self.builder.secnumbers = {}


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
        '''
        from sphinx.application import BUILTIN_DOMAINS, BUILTIN_BUILDERS, events, bold, Tags, Config, CONFIG_FILENAME
        from sphinx import __display_version__
        self.verbosity = verbosity
        self.next_listener_id = 0
        self._extensions = {}
        self._extension_metadata = {}
        self._listeners = {}
        self.domains = BUILTIN_DOMAINS.copy()
        self.builderclasses = BUILTIN_BUILDERS.copy()
        self.builder = None
        self.env = None

        if doctreedir is None:
            doctreedir = "."

        self.srcdir = srcdir
        self.confdir = confdir
        self.outdir = outdir
        self.doctreedir = doctreedir

        self.parallel = parallel

        if status is None:
            self._status = StringIO()
            self.quiet = True
        else:
            self._status = status
            self.quiet = False

        if warning is None:
            self._warning = StringIO()
        else:
            self._warning = warning
        self._warncount = 0
        self.warningiserror = warningiserror

        self._events = events.copy()
        self._translators = {}

        # keep last few messages for traceback
        self.messagelog = deque(maxlen=10)

        # say hello to the world
        self.info(bold('Running Sphinx v%s' % __display_version__))

        # status code for command-line application
        self.statuscode = 0

        # read config
        self.tags = Tags(tags)
        self.config = Config(confdir, CONFIG_FILENAME,
                             confoverrides or {}, self.tags)
        self.config.check_unicode(self.warn)
        # defer checking types until i18n has been initialized

        # set confdir to srcdir if -C given (!= no confdir); a few pieces
        # of code expect a confdir to be set
        if self.confdir is None:
            self.confdir = self.srcdir

        # extension loading support for alabaster theme
        # self.config.html_theme is not set from conf.py at here
        # for now, sphinx always load a 'alabaster' extension.
        if 'alabaster' not in self.config.extensions:
            self.config.extensions.append('alabaster')

        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)
        # the config file itself can be an extension
        if self.config.setup:
            # py31 doesn't have 'callable' function for below check
            if hasattr(self.config.setup, '__call__'):
                self.config.setup(self)
            else:
                raise ConfigError(
                    "'setup' that is specified in the conf.py has not been " +
                    "callable. Please provide a callable `setup` function " +
                    "in order to behave as a sphinx extension conf.py itself."
                )

        # now that we know all config values, collect them from conf.py
        self.config.init_values(self.warn)

        # check the Sphinx version if requested
        if self.config.needs_sphinx and \
           self.config.needs_sphinx > sphinx.__display_version__[:3]:
            raise VersionRequirementError(
                'This project needs at least Sphinx v%s and therefore cannot '
                'be built with this version.' % self.config.needs_sphinx)

        # check extension versions if requested
        if self.config.needs_extensions:
            for extname, needs_ver in self.config.needs_extensions.items():
                if extname not in self._extensions:
                    self.warn('needs_extensions config value specifies a '
                              'version requirement for extension %s, but it is '
                              'not loaded' % extname)
                    continue
                has_ver = self._extension_metadata[extname]['version']
                if has_ver == 'unknown version' or needs_ver > has_ver:
                    raise VersionRequirementError(
                        'This project needs the extension %s at least in '
                        'version %s and therefore cannot be built with the '
                        'loaded version (%s).' % (extname, needs_ver, has_ver))

        # set up translation infrastructure
        self._init_i18n()
        # check all configuration values for permissible types
        self.config.check_types(self.warn)
        # set up the build environment
        self._init_env(freshenv)
        # set up the builder
        self.builderclasses = dict(SingleFileHTMLBuilder=SingleFileHTMLBuilder,
                                   SerializingHTMLBuilder=SerializingHTMLBuilder)
        self._init_builder(buildername)
