"""
@file
@brief Few helpers for :epkg:`Sphinx`.
"""
import logging


def info_blocref(app, doctree, fromdocname, class_name,
                 entry_name, class_node, class_node_list):
    """
    Log information with :epkg:`Sphinx`.

    @param      app                 application (Sphinx)
    @param      doctree             document tree
    @param      fromdocname         document currently being compiled
    @param      class_name          name of the node
    @param      entry_name          entry name in ``TITLES``
    @param      class_node          class node (@see cl blocref_node)
    @param      class_node_list     class node list (@see cl blocreflist)
    """
    incconf = '%s_include_%ss' % (class_name, class_name)
    rows2 = []
    for node in doctree.traverse(class_node_list):
        breftag = node.get("breftag", None)
        rows2.append("tag={0} do={1}".format(breftag, app.config[incconf]))
    if len(rows2) == 0:
        return False

    attr_name = '%s_all_%ss' % (class_name, class_name)
    env = app.builder.env
    if hasattr(env, attr_name):
        bloc_list_env = getattr(env, attr_name)
    else:
        bloc_list_env = []

    rows = ["  [info_blocref]",
            "len(bloc_list_env)={0}".format(len(bloc_list_env)), ]
    rows.extend(rows2)
    rows.extend(["fromdocname='{0}'".format(fromdocname),
                 "entry_name='{0}'".format(entry_name),
                 "class_name='{0}'".format(class_name),
                 "class_node='{0}'".format(class_node),
                 "class_node_list='{0}'".format(class_node_list),
                 "doctree='{0}'".format(type(doctree)),
                 "#doctree={0}".format(len(doctree))])
    message = " ".join(rows)
    logger = logging.getLogger("info_blocref")
    logger.info(message)
    return True


def sphinx_lang(env, default_value='en'):
    """
    Returns the language defined in the configuration file.

    @param      env             environment
    @param      default_value   default value
    @return                     language
    """
    if hasattr(env, "settings"):
        settings = env.settings
        if hasattr(settings, "language_code"):
            lang = env.settings.language_code
        else:
            lang = "en"
    else:
        settings = None
        lang = "en"
    return lang


class TinyNode:
    """
    Returned by @see fn traverse.
    """

    def __init__(self, parent):
        """
        Create a note

        @param      parent      parent node
        """
        self.parent = parent


class NodeEnter(TinyNode):
    """
    Returned by function @see fn traverse.
    """
    pass


class NodeLeave(TinyNode):
    """
    Returned by function @see fn traverse.
    """
    pass


class WrappedNode:
    """
    Wraps a docutils node.
    """

    def __init__(self, node):
        self.node = node


def traverse(node, depth=0):
    """
    Enumerates through all children but insert a node whenever
    digging or leaving the childrens nodes.

    @param      node        node (from doctree)
    @param      depth       current depth
    @return                 enumerate (depth, node)

    @see cl NodeEnter and @see cl NodeLeave are returned whenever entering or leaving nodes.
    """
    if isinstance(node, WrappedNode):
        node = node.node
    ne = NodeEnter(node)
    nl = NodeLeave(node)
    yield (depth, ne)
    yield (depth, node)
    for n in node.children:
        for r in traverse(n, depth + 1):
            yield r
    yield (depth, nl)
