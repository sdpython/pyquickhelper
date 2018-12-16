# -*- coding: utf-8 -*-
"""
@file
@brief Inspired from `sphinxcontrib.youtube <https://github.com/thewtex/sphinx-contrib/blob/master/youtube/sphinxcontrib/youtube.py>`_
(not maintained anymore).
"""
import re
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

CONTROL_HEIGHT = 30


def get_size(d, key):
    """
    Get size.

    @param      d       string
    @param      key     string
    @return             integer
    """
    if key not in d:
        return None
    m = re.match("(\\d+)(|%|px)$", d[key])
    if not m:
        raise ValueError("invalid size %r" % d[key])
    return int(m.group(1)), m.group(2) or "px"


def css(d):
    """
    Returns style.
    """
    return "; ".join(sorted("%s: %s" % kv for kv in d.items()))


class youtube_node(nodes.General, nodes.Element):
    """
    Youtube node.
    """
    pass


def visit_youtube_node(self, node):
    """
    Visit youtube node (html).
    """
    aspect = node["aspect"]
    width = node["width"]
    height = node["height"]

    if aspect is None:
        aspect = 16, 9

    if hasattr(self, "starttag"):
        if (height is None) and (width is not None) and (width[1] == "%"):
            style = {
                "padding-top": "%dpx" % CONTROL_HEIGHT,
                "padding-bottom": "%f%%" % (width[0] * aspect[1] / aspect[0]),
                "width": "%d%s" % width,
                "position": "relative",
            }
            self.body.append(self.starttag(node, "div", style=css(style)))
            style = {
                "position": "absolute",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "border": "0",
            }
            attrs = {
                "src": "https://www.youtube.com/embed/%s" % node["id"],
                "style": css(style),
            }
            self.body.append(self.starttag(node, "iframe", **attrs))
            self.body.append("</iframe></div>")
        else:
            if width is None:
                if height is None:
                    width = 560, "px"
                else:
                    width = height[0] * aspect[0] / aspect[1], "px"
            if height is None:
                height = width[0] * aspect[1] / aspect[0], "px"
            style = {
                "width": "%d%s" % width,
                "height": "%d%s" % (height[0] + CONTROL_HEIGHT, height[1]),
                "border": "0",
            }
            attrs = {
                "src": "https://www.youtube.com/embed/%s" % node["id"],
                "style": css(style),
            }
            self.body.append(self.starttag(node, "iframe", **attrs))
            self.body.append("</iframe>")
    else:
        self.body.append("https://www.youtube.com/embed/%s" % node["id"])


def depart_youtube_node(self, node):
    """
    Youtube node.
    """
    pass


class YoutubeDirective(Directive):
    """
    Youtube directive.
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "aspect": directives.unchanged,
    }

    def run(self):
        if "aspect" in self.options:
            aspect = self.options.get("aspect")
            m = re.match("(\\d+):(\\d+)", aspect)
            if m is None:
                raise ValueError("invalid aspect ratio %r" % aspect)
            aspect = tuple(int(x) for x in m.groups())
        else:
            aspect = None
        width = get_size(self.options, "width")
        height = get_size(self.options, "height")
        idurl = self.arguments[0]
        if "https://" in idurl or "http://" in idurl:
            if "watch?v=" in idurl:
                uid = idurl.split("watch?v=")[-1]
            else:
                uid = idurl.split('/')[-1]
                if len(uid) <= 4 or '.' in uid:
                    env = self.state.document.settings.env if hasattr(
                        self.state.document.settings, "env") else None
                    logger = logging.getLogger("youtube")
                    lineno = self.lineno
                    docname = None if env is None else env.docname
                    logger.warning(
                        "[youtube] unable to extract video id from '{0}' in docname '{1}' - line {2}.".format(idurl, docname, lineno))
                    uid = ""
        else:
            uid = self.arguments[0]
        return [youtube_node(id=uid, aspect=aspect, width=width, height=height)]


def setup(app):
    """
    Setup for youtube extension.
    """
    app.add_node(youtube_node,
                 html=(visit_youtube_node, depart_youtube_node),
                 epub=(visit_youtube_node, depart_youtube_node),
                 elatex=(visit_youtube_node, depart_youtube_node),
                 latex=(visit_youtube_node, depart_youtube_node),
                 rst=(visit_youtube_node, depart_youtube_node),
                 md=(visit_youtube_node, depart_youtube_node),
                 text=(visit_youtube_node, depart_youtube_node))
    app.add_directive("youtube", YoutubeDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
