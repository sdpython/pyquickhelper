"""
@file
@brief Few helpers for Sphinx

.. versionadded:: 1.4
"""


def info_blocref(app, doctree, fromdocname, class_name,
                 entry_name, class_node, class_node_list):
    """
    log information with Sphinx

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
    for ilist, node in enumerate(doctree.traverse(class_node_list)):
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
    app.info(message)
    return True
