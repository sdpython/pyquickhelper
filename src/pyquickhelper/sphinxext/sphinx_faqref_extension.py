# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to keep track of FAQ.
"""
from docutils import nodes

import sphinx
from .sphinx_blocref_extension import BlocRef, process_blocrefs_generic, BlocRefList, process_blocref_nodes_generic


class faqref_node(nodes.admonition):
    """
    defines ``faqref`` ndoe
    """
    pass


class faqreflist(nodes.General, nodes.Element):
    """
    defines ``faqreflist`` node
    """
    pass


class FaqRef(BlocRef):
    """
    A ``faqref`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title*: a title for the bloc
    * *tag*: a tag to have several categories of blocs (optional)
    * *lid* or *label*: a label to refer to
    * *index*: to add an entry to the index (comma separated)

    Example::

        .. faqref::
            :title: example of a blocref
            :lid: id-you-can-choose

            An example of code:

            ::

                print("mignon")

    Which renders as:

    .. faqref::
        :title: example of a faqref
        :tag: dummy_example2
        :lid: id-you-can-choose2

        An example of code:

        ::

            print("mignon")

    All blocs can be displayed in another page by using ``faqreflist``::

        .. faqreflist::
            :tag: dummy_example2
            :sort: title

    Only blocs tagged as ``dummy_example`` will be inserted here.
    The option ``sort`` sorts items by *title*, *number*, *file*.
    You also link to it by typing ``:ref:'anchor <id-you-can-choose2>'`` which gives
    something like :ref:`link_to_blocref <id-you-can-choose2>`. The link must receive a name.

    .. faqreflist::
        :tag: dummy_example2
        :sort: title
    """

    node_class = faqref_node
    name_sphinx = "faqref"

    def run(self):
        """
        calls run from @see cl BlocRef and add defaut tag
        """
        if "tag" not in self.options:
            self.options["tag"] = "faq"
        return BlocRef.run(self)


def process_faqrefs(app, doctree):
    """
    collect all *faqref* in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    process_blocrefs_generic(
        app, doctree, bloc_name="faqref", class_node=faqref_node)


class FaqRefList(BlocRefList):
    """
    A list of all *faqref* entries, for a specific tag.

    * tag: a tag to filter bloc having this tag
    * sort: a way to sort the blocs based on the title, file, number, default: *title*
    * contents: add a bullet list with links to added blocs

    Example::

        .. faqreflist::
            :tag: issue
            :contents:
    """
    name_sphinx = "faqreflist"
    node_class = faqreflist

    def run(self):
        """
        calls run from @see cl BlocRefList and add default tag if not present
        """
        if "tag" not in self.options:
            self.options["tag"] = "faq"
        return BlocRefList.run(self)


def process_faqref_nodes(app, doctree, fromdocname):
    """
    process_faqref_nodes
    """
    process_blocref_nodes_generic(app, doctree, fromdocname, class_name='faqref',
                                  entry_name="faqmes", class_node=faqref_node,
                                  class_node_list=faqreflist)


def purge_faqrefs(app, env, docname):
    """
    purge_faqrefs
    """
    if not hasattr(env, 'faqref_all_faqrefs'):
        return
    env.faqref_all_faqrefs = [faqref for faqref in env.faqref_all_faqrefs
                              if faqref['docname'] != docname]


def merge_faqref(app, env, docnames, other):
    """
    merge_faqref
    """
    if not hasattr(other, 'faqref_all_faqrefs'):
        return
    if not hasattr(env, 'faqref_all_faqrefs'):
        env.faqref_all_faqrefs = []
    env.faqref_all_faqrefs.extend(other.faqref_all_faqrefs)


def visit_faqref_node(self, node):
    """
    visit_faqref_node
    """
    self.visit_admonition(node)


def depart_faqref_node(self, node):
    """
    depart_faqref_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_faqreflist_node(self, node):
    """
    visit_faqreflist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_faqreflist_node(self, node):
    """
    depart_faqref_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``faqref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('faqref', faqref_node)
        app.add_mapping('faqreflist', faqreflist)

    app.add_config_value('faqref_include_faqrefs', True, 'html')
    app.add_config_value('faqref_link_only', False, 'html')

    app.add_node(faqreflist,
                 html=(visit_faqreflist_node, depart_faqreflist_node),
                 epub=(visit_faqreflist_node, depart_faqreflist_node),
                 elatex=(visit_faqreflist_node, depart_faqreflist_node),
                 latex=(visit_faqreflist_node, depart_faqreflist_node),
                 text=(visit_faqreflist_node, depart_faqreflist_node),
                 md=(visit_faqreflist_node, depart_faqreflist_node),
                 rst=(visit_faqreflist_node, depart_faqreflist_node))
    app.add_node(faqref_node,
                 html=(visit_faqref_node, depart_faqref_node),
                 epub=(visit_faqref_node, depart_faqref_node),
                 elatex=(visit_faqref_node, depart_faqref_node),
                 latex=(visit_faqref_node, depart_faqref_node),
                 text=(visit_faqref_node, depart_faqref_node),
                 md=(visit_faqref_node, depart_faqref_node),
                 rst=(visit_faqref_node, depart_faqref_node))

    app.add_directive('faqref', FaqRef)
    app.add_directive('faqreflist', FaqRefList)
    app.connect('doctree-read', process_faqrefs)
    app.connect('doctree-resolved', process_faqref_nodes)
    app.connect('env-purge-doc', purge_faqrefs)
    app.connect('env-merge-info', merge_faqref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
