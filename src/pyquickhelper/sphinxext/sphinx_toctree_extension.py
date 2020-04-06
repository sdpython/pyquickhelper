# -*- coding: utf-8 -*-
"""
@file
@brief Overwrites `toctree <http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree>`_
directive to get catch exceptions when a document is processed inline.
"""
from docutils.parsers.rst import directives
from docutils import nodes
import sphinx
from sphinx.directives.other import TocTree, int_or_nothing
from sphinx.util.nodes import explicit_title_re, set_source_info
from sphinx import addnodes
from sphinx.util import url_re, docname_join
from sphinx.environment.collectors.toctree import TocTreeCollector
from sphinx.util import logging
from sphinx.transforms import SphinxContentsFilter
from sphinx.environment.adapters.toctree import TocTree as AdaptersTocTree
from sphinx.util.matching import patfilter
from ..texthelper import compare_module_version


class CustomTocTree(TocTree):
    """
    Overwrites `toctree
    <http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree>`_.
    The code is located at
    `sphinx/directives/other.py
    <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/directives/other.py#L38>`_.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'maxdepth': int,
        'name': directives.unchanged,
        'caption': directives.unchanged_required,
        'glob': directives.flag,
        'hidden': directives.flag,
        'includehidden': directives.flag,
        'numbered': int_or_nothing,
        'titlesonly': directives.flag,
        'reversed': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        suffixes = env.config.source_suffix
        glob = 'glob' in self.options

        ret = []
        # (title, ref) pairs, where ref may be a document, or an external link,
        # and title may be None if the document's title is to be used
        entries = []
        includefiles = []
        all_docnames = env.found_docs.copy()
        # don't add the currently visited file in catch-all patterns
        try:
            all_docnames.remove(env.docname)
        except KeyError:
            if env.docname == "<<string>>":
                # This comes from rst2html.
                pass
            else:
                logger = logging.getLogger("CustomTocTreeCollector")
                logger.warning(
                    "[CustomTocTreeCollector] unable to remove document '{0}' from {1}".format(
                        env.docname, ", ".join(all_docnames)))

        for entry in self.content:
            if not entry:
                continue
            if glob and ('*' in entry or '?' in entry or '[' in entry):
                patname = docname_join(env.docname, entry)
                docnames = sorted(patfilter(all_docnames, patname))
                for docname in docnames:
                    all_docnames.remove(docname)  # don't include it again
                    entries.append((None, docname))
                    includefiles.append(docname)
                if not docnames:
                    ret.append(self.state.document.reporter.warning(
                        '[CustomTocTree] glob pattern %r didn\'t match any documents'
                        % entry, line=self.lineno))
            else:
                # look for explicit titles ("Some Title <document>")
                m = explicit_title_re.match(entry)
                if m:
                    ref = m.group(2)
                    title = m.group(1)
                    docname = ref
                else:
                    ref = docname = entry
                    title = None
                # remove suffixes (backwards compatibility)
                for suffix in suffixes:
                    if docname.endswith(suffix):
                        docname = docname[:-len(suffix)]
                        break
                # absolutize filenames
                docname = docname_join(env.docname, docname)
                if url_re.match(ref) or ref == 'self':
                    entries.append((title, ref))
                elif docname not in env.found_docs:
                    ret.append(self.state.document.reporter.warning(
                        '[CustomTocTree] contains reference to nonexisting '
                        'document %r' % docname, line=self.lineno))
                    env.note_reread()
                else:
                    all_docnames.discard(docname)
                    entries.append((title, docname))
                    includefiles.append(docname)
        subnode = addnodes.toctree()
        subnode['parent'] = env.docname
        # entries contains all entries (self references, external links etc.)
        if 'reversed' in self.options:
            entries.reverse()
        subnode['entries'] = entries
        # includefiles only entries that are documents
        subnode['includefiles'] = includefiles
        subnode['maxdepth'] = self.options.get('maxdepth', -1)
        subnode['caption'] = self.options.get('caption')
        subnode['glob'] = glob
        subnode['hidden'] = 'hidden' in self.options
        subnode['includehidden'] = 'includehidden' in self.options
        subnode['numbered'] = self.options.get('numbered', 0)
        subnode['titlesonly'] = 'titlesonly' in self.options
        set_source_info(self, subnode)
        wrappernode = nodes.compound(classes=['toctree-wrapper'])
        wrappernode.append(subnode)
        self.add_name(wrappernode)
        ret.append(wrappernode)
        return ret


class CustomTocTreeCollector(TocTreeCollector):
    """
    Overwrites `TocTreeCollector <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/environment/collectors/toctree.py>`_.
    """

    # def __init__(self, *p, **kw):
    #     TocTreeCollector.__init__(self, *p, **kw)
    #    assert self.listener_ids is None

    def enable(self, app):
        # It needs to disable TocTreeCollector.
        app.disconnect_env_collector("TocTreeCollector", exc=False)
        assert self.listener_ids is None
        self.listener_ids = {
            'doctree-read': app.connect('doctree-read', self.process_doc),
            'env-merge-info': app.connect('env-merge-info', self.merge_other),
            'env-purge-doc': app.connect('env-purge-doc', self.clear_doc),
            'env-get-updated': app.connect('env-get-updated', self.get_updated_docs),
            'env-get-outdated': app.connect('env-get-outdated', self.get_outdated_docs),
        }

    def process_doc(self, app, doctree):
        """Build a TOC from the doctree and store it in the inventory."""
        docname = app.env.docname
        numentries = [0]  # nonlocal again...

        def traverse_in_section(node, cls):
            """Like traverse(), but stay within the same section."""
            result = []
            if isinstance(node, cls):
                result.append(node)
            for child in node.children:
                if isinstance(child, nodes.section):
                    continue
                result.extend(traverse_in_section(child, cls))
            return result

        def build_toc(node, depth=1):
            """Builds toc."""
            entries = []
            for sectionnode in node:
                # find all toctree nodes in this section and add them
                # to the toc (just copying the toctree node which is then
                # resolved in self.get_and_resolve_doctree)
                if isinstance(sectionnode, addnodes.only):
                    onlynode = addnodes.only(expr=sectionnode['expr'])
                    blist = build_toc(sectionnode, depth)
                    if blist:
                        onlynode += blist.children
                        entries.append(onlynode)
                    continue
                if not isinstance(sectionnode, nodes.section):
                    for toctreenode in traverse_in_section(sectionnode,
                                                           addnodes.toctree):
                        item = toctreenode.copy()
                        entries.append(item)
                        # important: do the inventory stuff
                        CustomAdaptersTocTree(app.env).note(
                            docname, toctreenode)
                    continue
                title = sectionnode[0]
                # copy the contents of the section title, but without references
                # and unnecessary stuff
                visitor = SphinxContentsFilter(doctree)
                title.walkabout(visitor)
                nodetext = visitor.get_entry_text()

                if not numentries[0]:
                    # for the very first toc entry, don't add an anchor
                    # as it is the file's title anyway
                    anchorname = ''
                else:
                    if len(sectionnode['ids']) == 0:
                        an = "unkown-anchor"
                        logger = logging.getLogger("CustomTocTreeCollector")
                        logger.warning(
                            "[CustomTocTreeCollector] no id for node '{0}'".format(sectionnode))
                    else:
                        an = sectionnode['ids'][0]
                    anchorname = '#' + an

                numentries[0] += 1
                # make these nodes:
                # list_item -> compact_paragraph -> reference
                reference = nodes.reference(
                    '', '', internal=True, refuri=docname,
                    anchorname=anchorname, *nodetext)
                para = addnodes.compact_paragraph('', '', reference)
                item = nodes.list_item('', para)
                sub_item = build_toc(sectionnode, depth + 1)
                item += sub_item
                entries.append(item)
            if entries:
                return nodes.bullet_list('', *entries)
            return []
        toc = build_toc(doctree)
        if toc:
            app.env.tocs[docname] = toc
        else:
            app.env.tocs[docname] = nodes.bullet_list('')
        app.env.toc_num_entries[docname] = numentries[0]


class CustomAdaptersTocTree(AdaptersTocTree):
    ":epkg:`Sphinx` directive"
    pass


def setup(app):
    """
    Setup for ``toctree`` and ``toctree2`` (sphinx).
    """
    app.add_directive('toctree2', CustomTocTree)
    directives.register_directive('toctree2', CustomTocTree)

    if hasattr(app, 'disconnect_env_collector'):
        # If it can disable the previous TocTreeCollector,
        # it connects a new collector to the app,
        # it disables the previous one.
        directives.register_directive('toctree', CustomTocTree)
        if compare_module_version(sphinx.__version__, '1.8') < 0:
            app.add_directive('toctree', CustomTocTree)
        else:
            app.add_directive('toctree', CustomTocTree, override=True)
        app.add_env_collector(CustomTocTreeCollector)

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
