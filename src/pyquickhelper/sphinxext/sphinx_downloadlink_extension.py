# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to show a link instead of downloading it.
This extension does not work for :epkg:`Sphinx` < 1.8.

.. versionadded:: 1.8
"""
import os
import sphinx
from docutils import nodes
from sphinx import addnodes
from sphinx.environment.collectors import EnvironmentCollector
from sphinx.util import status_iterator, ensuredir, copyfile
try:
    from sphinx.util import relative_path
except ImportError:
    # Sphinx >= 3.0.0
    from docutils.utils import relative_path
from sphinx.util import logging
from sphinx.locale import __

try:
    from sphinx.util import DownloadFiles
except ImportError:
    # Sphinx < 1.8
    class DownloadFiles(dict):
        def purge_doc(self, *args, **kwargs):
            pass

        def merge_other(self, *args, **kwargs):
            pass

        def add_file(self, docname, ref_filename):
            self[docname] = (docname, ref_filename)


class downloadlink_node(*addnodes.download_reference.__bases__):

    """
    Defines *download_reference* node.
    """
    pass


def process_downloadlink_role(role, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Defines custom role *downloadlink*. The following instructions defines
    a link which can be displayed or hidden based on the output format.
    The following directive creates a link to ``page.html`` only
    for the HTML output, it also copies the files next to the source
    and not in the folder ``_downloads``. The link does not push the user
    to download the file but to see it.

    ::

        :downloadlink:`html::page.html`

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.

    The role only works for :epkg:`Sphinx` 1.8+.
    """
    if options is None:
        options = {}
    if content is None:
        content = []

    if '<' in text and '>' in text:
        sep = text.split('<')
        if len(sep) != 2:
            msg = inliner.reporter.error(
                "Unable to interpret '{0}' for downloadlink".format(text))
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg]
        name = sep[0].strip()
        link = sep[1].strip('<>')
        anchor = name
    else:
        name = text
        link = text
        anchor = os.path.split(text)[-1]
        if '::' in anchor:
            anchor = anchor.split('::')[-1].strip()

    if '::' in link:
        spl = link.split('::')
        if len(spl) != 2:
            msg = inliner.reporter.error(
                "Unable to interpret '{0}' for downloadlink".format(text))
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg]
        out, src = spl
    else:
        ext = os.path.splitext(link)[-1]
        out, src = ext.strip('.'), link

    if "::" in src:
        raise RuntimeError("Value '{0}' is unexpected.".format(src))

    name = name.strip()
    node = downloadlink_node(text=anchor, raw=text)
    node['class'] = 'internal'
    node['format'] = out
    node['filename'] = src
    node['reftarget'] = src
    node['anchor'] = anchor

    logger = logging.getLogger("downloadlink")
    logger.info("[downloadlink] node '{0}'".format(str(node)))

    return [node], []


def visit_downloadlink_node_html(self, node):
    """
    Converts node *downloadlink* into :epkg:`html`.
    """
    if node['format'] != 'html':
        raise nodes.SkipNode

    logger = logging.getLogger("downloadlink")
    logger.info("[downloadlink] HTML '{0}'".format(str(node)))

    atts = {'class': 'reference'}

    if not self.builder.download_support:
        self.context.append('')
    elif 'refuri' in node:
        atts['class'] += ' external'
        atts['href'] = node['refuri']
        self.body.append(self.starttag(node, 'a', '', **atts))
        self.context.append('</a>')
    elif 'filename' in node:
        atts['class'] += ' internal'
        atts['href'] = node['filename']
        self.body.append(self.starttag(node, 'a', '', **atts))
        self.context.append('</a>')
    else:
        self.context.append('')


def depart_downloadlink_node_html(self, node):
    """
    Converts node *downloadlink* into :epkg:`html`.
    """
    self.body.append(self.context.pop())


def visit_downloadlink_node_latex(self, node):
    """
    Does notthing.
    """
    pass


def depart_downloadlink_node_latex(self, node):
    """
    Does notthing.
    """
    pass


def visit_downloadlink_node_text(self, node):
    """
    Does notthing.
    """
    if self.output_format in ('rst', 'md', "latex", "elatex"):
        raise RuntimeError("format should not be '{0}' for base_class {1}".format(
            self.output_format, self.base_class))


def depart_downloadlink_node_text(self, node):
    """
    Does notthing.
    """
    if self.output_format in ('rst', 'md', "latex", "elatex"):
        raise RuntimeError(
            "format should not be '{0}'".format(self.output_format))


def visit_downloadlink_node_rst(self, node):
    """
    Converts node *downloadlink* into :epkg:`rst`.
    """
    logger = logging.getLogger("downloadlink")
    logger.info("[downloadlink] RST '{0}'".format(str(node)))

    if node['format']:
        self.add_text(":downloadlink:`{0} <{1}::{2}>`".format(
            node["anchor"], node["format"], node["filename"]))
    else:
        self.add_text(":downloadlink:`{0} <{0}::{1}>`".format(
            node["anchor"], node["filename"]))
    raise nodes.SkipNode


