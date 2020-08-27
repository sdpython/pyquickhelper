# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to show :epkg:`DOT` graph
with :epkg:`viz.js` or :epkg:`graphviz`.

.. versionadded:: 1.9
"""
import os
import logging
import shutil
from docutils import nodes
from docutils.parsers.rst import directives
import sphinx
from docutils.parsers.rst import Directive
from .sphinxext_helper import get_env_state_info
from .sphinx_runpython_extension import run_python_script


class gdot_node(nodes.admonition):
    """
    defines ``gdot`` node.
    """
    pass


class GDotDirective(Directive):
    """
    A ``gdot`` node displays a :epkg:`DOT` graph.
    The build choose :epkg:`SVG` for :epkg:`HTML` format and image for
    other format unless it is specified.

    * *format*: SVG or HTML
    * *script*: boolean or a string to indicate than the standard output
        should only be considered after this substring
    * *url*: url to :epkg:`viz.js`, only if format *SVG* is selected

    Example::

        .. gdot::

            digraph foo {
                "bar" -> "baz";
            }

    Which gives:

    .. gdot::

        digraph foo {
            "bar" -> "baz";
        }

    The directive also accepts scripts producing
    dot graphs on the standard output. Option *script*
    must be specified. This extension loads
    `sphinx.ext.graphviz <https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html>`_
    if not added to the list of extensions:

    Example::

        .. gdot::
            :format: png

            digraph foo {
                "bar" -> "baz";
            }

    .. gdot::
        :format: png

        digraph foo {
            "bar" -> "baz";
        }
    """
    node_class = gdot_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'format': directives.unchanged,
        'script': directives.unchanged,
        'url': directives.unchanged,
    }

    _default_url = "http://www.xavierdupre.fr/js/vizjs/viz.js"

    def run(self):
        """
        Builds the collapse text.
        """
        # retrieves the parameters
        if 'format' in self.options:
            format = self.options['format']
        else:
            format = '?'
        url = self.options.get('url', 'local')
        if url == 'local':
            try:
                import jyquickhelper
                path = os.path.join(os.path.dirname(
                    jyquickhelper.__file__), "js", "vizjs", "viz.js")
                if not os.path.exists(path):
                    raise ImportError(
                        "jyquickelper needs to be updated to get viz.js.")
                url = 'local'
            except ImportError:
                url = GDotDirective._default_url
                logger = logging.getLogger("gdot")
                logger.warning("[gdot] jyquickhelper not installed, falling back to "
                               "'{}'".format(url))

        info = get_env_state_info(self)
        docname = info['docname']
        if url == 'local':
            if docname is None or 'HERE' not in info:
                url = GDotDirective._default_url
                logger = logging.getLogger("gdot")
                logger.warning("[gdot] docname is none, falling back to "
                               "'{}'".format(url))
            else:
                spl = docname.split("/")
                sp = ['..'] * (len(spl) - 1) + ['_static', 'viz.js']
                url = "/".join(sp)

        if 'script' in self.options:
            script = self.options['script']
            if script in (0, "0", "False", 'false'):
                script = None
            elif script in (1, "1", "True", 'true', ''):
                script = ''
            elif len(script) == 0:
                raise RuntimeError("script should be a string to indicate"
                                   " the beginning of DOT graph.")
        else:
            script = False

        # executes script if any
        content = "\n".join(self.content)
        if script or script == '':
            stdout, stderr, _ = run_python_script(content)
            if stderr:
                raise RuntimeError(
                    "A graph cannot be draw due to {}".format(stderr))
            content = stdout
            if script:
                spl = content.split(script)
                if len(spl) > 2:
                    raise RuntimeError("'{}' indicates the beginning of the graph "
                                       "but there are many in\n{}".format(script, content))
                content = spl[-1]

        node = gdot_node(format=format, code=content, url=url,
                         options={'docname': docname})
        return [node]


def visit_gdot_node_rst(self, node):
    """
    visit collapse_node
    """
    self.new_state(0)
    self.add_text('.. gdot::' + self.nl)
    if node['format'] != '?':
        self.add_text('    :format: ' + node['format'] + self.nl)
    if node['url']:
        self.add_text('    :url: ' + node['url'] + self.nl)
    self.new_state(self.indent)
    for row in node['code'].split('\n'):
        self.add_text(row + self.nl)


def depart_gdot_node_rst(self, node):
    """
    depart collapse_node
    """
    self.end_state()
    self.end_state(wrap=False)


def visit_gdot_node_html_svg(self, node):
    """
    visit collapse_node
    """
    def process(text):
        text = text.replace("\\", "\\\\")
        text = text.replace("\n", "\\n")
        text = text.replace('"', '\\"')
        return text

    nid = str(id(node))

    content = """
    <div id="gdot-{0}-cont"><div id="gdot-{0}" style="width:100%;height:100%;"></div>
    """.format(nid)

    script = """
    require(['__URL__'], function() { var svgGraph = Viz("__DOT__");
    document.getElementById('gdot-__ID__').innerHTML = svgGraph; });
    """.replace('__ID__', nid).replace('__DOT__', process(node['code'])).replace(
        "__URL__", node['url'])

    self.body.append(content)
    self.body.append("<script>{0}{1}{0}</script>{0}".format("\n", script))


def depart_gdot_node_html_svg(self, node):
    """
    depart collapse_node
    """
    self.body.append("</div>")


def visit_gdot_node_html(self, node):
    """
    visit collapse_node, the function switches between
    `graphviz.py <https://github.com/sphinx-doc/sphinx/blob/
    master/sphinx/ext/graphviz.py>`_ and the :epkg:`SVG` format.
    """
    if node['format'].lower() == 'png':
        from sphinx.ext.graphviz import html_visit_graphviz
        return html_visit_graphviz(self, node)
    if node['format'].lower() in ('?', 'svg'):
        return visit_gdot_node_html_svg(self, node)
    raise RuntimeError(
        "Unexpected format for graphviz '{}'.".format(node['format']))


def depart_gdot_node_html(self, node):
    """
    depart collapse_node
    """
    if node['format'] == 'png':
        return None
    return depart_gdot_node_html_svg(self, node)


def copy_js_files(app):
    try:
        import jyquickhelper
        local = True
    except ImportError:
        local = False

    logger = logging.getLogger("gdot")
    if local:
        path = os.path.join(os.path.dirname(
            jyquickhelper.__file__), "js", "vizjs", "viz.js")
        if os.path.exists(path):
            # We copy the file to static path.
            dest = app.config.html_static_path
            if isinstance(dest, list) and len(dest) > 0:
                dest = dest[0]
            else:
                dest = None

            srcdir = app.builder.srcdir
            if "IMPOSSIBLE:TOFIND" not in srcdir:
                if not os.path.exists(srcdir):
                    raise FileNotFoundError(
                        "Source file is wrong '{}'.".format(srcdir))

                if dest is not None:
                    destf = os.path.join(os.path.abspath(srcdir), dest)
                    if os.path.exists(destf):
                        dest = os.path.join(destf, 'viz.js')
                        try:
                            shutil.copy(path, dest)
                            logger.info(
                                "[gdot] copy '{}' to '{}'.".format(path, dest))
                        except PermissionError as e:  # pragma: no cover
                            logger.warning("[gdot] permission error: {}, "
                                           "unable to use local viz.js.".format(e))

                        if not os.path.exists(dest):
                            logger.warning("[gdot] unable to copy='{}', "
                                           "unable to use local viz.js.".format(dest))
                    else:
                        logger.warning("[gdot] destination folder='{}' does not exists, "
                                       "unable to use local viz.js.".format(destf))
                else:
                    logger.warning("[gdot] unable to locate html_static_path='{}', "
                                   "unable to use local viz.js.".format(app.config.html_static_path))
        else:
            logger.warning("[gdot] jyquickhelper needs to be update, unable to find '{}'.".format(
                path))
    else:
        logger.warning("[gdot] jyquickhelper not installed, falling back to "
                       "'{}'".format(GDotDirective._default_url))


def setup(app):
    """
    setup for ``gdot`` (sphinx)
    """
    if 'sphinx.ext.graphviz' not in app.config.extensions:
        from sphinx.ext.graphviz import setup as setup_g  # pylint: disable=W0611
        setup_g(app)

    app.connect('builder-inited', copy_js_files)

    from sphinx.ext.graphviz import latex_visit_graphviz, man_visit_graphviz  # pylint: disable=W0611
    from sphinx.ext.graphviz import text_visit_graphviz  # pylint: disable=W0611
    app.add_node(gdot_node,
                 html=(visit_gdot_node_html, depart_gdot_node_html),
                 epub=(visit_gdot_node_html, depart_gdot_node_html),
                 elatex=(latex_visit_graphviz, None),
                 latex=(latex_visit_graphviz, None),
                 text=(text_visit_graphviz, None),
                 md=(text_visit_graphviz, None),
                 rst=(visit_gdot_node_rst, depart_gdot_node_rst))

    app.add_directive('gdot', GDotDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
