# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to hide / unhide section of the
HTML page.

.. versionadded:: 1.7
"""
import logging
from docutils import nodes
from docutils.parsers.rst import directives
import sphinx
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from .sphinx_ext_helper import sphinx_lang
from ..texthelper.texts_language import TITLES


class collapse_node(nodes.admonition):
    """
    defines ``collapse`` node.
    """
    pass


class CollapseDirective(Directive):
    """
    A ``collapse`` adds hide/unhide button
    for a part of HTML page. It has no effect
    in other formats.

    * *legend*: legend for the button, if not precise,
      it will be hide / unhide. Example: ``:legend: hide/unhide``.
    * *hide*: the text is shown by default unless this option is set up.

    Example::

        .. collapse::
            :legend: hide/unhide

            some text to hide or unhide

    Which gives:

    .. collapse::

        some text to hide or unhide
    """
    node_class = collapse_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'legend': directives.unchanged,
        'hide': directives.unchanged,
    }

    def run(self):
        """
        Builds the collapse text.
        """
        env = getattr(self.state.document.settings, "env", None)
        lang = sphinx_lang(env)
        titles = TITLES.get(lang, TITLES['en'])

        if 'legend' in self.options:
            legend = self.options['legend']
            if '/' not in legend:
                logger = logging.getLogger("sphinx")
                logger.warning(
                    "[CollapseDirective] unable to interpret parameter legend '{0}'".format(legend))
                legend = None
            spl = legend.split('/')
            hide = spl[0].strip()
            unhide = spl[1].strip()
        else:
            legend = None

        if legend is None:
            hide = titles['hide']
            unhide = titles['unhide']

        if 'hide' in self.options and self.options['hide'] not in (False, 'False', 'false', 0, '0'):
            show = False
        else:
            show = True
        node = collapse_node(hide=hide, unhide=unhide, show=show)
        nested_parse_with_titles(self.state, self.content, node)
        return [node]


def visit_collapse_node(self, node):
    """
    visit collapse_node
    """
    pass  # pragma: no cover


def depart_collapse_node(self, node):
    """
    depart collapse_node
    """
    pass  # pragma: no cover


def visit_collapse_node_rst(self, node):
    """
    visit collapse_node
    """
    self.new_state(0)
    legend = '/'.join([node['hide'], node['unhide']])
    self.add_text('.. collapse::' + self.nl)
    self.add_text('    :legend: ' + legend + self.nl)
    if not node['show']:
        self.add_text('    :hide:' + self.nl)
    self.new_state(self.indent)


def depart_collapse_node_rst(self, node):
    """
    depart collapse_node
    """
    self.end_state()
    self.end_state(wrap=False)


def visit_collapse_node_html(self, node):
    """
    visit collapse_node
    """
    nid = str(id(node))
    hide, unhide = node['hide'], node['unhide']

    script = """function myFunction__ID__() {
                    var x = document.getElementById("collapse__ID__");
                    var b = document.getElementById("colidb__ID__");
                    if (x.style.display === "none") { x.style.display = "block"; b.innerText = '__HIDE__'; }
                    else { x.style.display = "none"; b.innerText = '__UNHIDE__'; }
                }""".replace("                ", "")
    script = script.replace('__ID__', nid)
    script = script.replace('__HIDE__', hide)
    script = script.replace('__UNHIDE__', unhide)

    self.body.append("<script>{0}{1}{0}</script>{0}".format("\n", script))
    if node['show']:
        content = '<div id="collapse{0}"">'.format(nid)
        label = hide
    else:
        content = '<div id="collapse{0}" style="display:none;">'.format(nid)
        label = unhide
    self.body.append(
        '<p style="margin-bottom:10px;"><button id="colidb{0}" onclick="myFunction{0}()">{1}</button></p>{2}'.format(nid, label, "\n"))
    self.body.append(content)


def depart_collapse_node_html(self, node):
    """
    depart collapse_node
    """
    self.body.append("</div>")


def setup(app):
    """
    setup for ``collapse`` (sphinx)
    """
    app.add_node(collapse_node,
                 html=(visit_collapse_node_html, depart_collapse_node_html),
                 epub=(visit_collapse_node_html, depart_collapse_node_html),
                 elatex=(visit_collapse_node, depart_collapse_node),
                 latex=(visit_collapse_node, depart_collapse_node),
                 text=(visit_collapse_node, depart_collapse_node),
                 md=(visit_collapse_node, depart_collapse_node),
                 rst=(visit_collapse_node_rst, depart_collapse_node_rst))

    app.add_directive('collapse', CollapseDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
