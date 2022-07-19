# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to add button to share a page
"""
import os
import copy
import shutil
from html import escape
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.logging import getLogger
from sphinx.util import FilenameUniqDict


DEFAULT_CONFIG = dict(
    default_image_width=None,
    default_image_height=None,
    cache_path='_images',
)


class simpleimage_node(nodes.General, nodes.Element):

    """
    Defines *image* node.
    """
    pass


class SimpleImageDirective(Directive):
    """
    Adds an image to a page. It can be done by adding::

        .. simpleimage:: filename.png
            :width: 400
            :height: 600

    Available options:

    * ``:width:``, ``:height:``, ``:scale:``: resize the image
    * ``:target:``: for HTML, clickable image
    * ``:alt:``: for HTML
    * ``:download:`` if the image is a url, it downloads the image.
    * ``:convert:`` convert the image into a new format
    """
    required_arguments = True
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'width': directives.unchanged,
                   'height': directives.unchanged,
                   'scale': directives.unchanged,
                   'target': directives.unchanged,
                   'alt': directives.unchanged,
                   'download': directives.unchanged,
                   'convert': directives.unchanged,
                   }
    has_content = True
    node_class = simpleimage_node

    def run(self):
        """
        Runs the directive.

        @return      a list of nodes
        """
        env = self.state.document.settings.env
        conf = env.app.config.simpleimages_config
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
        else:
            docname = ''

        source = self.state.document.current_source
        filename = self.arguments[0]

        if '://' in filename:
            logger = getLogger("simpleimage")  # pragma: no cover
            logger.warning(  # pragma: no cover
                "[simpleimage] url detected '{0}' in docname '{1}' - line {2}"
                ".".format(filename, docname, self.lineno))
            is_url = True
        else:
            is_url = False

        convert = self.options.get('convert', None)
        if convert:
            logger = getLogger("simpleimage")  # pragma: no cover
            logger.warning(  # pragma: no cover
                "[simpleimage] convert into '{3}' not implemented for '{0}' in "
                "docname '{1}' - line {2}.".format(
                    filename, docname, self.lineno, convert))

        download = self.options.get('download', None)
        if convert:
            logger = getLogger("simpleimage")
            logger.warning(  # pragma: no cover
                f"[simpleimage] download not implemented for '{filename}' in docname '{docname}' - line {self.lineno}.")

        if not is_url:
            env.images_mapping.add_file('', filename)

            srcdir = env.srcdir
            rstrel = os.path.relpath(source, srcdir)
            rstfold = os.path.split(rstrel)[0]
            cache = os.path.join(srcdir, conf['cache_path'])
            img = os.path.join(cache, filename)
            abspath = None
            relpath = None

            if os.path.exists(img):
                abspath = img
                relpath = cache
            else:
                last = rstfold.replace('\\', '/')
                img = os.path.join(srcdir, last, filename)
                if os.path.exists(img):
                    relpath = last
                    abspath = img

            if abspath is None:
                logger = getLogger("simpleimage")  # pragma: no cover
                logger.warning(  # pragma: no cover
                    "[simpleimage] Unable to find '{0}' in docname '{1}' - line {2} - srcdir='{3}'.".format(
                        filename, docname, self.lineno, srcdir))
        else:
            abspath = None
            relpath = None

        width = self.options.get('width', conf['default_image_width'])
        height = self.options.get('height', conf['default_image_height'])
        scale = self.options.get('scale', None)
        alt = self.options.get('alt', None)
        target = self.options.get('target', None)

        # build node
        node = self.__class__.node_class(uri=filename, docname=docname, lineno=self.lineno,
                                         width=width, height=height, abspath=abspath,
                                         relpath=relpath, is_url=is_url, alt=alt, scale=scale,
                                         target=target, convert=convert, download=download)
        node['classes'] += ["place-image"]
        node['image'] = filename
        ns = [node]
        return ns


def visit_simpleimage_node(self, node):
    """
    Visits a image node.
    Copies the image.
    """
    if node['abspath'] is not None:
        outdir = self.builder.outdir
        relpath = os.path.join(outdir, node['relpath'])
        dname = os.path.split(node['uri'])[0]
        if dname:
            relpath = os.path.join(relpath, dname)
        if not os.path.exists(relpath):
            os.makedirs(relpath)
        if os.path.dirname(node['abspath']) != relpath:
            shutil.copy(node['abspath'], relpath)
            logger = getLogger("image")  # pragma: no cover
            logger.info("[image] copy '{0}' to '{1}'".format(  # pragma: no cover
                node['uri'], relpath))


def _clean_value(val):
    if isinstance(val, tuple):
        return val[0]
    return val


def depart_simpleimage_node_html(self, node):
    """
    What to do when leaving a node *image*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        filename = node["uri"]
        width = _clean_value(node["width"])
        height = _clean_value(node["height"])
        scale = node["scale"]
        alt = node["alt"]
        target = node["target"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:  # pragma: no cover
            body = f"<b>unable to find '{filename}'</b>"
            self.body.append(body)
        else:
            body = '<img src="{0}" {1} {2}/>'
            width = f' width="{width}"' if width else ""
            height = f' height="{height}"' if height else ""
            if width or height:
                style = f"{width}{height}"
            elif scale:
                style = f" width={scale}%"
            alt = f' alt="{escape(alt)}"' if alt else ""
            body = body.format(filename, style, alt)
            if target:
                body = f'<a href="{escape(target)}">{body}</a>'
            self.body.append(body)


def depart_simpleimage_node_text(self, node):
    """
    What to do when leaving a node *image*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if 'rst' in (self.builder.name, self.builder.format):
        depart_simpleimage_node_rst(self, node)
    elif 'md' in (self.builder.name, self.builder.format):
        depart_simpleimage_node_md(self, node)
    elif 'latex' in (self.builder.name, self.builder.format):
        depart_simpleimage_node_latex(self, node)
    elif node.hasattr("uri"):
        filename = node["uri"]
        width = _clean_value(node["width"])
        height = _clean_value(node["height"])
        scale = node["scale"]
        alt = node["alt"]
        target = node["target"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:  # pragma: no cover
            body = f"unable to find '{filename}'"
            self.body.append(body)
        else:
            body = '\nimage {0}{1}{2}: {3}{4}\n'
            width = f' width="{width}"' if width else ""
            height = f' height="{height}"' if height else ""
            scale = f' scale="{scale}"' if scale else ""
            alt = ' alt="{0}"'.format(alt.replace('"', '\\"')) if alt else ""
            target = ' target="{0}"'.format(
                target.replace('"', '\\"')) if target else ""
            body = body.format(width, height, scale, filename, alt, target)
            self.add_text(body)


def depart_simpleimage_node_latex(self, node):
    """
    What to do when leaving a node *image*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        width = _clean_value(node["width"])
        height = _clean_value(node["height"])
        scale = node["scale"]
        alt = node["alt"]
        full = os.path.join(node["relpath"], node['uri'])
        found = node['abspath'] is not None or node["is_url"]
        if not found:  # pragma: no cover
            body = f"\\textbf{{unable to find '{full}'}}"
            self.body.append(body)
        else:
            body = '\\includegraphics{0}{{{1}}}\n'
            width = f"width={width}" if width else ""
            height = f"height={height}" if height else ""
            scale = f"scale={scale}" if scale else ""
            if width or height or scale:
                dims = [_ for _ in [width, height, scale] if _]
                style = f"[{','.join(dims)}]"
            else:
                style = ""
            alt = ' alt="{0}"'.format(alt.replace('"', '\\"')) if alt else ""
            full = full.replace('\\', '/').replace('_', '\\_')
            body = body.format(style, full)
            self.body.append(body)


def depart_simpleimage_node_rst(self, node):
    """
    What to do when leaving a node *image*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        filename = node["uri"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:  # pragma: no cover
            body = f".. simpleimage:: {filename} [not found]"
            self.add_text(body + self.nl)
        else:
            options = SimpleImageDirective.option_spec
            body = f".. simpleimage:: {filename}"
            self.new_state(0)
            self.add_text(body + self.nl)
            for opt in options:
                v = node.get(opt, None)
                if v:
                    self.add_text(f'    :{opt}: {v}' + self.nl)
            self.end_state(wrap=False)


def depart_simpleimage_node_md(self, node):
    """
    What to do when leaving a node *image*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("uri"):
        filename = node["uri"]
        found = node["abspath"] is not None or node["is_url"]
        if not found:  # pragma: no cover
            body = f"[{filename}](not found)"
            self.add_text(body + self.nl)
        else:
            alt = node.get("alt", "")
            uri = filename
            width = node.get('width', '').replace('px', '')
            height = node.get('height', '').replace('px', '')
            style = f" ={width}x{height}"
            if style == " =x":
                style = ""
            text = f"![{alt}]({uri}{style})"
            self.add_text(text)


def initialize_simpleimages_directive(app):
    """
    Initializes the image directives.
    """
    global DEFAULT_CONFIG

    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(app.config.simpleimages_config)
    app.config.simpleimages_config = config
    app.env.images_mapping = FilenameUniqDict()


def setup(app):
    """
    setup for ``image`` (sphinx)
    """
    global DEFAULT_CONFIG
    if hasattr(app, "add_mapping"):
        app.add_mapping('simpleimages_mapping', simpleimage_node)
    app.add_config_value('simpleimages_config', DEFAULT_CONFIG, 'env')
    app.connect('builder-inited', initialize_simpleimages_directive)
    app.add_node(simpleimage_node,
                 html=(visit_simpleimage_node, depart_simpleimage_node_html),
                 epub=(visit_simpleimage_node, depart_simpleimage_node_html),
                 elatex=(visit_simpleimage_node,
                         depart_simpleimage_node_latex),
                 latex=(visit_simpleimage_node, depart_simpleimage_node_latex),
                 rst=(visit_simpleimage_node, depart_simpleimage_node_rst),
                 md=(visit_simpleimage_node, depart_simpleimage_node_md),
                 text=(visit_simpleimage_node, depart_simpleimage_node_text))

    app.add_directive('simpleimage', SimpleImageDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
