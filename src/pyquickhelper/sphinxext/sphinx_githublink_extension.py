# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to display a link on github.

.. versionadded:: 1.5
"""
import os
import sphinx
from docutils import nodes
from docutils.parsers.rst.roles import set_classes


class githublink_node(nodes.Element):

    """
    defines *githublink* node
    """
    pass


def make_link_node(rawtext, app, path, anchor, lineno, options):
    """
    Create a link to a github file.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param path: path to filename
    :param lineno: line number
    :param anchor: anchor
    :param options: Options dictionary passed to role func.
    """
    try:
        opt = app.config.github_options
        if not opt:
            raise AttributeError
    except AttributeError as err:
        raise ValueError(
            'github_options configuration value is not set (%s)' % str(err))
    user = opt["user"]
    project = opt["project"]
    ref = "https://github.com/{0}/{1}/blob/master/{2}#{3}".format(
        user, project, path.replace("\\", "/"), lineno)
    set_classes(options)
    node = nodes.reference(rawtext, anchor, refuri=ref, **options)
    return node


def githublink_role(role, rawtext, text, lineno, inliner,
                    options={}, content=[]):
    """
    Defines custom role *githublink*. The following instruction add
    a link to the documentation on github.

        :githublink:

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    :return: ``[node], []``
    """
    if not rawtext or len(rawtext) == 0:
        rawtext = "github"
    app = inliner.document.settings.env.app
    docname = inliner.document.settings.env.docname
    folder = docname
    git = os.path.join(folder, ".git")
    while len(folder) > 0 and not os.path.exists(git):
        folder = os.path.split(folder)[0]
        git = os.path.join(folder, ".git")
    path = docname.replace(git, "").strip("\\/")

    try:
        node = make_link_node(rawtext, app, path, lineno, rawtext, options)
    except (ValueError, AttributeError) as e:
        msg = inliner.reporter.error('github_options must be set to a dictionary with keys (user, project)\n%s' % str(e),
                                     line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    return [node], []


def setup(app):
    """
    setup for ``githublink`` (sphinx)
    """
    app.add_role('githublink', githublink_role)
    app.add_config_value('github_options', None, 'env')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
