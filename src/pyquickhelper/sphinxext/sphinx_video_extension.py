# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to add button to share a page

.. versionadded:: 1.3
"""
import os
import copy
import sphinx
import shutil
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.logging import getLogger
from sphinx.util.docutils import is_html5_writer_available
from sphinx.util import FilenameUniqDict


if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
    from sphinx.writers.html import HTMLTranslator as HTMLTranslatorOld
    inheritance = (HTMLTranslator, HTMLTranslatorOld)
else:
    from sphinx.writers.html import HTMLTranslator
    inheritance = HTMLTranslator


DEFAULT_CONFIG = dict(
    default_video_width='100%',
    default_video_height='auto',
    cache_path='_videos',
)


class video_node(nodes.General, nodes.Element):

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

    For latex, unit becomes *pt*.
    See `latex units <https://tex.stackexchange.com/questions/8260/what-are-the-various-units-ex-em-in-pt-bp-dd-pc-expressed-in-mm>`_.
    Videos are not enabled on latex by default,
    option ``:latex:`` must be set up.
    """
    required_arguments = True
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'width': directives.unchanged,
                   'height': directives.unchanged,
                   'latex': directives.unchanged,
                   }
    has_content = True
    video_class = video_node

    def run(self):
        """
        Runs the directive.

        @return      a list of nodes
        """
        env = self.state.document.settings.env
        conf = env.app.config.videos_config
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
        else:
            docname = ''

        source = self.state.document.current_source
        filename = self.arguments[0]

        if '://' in filename:
            logger = getLogger("video")
            logger.warning(
                "[video] url detected '{0}' in docname '{1}' - line {2}.".format(filename, docname, self.lineno))
            is_url = True
        else:
            is_url = False

        if not is_url:
            env.videos.add_file('', filename)

            srcdir = env.srcdir
            rstrel = os.path.relpath(source, srcdir)
            rstfold = os.path.split(rstrel)[0]
            cache = os.path.join(srcdir, conf['cache_path'])
            vid = os.path.join(cache, filename)
            abspath = None
            relpath = None

            if os.path.exists(vid):
                abspath = vid
                relpath = cache
            else:
                last = rstfold.replace('\\', '/')
                vid = os.path.join(srcdir, last, filename)
                if os.path.exists(vid):
                    relpath = last
                    abspath = vid

            if abspath is None:
                logger = getLogger("video")
                logger.warning(
                    "[video] Unable to find '{0}' in docname '{1}' - line {2} - srcdir='{3}'.".format(filename, docname, self.lineno, srcdir))
        else:
            abspath = None
            relpath = None

        width = self.options.get('width', conf['default_video_width'])
        height = self.options.get('height', conf['default_video_height'])
        latex = self.options.get('latex', False) in (
            'True', 'true', True, 1, "1")

        # build node
        node = self.__class__.video_class(uri=filename, docname=docname, lineno=self.lineno,
                                          width=width, height=height, abspath=abspath,
                                          relpath=relpath, is_url=is_url)
        node['classes'] += ["place-video"]
        node['video'] = filename
        node['latex'] = latex
        ns = [node]
        return ns


def visit_video_node(self, node):
    """
    Visits a video node.
    Copies the video.
    """
    if node['abspath'] is not None:
        outdir = self.builder.outdir
        relpath = os.path.join(outdir, node['relpath'])
        dname = os.path.split(node['uri'])[0]
        if dname:
            relpath = os.path.join(relpath, dname)
        if not os.path.exists(relpath):
            os.makedirs(relpath)
        shutil.copy(node['abspath'], relpath)
        logger = getLogger("video")
        logger.info("[video] copy '{0}' to '{1}'".format(node['uri'], relpath))


def depart_video_node_html(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        filename = node["uri"]
        width = node["width"]
        height = node["height"]
        found = node["abspath"] is not None or node["is_url"]
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


def depart_video_node_text(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if self.builder.name == "rst":
        return depart_video_node_rst(self, node)
    elif node.hasattr("uri"):
        filename = node["uri"]
        width = node["width"]
        height = node["height"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:
            body = "unable to find '{0}'".format(filename)
            self.body.append(body)
        else:
            body = '\nvideo {0}{1}: {2}\n'
            width = ' width="{0}"'.format(width) if width else ""
            height = ' height="{0}"'.format(height) if height else ""
            body = body.format(width, height, filename,
                               os.path.splitext(filename)[-1].strip('.'))
            self.add_text(body)


def depart_video_node_latex(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        width = node["width"]
        height = node["height"]
        full = os.path.join(node["relpath"], node['uri'])
        found = node['abspath'] is not None or node["is_url"]
        if not found:
            body = "\\textbf{{unable to find '{0}'}}".format(full)
            self.body.append(body)
        else:
            def format_dim(s):
                if s == "auto" or s is None:
                    return "{}"
                else:
                    return "{{{0}pt}}".format(s)
            body = '{3}\\includemovie[poster,autoplay,externalviewer,inline=false]{0}{1}{{{2}}}\n'
            width = format_dim(width)
            height = format_dim(height)
            full = full.replace('\\', '/').replace('_', '\\_')
            comment = '' if node['latex'] else '%'
            body = body.format(width, height, full, comment)
            self.body.append(body)


def depart_video_node_rst(self, node):
    """
    What to do when leaving a node *video*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        filename = node["uri"]
        width = node["width"]
        height = node["height"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:
            body = ".. video:: {0} [not found]".format(filename)
            self.add_text(body + self.nl)
        else:
            body = ".. video:: {0}".format(filename)
            self.new_state(0)
            self.add_text(body + self.nl)
            if width:
                self.add_text('    :width: {0}'.format(width) + self.nl)
            if height:
                self.add_text('    :height: {0}'.format(height) + self.nl)
            self.end_state(wrap=False)


def initialize_videos_directive(app):
    """
    Initializes the video directives.
    """
    global DEFAULT_CONFIG

    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(app.config.videos_config)
    app.config.videos_config = config
    # ensuredir(os.path.join(app.env.srcdir, config['cache_path']))
    # app.info("Initiated video directive: cache='{}'".format(config['cache_path']))
    app.env.videos = FilenameUniqDict()


def setup(app):
    """
    setup for ``video`` (sphinx)
    """
    global DEFAULT_CONFIG
    if hasattr(app, "add_mapping"):
        app.add_mapping('video', video_node)
    app.add_config_value('videos_config', DEFAULT_CONFIG, 'env')
    app.connect('builder-inited', initialize_videos_directive)
    app.add_node(video_node,
                 html=(visit_video_node, depart_video_node_html),
                 latex=(visit_video_node, depart_video_node_latex),
                 rst=(visit_video_node, depart_video_node_rst),
                 text=(visit_video_node, depart_video_node_text))

    app.add_directive('video', VideoDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
