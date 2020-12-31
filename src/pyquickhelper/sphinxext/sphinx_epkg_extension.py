# -*- coding: utf-8 -*-
"""
@file
@brief Defines a way to reference a package or a page in this package.
"""

import sphinx
from docutils import nodes
from .import_object_helper import import_any_object


class epkg_node(nodes.TextElement):

    """
    Defines *epkg* node.
    """
    pass


class ClassStruct:
    """
    Class as struct.
    """

    def __init__(self, **kwargs):
        """
        All arguments are added to the class.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)


def epkg_role(role, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Defines custom role *epkg*. A list of supported urls must be defined in the
    configuration file. It wants to replace something like:

    ::

        `to_html <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_html.html>`_

    By:

    ::

        :epkg:`pandas:DataFrame.to_html`

    It inserts in the configuration the variable:

    ::

        epkg_dictionary = {'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                      ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1))
                                                                                    # 1 for one paraemter
                            '*py': ('https://docs.python.org/3/',
                                    ('https://docs.python.org/3/library/{0}.html#{0}.{1}', 2))
                           }

    If the module name starts with a '*', the anchor does not contain it.
    See also :ref:`l-sphinx-epkg`.
    If no template is found, the role will look into the list of options
    to see if there is one function. It must be the last one.

    ::

        def my_custom_links(input):
            return "string to display", "url"

        epkg_dictionary = {'weird_package': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                      ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1),
                                      my_custom_links)

    However, it is impossible to use a function as a value
    in the configuration because :epkg:`*py:pickle` does not handle
    this scenario (see `PicklingError on environment when config option
    value is a callable <https://github.com/sphinx-doc/sphinx/issues/1424>`_),
    ``my_custom_links`` needs to be replaced by:
    ``("module_where_it_is_defined.function_name", None)``.
    The role *epkg* will import it based on its name.

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    # It extracts the pieces of the text.
    spl = text.split(":")
    if len(spl) == 0:  # pragma: no cover
        msg = inliner.reporter.error("empty value for role epkg", line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    # Configuration.
    env = inliner.document.settings.env
    app = env.app
    config = app.config
    try:
        epkg_dictionary = config.epkg_dictionary
    except AttributeError as e:  # pragma: no cover
        ma = "\n".join(sorted(str(_) for _ in app.config))
        raise AttributeError(
            "unable to find 'epkg_dictionary' in configuration. Available:\n{0}"
            "".format(ma)) from e

    # Supported module?
    modname = spl[0]
    if modname not in epkg_dictionary:
        msg = inliner.reporter.error(
            "Unable to find module '{0}' in epkg_dictionary, existing={1}".format(
                modname, ", ".join(sorted(epkg_dictionary.keys())), line=lineno))
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    if len(spl) == 1:
        value = epkg_dictionary[modname]
        if isinstance(value, tuple):
            if len(value) == 0:  # pragma: no cover
                msg = inliner.reporter.error(
                    "Empty values for module '{0}' in epkg_dictionary.".format(modname))
                prb = inliner.problematic(rawtext, rawtext, msg)
                return [prb], [msg]
            value = value[0]
        anchor, url = modname, value
    else:
        value = epkg_dictionary[modname]
        expected = len(spl) - 1
        found = None
        for tu in value:
            if isinstance(tu, tuple) and len(tu) == 2 and tu[1] == expected:
                found = tu[0]
        if found is None:
            if callable(value[-1]):
                found = value[-1]
            elif isinstance(value[-1], tuple) and len(value[-1]) == 2 and value[-1][-1] is None:
                # It assumes the first parameter is a name of a function.
                namef = value[-1][0]
                if not hasattr(config, namef):
                    # It assumes its name is defined in a package.
                    found = import_any_object(namef)[0]
                else:
                    # Defined in the configuration.
                    found = getattr(config, namef)

        if found is None:  # pragma: no cover
            msg = inliner.reporter.error(
                "Unable to find a tuple with '{0}' parameters in epkg_dictionary['{1}']"
                "".format(expected, modname))
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg]

        if callable(found):
            try:
                anchor, url = found(text)
            except TypeError:
                try:
                    anchor, url = found()(text)
                except Exception as e:  # pragma: no cover
                    raise ValueError(
                        "epkg accepts function or classes with __call__ overloaded. "
                        "Found '{0}'".format(found)) from e
        else:
            url = found.format(*tuple(spl[1:]))
            if spl[0].startswith("*"):
                anchor = ".".join(spl[1:])  # pragma: no cover
            else:
                anchor = ".".join(spl)

    extref = "`{0} <{1}>`__".format(anchor, url)
    node = epkg_node(rawtext=rawtext)
    node['classes'] += ["epkg"]

    memo = ClassStruct(document=inliner.document, reporter=inliner.reporter,
                       language=inliner.language)
    processed, messages = inliner.parse(extref, lineno, memo, node)
    if len(messages) > 0:  # pragma: no cover
        msg = inliner.reporter.error(
            "unable to interpret '{0}', messages={1}".format(
                text, ", ".join(str(_) for _ in messages)), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    node += processed
    return [node], []


def visit_epkg_node(self, node):
    """
    What to do when visiting a node *epkg*.
    """
    pass


def depart_epkg_node(self, node):
    """
    What to do when leaving a node *epkg*.
    """
    pass


def setup(app):
    """
    setup for ``bigger`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('epkg', epkg_node)

    app.add_config_value('epkg_dictionary', {}, 'env')
    app.add_node(epkg_node,
                 html=(visit_epkg_node, depart_epkg_node),
                 epub=(visit_epkg_node, depart_epkg_node),
                 elatex=(visit_epkg_node, depart_epkg_node),
                 latex=(visit_epkg_node, depart_epkg_node),
                 rst=(visit_epkg_node, depart_epkg_node),
                 md=(visit_epkg_node, depart_epkg_node),
                 text=(visit_epkg_node, depart_epkg_node))

    app.add_role('epkg', epkg_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
