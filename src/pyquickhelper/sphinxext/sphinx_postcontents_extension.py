# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension which proposes a new version of ``.. contents::``
which takes into account titles dynamically added.
"""
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging

import sphinx
from sphinx.util.logging import getLogger
from docutils.parsers.rst import Directive
from .sphinx_ext_helper import traverse, NodeLeave, WrappedNode


class postcontents_node(nodes.paragraph):
    """
    defines ``postcontents`` node
    """
    pass


class PostContentsDirective(Directive):
    """
    Defines a sphinx extension which proposes a new version of ``.. contents::``
    which takes into account titles dynamically added.

    Example::

        .. postcontents::

        title 1
        =======

        .. runpython::
            :rst:

            print("title 2")
            print("=======")

    Which renders as:

    .. contents::
        :local:

        title 1
        =======

        title 2
        =======

    Directive ``.. contents::`` only considers titles defined by the user,
    not titles dynamically created by another directives.

    .. warning:: It is not recommended to dynamically insert
        such a directive. It is not recursive.
    """

    node_class = postcontents_node
    name_sphinx = "postcontents"
    has_content = True
    option_spec = {'depth': directives.unchanged,
                   'local': directives.unchanged}

    def run(self):
        """
        Just add a @see cl postcontents_node.

        @return                         list of nodes or list of nodes, container
        """
        lineno = self.lineno

        settings = self.state.document.settings
        env = settings.env if hasattr(settings, "env") else None
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
        else:
            docname = ''  # pragma: no cover

        node = postcontents_node()
        node['pclineno'] = lineno
        node['pcdocname'] = docname
        node["pcprocessed"] = 0
        node["depth"] = self.options.get("depth", "*")
        node["local"] = self.options.get("local", None)
        return [node]


def process_postcontents(app, doctree):
    """
    Collect all *postcontents* in the environment.
    Look for the section or document which contain them.
    Put them into the variable *postcontents_all_postcontents* in the config.
    """
    logger = getLogger('postcontents')
    env = app.builder.env
    attr = 'postcontents_all_postcontents'
    if not hasattr(env, attr):
        setattr(env, attr, [])
    attr_list = getattr(env, attr)
    for node in doctree.traverse(postcontents_node):
        # It looks for a section or document which contains the directive.
        parent = node
        while not isinstance(parent, (nodes.document, nodes.section)):
            parent = node.parent
        node["node_section"] = WrappedNode(parent)
        node["pcprocessed"] += 1
        node["processed"] = 1
        attr_list.append(node)
        logger.info("[postcontents] in '{}.rst' line={} found:{}".format(
            node['pcdocname'], node['pclineno'], node['pcprocessed']))
        _modify_postcontents(node, "postcontentsP")


def _modify_postcontents(node, event):
    node["transformed"] = 1
    logger = getLogger('postcontents')
    logger.info("[{}] in '{}.rst' line={} found:{}".format(
        event, node['pcdocname'], node['pclineno'], node['pcprocessed']))
    parent = node["node_section"]
    sections = []
    main_par = nodes.paragraph()
    node += main_par
    roots = [main_par]
    # depth = int(node["depth"]) if node["depth"] != '*' else 20
    memo = {}
    level = 0

    for _, subnode in traverse(parent):
        if isinstance(subnode, nodes.section):
            if len(subnode["ids"]) == 0:
                subnode["ids"].append("postid-{}".format(id(subnode)))
            nid = subnode["ids"][0]
            if nid in memo:
                raise KeyError(  # pragma: no cover
                    "node was already added '{0}'".format(nid))
            logger.info("[{}]  {}section id '{}'".format(
                event, "  " * level, nid))
            level += 1
            memo[nid] = subnode
            bli = nodes.bullet_list()
            roots[-1] += bli
            roots.append(bli)
            sections.append(subnode)
        elif isinstance(subnode, nodes.title):
            logger.info("[{}]  {}title '{}'".format(
                event, "  " * level, subnode.astext()))
            par = nodes.paragraph()
            ref = nodes.reference(refid=sections[-1]["ids"][0],
                                  reftitle=subnode.astext(),
                                  text=subnode.astext())
            par += ref
            bullet = nodes.list_item()
            bullet += par
            roots[-1] += bullet
        elif isinstance(subnode, NodeLeave):
            parent = subnode.parent
            if isinstance(parent, nodes.section):
                ids = None if len(parent["ids"]) == 0 else parent["ids"][0]
                if ids in memo:
                    level -= 1
                    logger.info("[{}]  {}end of section '{}'".format(
                        event, "  " * level, parent["ids"]))
                    sections.pop()
                    roots.pop()


def transform_postcontents(app, doctree, fromdocname):
    """
    The function is called by event ``'doctree_resolved'``. It looks for
    every section in page stored in *postcontents_all_postcontents*
    in the configuration and builds a short table of contents.
    The instruction ``.. contents::`` is resolved before every directive in
    the page is executed, the instruction ``.. postcontents::`` is resolved after.

    @param      app             Sphinx application
    @param      doctree         doctree
    @param      fromdocname     docname

    Thiis directive should be used if you need to capture a section
    which was dynamically added by another one. For example @see cl RunPythonDirective
    calls function ``nested_parse_with_titles``. ``.. postcontents::`` will capture the
    new section this function might eventually add to the page.
    For some reason, this function does not seem to be able to change
    the doctree (any creation of nodes is not taken into account).
    """
    logger = logging.getLogger("postcontents")

    # check this is something to process
    env = app.builder.env
    attr_name = 'postcontents_all_postcontents'
    if not hasattr(env, attr_name):
        setattr(env, attr_name, [])
    post_list = getattr(env, attr_name)
    if len(post_list) == 0:
        # No postcontents found.
        return

    for node in post_list:
        if node["pcprocessed"] != 1:
            logger.warning("[postcontents] no first loop was ever processed: 'pcprocessed'={0} , File '{1}', line {2}".format(
                node["pcprocessed"], node["pcdocname"], node["pclineno"]))
            continue
        if len(node.children) > 0:
            # already processed
            continue

        _modify_postcontents(node, "postcontentsT")


def visit_postcontents_node(self, node):
    """
    does nothing
    """
    pass


def depart_postcontents_node(self, node):
    """
    does nothing
    """
    pass


def setup(app):
    """
    setup for ``postcontents`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('postcontents', postcontents_node)

    app.add_node(postcontents_node,
                 html=(visit_postcontents_node, depart_postcontents_node),
                 epub=(visit_postcontents_node, depart_postcontents_node),
                 elatex=(visit_postcontents_node, depart_postcontents_node),
                 latex=(visit_postcontents_node, depart_postcontents_node),
                 text=(visit_postcontents_node, depart_postcontents_node),
                 md=(visit_postcontents_node, depart_postcontents_node),
                 rst=(visit_postcontents_node, depart_postcontents_node))

    app.add_directive('postcontents', PostContentsDirective)
    app.connect('doctree-read', process_postcontents)
    app.connect('doctree-resolved', transform_postcontents)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
