# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to display a link on github.

.. versionadded:: 1.5


.. todoext::
    :title: add link to github code for each function, class...
    :cost: 2
    :hidden:
    :date: 2016-11-20
    :tag: done

    Add a link to the source on GitHub in the documentation for every function,
    class, notebook.
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


def make_link_node(rawtext, app, path, anchor, lineno, options, settings):
    """
    Create a link to a github file.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param path: path to filename
    :param lineno: line number
    :param anchor: anchor
    :param options: Options dictionary passed to role func.
    :param settings: settings

    The configuration of the documentation must contain
    a member ``githublink_options`` (a dictionary) which contains the following fields
    either the pair:

    * *user*, *project*: to form the url
      ``https://github.com/<user>/<project>``

    Or the field:

    * *processor*: function with takes a path and a line number and returns an url and an anchor name

    Example:

    ::

        def processor_github(path, lineno):
            url = "https://github.com/{0}/{1}/blob/master/{2}".format(user, project, path)
            if lineno:
                url += "#L{0}".format(lineno)
            return url, "source on GitHub"
    """
    try:
        exc = []
        try:
            config = app.config
        except Exception as e:
            exc.append(e)
            config = None
        if config is not None:
            try:
                opt = config.githublink_options
            except Exception as ee:
                exc.append(ee)
                opt = None
        else:
            opt = None
        if not opt:
            try:
                opt = settings.githublink_options
            except Exception as eee:
                exc.append(eee)
                opt = None
        if not opt:
            lines = "\n".join("## {0} ##".format(str(e)) for e in exc)
            raise AttributeError(
                "settings does not have a key githublink_options, app does not have a member config.\n{0}".format(lines))
    except AttributeError as err:
        # it just means the role will be ignored
        return None
    if "processor" not in opt:
        user = opt["user"]
        project = opt["project"]
        ref = "https://github.com/{0}/{1}/blob/master/{2}".format(
            user, project, path)
        if lineno:
            ref += "#L{0}".format(lineno)
    else:
        ref, anchor = opt["processor"](path, lineno)
    if anchor == "%" and 'anchor' in opt:
        anchor = opt['anchor']
    set_classes(options)
    node = nodes.reference(rawtext, anchor, refuri=ref, **options)
    return node


def githublink_role(role, rawtext, text, lineno, inliner,
                    options=None, content=None):
    """
    Defines custom role *githublink*. The following instruction add
    a link to the documentation on github.

        :githublink:`source on GitHub|py`

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization (dictionary)
    :param content: The directive content for customization (list)
    :return: ``[node], []``

    The pipe ``|`` indicates that  an extension must be added to
    *docname* to get the true url.

    Different formats handled by the role:

    * ``anchor``: anchor = filename, line number is guess form the position in the file
    * ``anchor|py|*``: extension *.py* is added to the anchor, no line number
    * ``anchor|py|45``: extension *.py* is added to the anchor, line number is 45
    * ``%|py|45``: the anchor name comes from the variable ``githublink_options['anchor']`` in the configuration file
    """
    if options is None:
        options = {}
    if content is None:
        content = []
    if not rawtext or len(rawtext) == 0:
        rawtext = "source"
    app = inliner.document.settings.env.app
    docname = inliner.document.settings.env.docname
    folder = docname
    git = os.path.join(folder, ".git")
    while len(folder) > 0 and not os.path.exists(git):
        folder = os.path.split(folder)[0]
        git = os.path.join(folder, ".git")
    if len(folder) > 0:
        path = docname[len(folder):]
    else:
        path = os.path.join('src', docname)
    path = path.replace("\\", "/").strip("/")

    if "|" in text:
        # no extension to the url, we add one
        spl = text.split("|")
        if len(spl) == 3:
            text, ext, no = spl
            if len(ext) > 5 or "." in ext:
                path = ext
            else:
                path += "." + ext
            lineno = int(no) if no != "*" else None
        elif len(spl) != 2:
            raise ValueError("unable to interpret '{0}'".format(text))
        else:
            text, ext = spl
            path += "." + ext

    try:
        node = make_link_node(rawtext=rawtext, app=app, path=path, lineno=lineno,
                              options=options, anchor=text, settings=inliner.document.settings)
    except (ValueError, AttributeError) as e:
        msg = inliner.reporter.error('githublink_options must be set to a dictionary with keys (user, project)\n%s' % str(e),
                                     line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    if node is None:
        return [], []
    else:
        return [node], []


def setup(app):
    """
    setup for ``githublink`` (sphinx)
    """
    app.add_role('githublink', githublink_role)
    app.add_config_value('githublink_options', None, 'env')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