def depart_downloadlink_node_rst(self, node):
    """
    Converts node *downloadlink* into :epkg:`rst`.
    """
    pass


def visit_downloadlink_node_md(self, node):
    """
    Converts node *downloadlink* into :epkg:`md`.
    """
    self.add_text("[{0}]({1})".format(node["anchor"], node["filename"]))
    raise nodes.SkipNode


def depart_downloadlink_node_md(self, node):
    """
    Converts node *downloadlink* into :epkg:`md`.
    """
    pass


class DownloadLinkFileCollector(EnvironmentCollector):
    """Download files collector for *sphinx.environment*."""

    def check_attr(self, env):
        if not hasattr(env, 'dllinkfiles'):
            env.dllinkfiles = DownloadFiles()

    def clear_doc(self, app, env, docname):
        self.check_attr(env)
        if env.dllinkfiles and len(env.dllinkfiles) > 0:
            env.dllinkfiles.purge_doc(docname)

    def merge_other(self, app, env, docnames, other):
        logger = logging.getLogger("downloadlink")
        logger.info("[downloadlink] merge")
        self.check_attr(env)
        env.dllinkfiles.merge_other(docnames, other.dllinkfiles)

    def process_doc(self, app, doctree):
        """Process downloadable file paths. """
        self.check_attr(app.env)
        nb = 0
        for node in doctree.traverse(downloadlink_node):
            format = node["format"]
            if format and format != app.builder.format:
                continue
            nb += 1
            dest = os.path.split(app.env.docname)[0]
            name = node["filename"]
            rel_filename = os.path.join(dest, name)
            app.env.dependencies[app.env.docname].add(rel_filename)
            node['dest'] = app.env.dllinkfiles.add_file(
                app.env.docname, rel_filename)
        if nb > 0:
            logger = logging.getLogger("downloadlink")
            logger.info("[downloadlink] processed {0}".format(nb))


def copy_download_files(app, exc):
    """
    Copies all files mentioned with role *downloadlink*.
    """
    if exc:
        builder = app.builder
        logger = logging.getLogger("downloadlink")
        mes = "Builder format '{0}'-'{1}', unable to copy file due to {2}".format(
            builder.format, builder.__class__.__name__, exc)
        logger.warning(mes)
        return

    def to_relpath(f):
        return relative_path(app.srcdir, f)
    # copy downloadable files
    builder = app.builder
    if builder.env.dllinkfiles:
        logger = logging.getLogger("downloadlink")
        logger.info("[downloadlink] copy_download_files")
        for src in status_iterator(builder.env.dllinkfiles, __('copying downloadable(link) files... '),
                                   "brown", len(
                                       builder.env.dllinkfiles), builder.app.verbosity,
                                   stringify_func=to_relpath):
            docname, dest = builder.env.dllinkfiles[src]
            relpath = set(os.path.dirname(dn) for dn in docname)
            for rel in relpath:
                dest = os.path.join(builder.outdir, rel)
                ensuredir(os.path.dirname(dest))
                shortname = os.path.split(src)[-1]
                dest = os.path.join(dest, shortname)
                name = os.path.join(builder.srcdir, src)
                try:
                    copyfile(name, dest)
                    logger.info(
                        "[downloadlink] copy '{0}' to '{1}'".format(name, dest))
                except FileNotFoundError:
                    mes = "Builder format '{0}'-'{3}', unable to copy file '{1}' into {2}'".format(
                        builder.format, name, dest, builder.__class__.__name__)
                    logger.warning(
                        "[downloadlink] cannot copy '{0}' to '{1}'".format(name, dest))


def setup(app):
    """
    setup for ``bigger`` (sphinx)
    """
    app.add_env_collector(DownloadLinkFileCollector)

    if hasattr(app, "add_mapping"):
        app.add_mapping('downloadlink', downloadlink_node)

    app.connect('build-finished', copy_download_files)
    app.add_node(downloadlink_node,
                 html=(visit_downloadlink_node_html,
                       depart_downloadlink_node_html),
                 epub=(visit_downloadlink_node_html,
                       depart_downloadlink_node_html),
                 latex=(visit_downloadlink_node_latex,
                        depart_downloadlink_node_latex),
                 elatex=(visit_downloadlink_node_latex,
                         depart_downloadlink_node_latex),
                 text=(visit_downloadlink_node_text,
                       depart_downloadlink_node_text),
                 md=(visit_downloadlink_node_md,
                     depart_downloadlink_node_md),
                 rst=(visit_downloadlink_node_rst, depart_downloadlink_node_rst))

    app.add_role('downloadlink', process_downloadlink_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
