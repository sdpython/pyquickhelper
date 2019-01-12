# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to keep track of ex.
"""
from docutils import nodes

import sphinx
from .sphinx_blocref_extension import BlocRef, process_blocrefs_generic, BlocRefList, process_blocref_nodes_generic


class exref_node(nodes.admonition):
    """
    defines ``exref`` ndoe
    """
    pass


class exreflist(nodes.General, nodes.Element):
    """
    defines ``exreflist`` node
    """
    pass


class ExRef(BlocRef):
    """
    A ``exref`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title*: a title for the bloc
    * *tag*: a tag to have several categories of blocs (optional)
    * *lid* or *label*: a label to refer to
    * *index*: to add an entry to the index (comma separated)

    Example::

        .. exref::
            :title: example of a blocref
            :lid: id-you-can-choose6

            An example of code:

            ::

                print("mignon")

    Which renders as:

    .. exref::
        :title: example of a exref
        :tag: dummy_example6
        :lid: id-you-can-choose6

        An example of code:

        ::

            print("mignon")

    All blocs can be displayed in another page by using ``exreflist``::

        .. exreflist::
            :tag: dummy_example6
            :sort: title

    Only blocs tagged as ``dummy_example`` will be inserted here.
    The option ``sort`` sorts items by *title*, *number*, *file*.
    You also link to it by typing ``:ref:'anchor <id-you-can-choose2>'`` which gives
    something like :ref:`link_to_blocref <id-you-can-choose2>`. The link must receive a name.

    .. exreflist::
        :tag: dummy_example6
        :sort: title
    """

    node_class = exref_node
    name_sphinx = "exref"

    def run(self):
        """
        calls run from @see cl BlocRef and add defaut tag
        """
        if "tag" not in self.options:
            self.options["tag"] = "ex"
        return BlocRef.run(self)


def process_exrefs(app, doctree):
    """
    collect all *exref* in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    process_blocrefs_generic(
        app, doctree, bloc_name="exref", class_node=exref_node)


class ExRefList(BlocRefList):
    """
    A list of all *exref* entries, for a specific tag.

    * tag: a tag to filter bloc having this tag
    * sort: a way to sort the blocs based on the title, file, number, default: *title*
    * contents: add a bullet list with links to added blocs

    Example::

        .. exreflist::
            :tag: issue
    """
    name_sphinx = "exreflist"
    node_class = exreflist

    def run(self):
        """
        calls run from @see cl BlocRefList and add default tag if not present
        """
        if "tag" not in self.options:
            self.options["tag"] = "ex"
        return BlocRefList.run(self)


def process_exref_nodes(app, doctree, fromdocname):
    """
    process_blocref_nodes
    """
    process_blocref_nodes_generic(app, doctree, fromdocname, class_name='exref',
                                  entry_name="exmes", class_node=exref_node,
                                  class_node_list=exreflist)


def purge_exrefs(app, env, docname):
    """
    purge_exrefs
    """
    if not hasattr(env, 'exref_all_exrefs'):
        return
    env.exref_all_exrefs = [exref for exref in env.exref_all_exrefs
                            if exref['docname'] != docname]


def merge_exref(app, env, docnames, other):
    """
    merge_exref
    """
    if not hasattr(other, 'exref_all_exrefs'):
        return
    if not hasattr(env, 'exref_all_exrefs'):
        env.exref_all_exrefs = []
    env.exref_all_exrefs.extend(other.exref_all_exrefs)


def visit_exref_node(self, node):
    """
    visit_exref_node
    """
    self.visit_admonition(node)


def depart_exref_node(self, node):
    """
    depart_exref_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_exreflist_node(self, node):
    """
    visit_exreflist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_exreflist_node(self, node):
    """
    depart_exref_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``exref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('exref', exref_node)
        app.add_mapping('exreflist', exreflist)

    app.add_config_value('exref_include_exrefs', True, 'html')
    app.add_config_value('exref_link_only', False, 'html')

    app.add_node(exreflist,
                 html=(visit_exreflist_node, depart_exreflist_node),
                 epub=(visit_exreflist_node, depart_exreflist_node),
                 elatex=(visit_exreflist_node, depart_exreflist_node),
                 latex=(visit_exreflist_node, depart_exreflist_node),
                 tex=(visit_exreflist_node, depart_exreflist_node),
                 text=(visit_exreflist_node, depart_exreflist_node),
                 md=(visit_exreflist_node, depart_exreflist_node),
                 rst=(visit_exreflist_node, depart_exreflist_node))
    app.add_node(exref_node,
                 html=(visit_exref_node, depart_exref_node),
                 epub=(visit_exref_node, depart_exref_node),
                 elatex=(visit_exref_node, depart_exref_node),
                 latex=(visit_exref_node, depart_exref_node),
                 tex=(visit_exref_node, depart_exref_node),
                 text=(visit_exref_node, depart_exref_node),
                 md=(visit_exref_node, depart_exref_node),
                 rst=(visit_exref_node, depart_exref_node))

    app.add_directive('exref', ExRef)
    app.add_directive('exreflist', ExRefList)
    app.connect('doctree-read', process_exrefs)
    app.connect('doctree-resolved', process_exref_nodes)
    app.connect('env-purge-doc', purge_exrefs)
    app.connect('env-merge-info', merge_exref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
