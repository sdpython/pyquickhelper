# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to keep track of nb.
"""
from docutils import nodes

import sphinx
from .sphinx_blocref_extension import BlocRef, process_blocrefs_generic, BlocRefList, process_blocref_nodes_generic


class nbref_node(nodes.admonition):
    """
    defines ``nbref`` ndoe
    """
    pass


class nbreflist(nodes.General, nodes.Element):
    """
    defines ``nbreflist`` node
    """
    pass


class NbRef(BlocRef):
    """
    A ``nbref`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title*: a title for the bloc
    * *tag*: a tag to have several categories of blocs, if not specified, it will be equal to *nb*
    * *lid* or *label*: a label to refer to
    * *index*: to add an additional entry to the index (comma separated)

    See :ref:`%encrypt_file <l-nb-encrypt-file>` for an example.
    All entries can be aggregated per tag with ``nbreflist``::

        .. nbreflist::
            :tag: dummy_example2
            :sort: title

    It works the same way as @see cl BlocRef.
    """

    node_class = nbref_node
    name_sphinx = "nbref"

    def run(self):
        """
        calls run from @see cl BlocRef and add index entries by default
        """
        if 'title' not in self.options:
            lineno = self.lineno
            env = self.state.document.settings.env if hasattr(
                self.state.document.settings, "env") else None
            docname = None if env is None else env.docname
            raise KeyError("unable to find 'title' in node {0}\n  File \"{1}\", line {2}\nkeys: {3}".format(
                str(self.__class__), docname, lineno, list(self.options.keys())))
        title = self.options['title']
        if "tag" not in self.options:
            self.options["tag"] = "nb"
        if "index" not in self.options:
            self.options["index"] = title
        else:
            self.options["index"] += "," + title
        return BlocRef.run(self)


def process_nbrefs(app, doctree):
    """
    Collect all *nbref* in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions.
    """
    process_blocrefs_generic(
        app, doctree, bloc_name="nbref", class_node=nbref_node)


class NbRefList(BlocRefList):
    """
    A list of all *nbref* entries, for a specific tag.

    * tag: a tag to have several categories of nbref
    * contents: add a bullet list with links to added blocs

    Example::

        .. nbreflist::
            :tag: issue
    """
    name_sphinx = "nbreflist"
    node_class = nbreflist

    def run(self):
        """
        calls run from @see cl BlocRefList and add default tag if not present
        """
        if "tag" not in self.options:
            self.options["tag"] = "nb"
        return BlocRefList.run(self)


def process_nbref_nodes(app, doctree, fromdocname):
    """
    process_nbref_nodes
    """
    process_blocref_nodes_generic(app, doctree, fromdocname, class_name='nbref',
                                  entry_name="nbmes", class_node=nbref_node,
                                  class_node_list=nbreflist)


def purge_nbrefs(app, env, docname):
    """
    purge_nbrefs
    """
    if not hasattr(env, 'nbref_all_nbrefs'):
        return
    env.nbref_all_nbrefs = [nbref for nbref in env.nbref_all_nbrefs
                            if nbref['docname'] != docname]


def merge_nbref(app, env, docnames, other):
    """
    merge_nbref
    """
    if not hasattr(other, 'nbref_all_nbrefs'):
        return
    if not hasattr(env, 'nbref_all_nbrefs'):
        env.nbref_all_nbrefs = []
    env.nbref_all_nbrefs.extend(other.nbref_all_nbrefs)


def visit_nbref_node(self, node):
    """
    visit_nbref_node
    """
    self.visit_admonition(node)


def depart_nbref_node(self, node):
    """
    *depart_nbref_node*,
    see `sphinx/writers/html.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py>`_.
    """
    self.depart_admonition(node)


def visit_nbreflist_node(self, node):
    """
    *visit_nbreflist_node*,
    see `sphinx/writers/html.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py>`_.
    """
    self.visit_admonition(node)


def depart_nbreflist_node(self, node):
    """
    depart_nbref_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``nbref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('nbref', nbref_node)
        app.add_mapping('nbreflist', nbreflist)

    app.add_config_value('nbref_include_nbrefs', True, 'html')
    app.add_config_value('nbref_link_only', False, 'html')

    app.add_node(nbreflist,
                 html=(visit_nbreflist_node, depart_nbreflist_node),
                 epub=(visit_nbreflist_node, depart_nbreflist_node),
                 elatex=(visit_nbreflist_node, depart_nbreflist_node),
                 latex=(visit_nbreflist_node, depart_nbreflist_node),
                 text=(visit_nbreflist_node, depart_nbreflist_node),
                 md=(visit_nbreflist_node, depart_nbreflist_node),
                 rst=(visit_nbreflist_node, depart_nbreflist_node))
    app.add_node(nbref_node,
                 html=(visit_nbref_node, depart_nbref_node),
                 epub=(visit_nbref_node, depart_nbref_node),
                 elatex=(visit_nbref_node, depart_nbref_node),
                 latex=(visit_nbref_node, depart_nbref_node),
                 text=(visit_nbref_node, depart_nbref_node),
                 md=(visit_nbref_node, depart_nbref_node),
                 rst=(visit_nbref_node, depart_nbref_node))

    app.add_directive('nbref', NbRef)
    app.add_directive('nbreflist', NbRefList)
    app.connect('doctree-read', process_nbrefs)
    app.connect('doctree-resolved', process_nbref_nodes)
    app.connect('env-purge-doc', purge_nbrefs)
    app.connect('env-merge-info', merge_nbref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
