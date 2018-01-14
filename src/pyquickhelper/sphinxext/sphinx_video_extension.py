# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to add button to share a page

.. versionadded:: 1.3
"""
import os
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.logging import getLogger
from sphinx.util.docutils import is_html5_writer_available


if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
    from sphinx.writers.html import HTMLTranslator as HTMLTranslatorOld
    inheritance = (HTMLTranslator, HTMLTranslatorOld)
else:
    from sphinx.writers.html import HTMLTranslator
    inheritance = HTMLTranslator


class video_node(nodes.Structural, nodes.Element):

    """
    Defines *video* node.
    """
    pass


class VideoDirective(Directive):
    """
    Adds video to a page. It can be done by adding::

        .. video:: filename.mp4
            :width: 400
            :height: 600
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'width': directives.unchanged,
                   'height': directives.unchanged,
                   }
    has_content = True
    video_class = video_node

    def run(self):
        """
        Runs the directve.

        @return      a list of nodes
        """
        try:
            source, lineno = self.reporter.get_source_and_line(self.lineno)
        except AttributeError:
            source = lineno = None
        filename = " ".join(_.strip("\n\r\t ") for _ in self.content)

        folder = os.path.abspath(source) if source else None
        abspath = os.path.join(
            folder, filename) if folder and '//' not in filename else None
        if '//' not in filename and (not abspath or not os.path.exists(abspath)):
            logger = getLogger("video")
            logger.warning(
                "[video] video not found '{0}' in docname '{1}' - line {2}.".format(filename, source, lineno))
            found = False
        else:
            found = True

        # build node
        node = self.__class__.video_class(filename=filename, abspath=abspath, docname=source,
                                          width=self.options.get(
                                              'width', None),
                                          height=self.options.get(
                                              'height', None),
                                          found=found)
        node['classes'] += "-video"
        node['video'] = node
        ns = [node]
        return ns


def visit_video_node(self, node):
    """
    Youtube node.
    """
    pass


def depart_video_node_html(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("filename"):
        filename = node["filename"]
        width = node["width"]
        height = node["height"]
        found = node["found"]
        if not found:
            body = "<b>unable to find '{0}'</b>".format(filename)
            self.body.append(body)
        else:
            body = '<video{0}{1} controls><source src="{2}" type="video/{3}">Your browser does not support the video tag.</video>'
            width = ' width="{0}"'.format(width) if width else ""
            height = ' height="{0}"'.format(height) if height else ""
            body = body.format(width, height, filename,
                               os.path.splitext(filename)[-1].strip('.'))
            self.body.append(body)
            # copy the filename


def depart_video_node_text(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("filename"):
        filename = node["filename"]
        width = node["width"]
        height = node["height"]
        found = node["found"]
        if not found:
            body = "unable to find '{0}'".format(filename)
            self.body.append(body)
        else:
            body = 'video {0}{1}: {2}'
            width = ' width="{0}"'.format(width) if width else ""
            height = ' height="{0}"'.format(height) if height else ""
            body = body.format(width, height, filename,
                               os.path.splitext(filename).strip('.'))
            self.body.append(body)


def depart_video_node_latex(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("filename"):
        filename = node["filename"]
        width = node["width"]
        height = node["height"]
        found = node["found"]
        if not found:
            body = "\\textbf{{unable to find '{0}'}}".format(filename)
            self.body.append(body)
        else:
            body = '\\includemovie[poster,autoplay,externalviewer,inline=false]{{{0}}}{{{1}}}{{{2}}}'
            width = '{0}'.format(width) if width else "400"
            height = '{0}"'.format(height) if height else "300"
            body = body.format(width, height, filename)
            self.body.append(body)


def depart_video_node_rst(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("filename"):
        filename = node["filename"]
        width = node["width"]
        height = node["height"]
        found = node["found"]
        if not found:
            body = ".. video:: {0} [not found]".format(filename)
            self.add_text(body + self.nl)
        else:
            body = ".. video:: {0}".format(filename)
            self.add_text(body + self.nl)
            self.add_text.append(body)
            if width:
                self.add_text.append('    :width: {0}'.format(width) + self.nl)
            if height:
                self.add_text.append(
                    '    :height: {0}'.format(height) + self.nl)


def setup(app):
    """
    setup for ``video`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('video', video_node)

    app.add_node(video_node,
                 html=(visit_video_node, depart_video_node_html),
                 latex=(visit_video_node, depart_video_node_latex),
                 rst=(visit_video_node, depart_video_node_rst),
                 text=(visit_video_node, depart_video_node_text))

    app.add_directive('video', VideoDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
