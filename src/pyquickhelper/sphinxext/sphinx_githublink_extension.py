# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to display a link on github.
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
        except AttributeError as e:  # pragma: no cover
            exc.append(e)
            config = None
        if config is not None:
            try:
                opt = config.githublink_options
            except AttributeError as ee:  # pragma: no cover
                exc.append(ee)
                opt = None
        else:
            opt = None  # pragma: no cover
        if not opt:
            try:
                opt = settings.githublink_options
            except AttributeError as eee:
                exc.append(eee)
                opt = None
        if not opt:
            lines = "\n".join("## {0} ##".format(str(e)) for e in exc)
            raise AttributeError(
                "settings does not have a key githublink_options, app does not have a member config.\n{0}".format(lines))
    except AttributeError:
        # it just means the role will be ignored
        return None
    if "processor" not in opt:
        user = opt["user"]
        project = opt["project"]
        ll = 'x' if '.cpython' in path else ''
        ref = "https://github.com/{0}/{1}/blob/master/{2}{3}".format(
            user, project, path, ll)
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
    * ``%|py|45``: the anchor name comes from the variable ``githublink_options['anchor']`` in the configuration file.

    A suffix can be added to the extension ``rst-doc`` to tell the extension
    the source comes from the subfolder ``_doc/sphinx/source`` and not from
    a subfolder like ``src``.
    """
    if options is None:
        options = {}
    if content is None:
        content = []
    if not rawtext or len(rawtext) == 0:
        rawtext = "source"  # pragma: no cover

    app = inliner.document.settings.env.app
    docname = inliner.document.settings.env.docname
    folder = docname

    # Retrieves extension and path.
    text0 = text
    path = None
    if "|" in text:
        # No extension to the url, it adds one.
        spl = text.split("|")
        if len(spl) == 3:
            text, ext, no = spl
            if len(ext) > 7 or "." in ext:
                path = ext
                ext = None
            else:
                ext = "." + ext
            lineno = int(no) if no != "*" else None
        elif len(spl) != 2:
            raise ValueError(  # pragma: no cover
                "Unable to interpret '{0}'.".format(text))
        else:
            text, ext = spl
            ext = "." + ext
    else:
        ext = None

    # -
    if ext is not None and "-" in ext:
        spl = ext.split("-")
        if len(spl) != 2:
            raise ValueError(  # pragma: no cover
                "Unable to interpret extension in '{0}'".format(text0))
        ext, doc = spl
    else:
        doc = "src"

    # Get path to source.
    if path is None:
        git = os.path.join(folder, ".git")
        while len(folder) > 0 and not os.path.exists(git):
            folder = os.path.split(folder)[0]
            git = os.path.join(folder, ".git")

        if len(folder) > 0:
            path = docname[len(folder):]
        elif doc == "src":
            path = docname
            source_doc = inliner.document.settings._source
            if source_doc is not None:
                source_doc = source_doc.replace("\\", "/")
                spl = source_doc.split('/')
                if '_doc' in spl:
                    sub_doc = spl[:spl.index('_doc')]
                    root_doc = "/".join(sub_doc)
                    root_doc_src = os.path.join(root_doc, 'src')
                    if os.path.exists(root_doc_src):
                        path = os.path.join('src', docname)  # pragma: no cover
        elif doc == "doc":
            path = os.path.join('_doc', 'sphinxdoc', 'source', docname)
        else:
            raise ValueError(  # pragma: no cover
                "Unable to interpret subfolder in '{0}'.".format(text0))

    # Path with extension.
    if ext is not None:
        path += ext
    path = path.replace("\\", "/")

    # Get rid of binaries (.pyd, .so) --> add a link to the root.
    if path.endswith(".pyd") or path.endswith(".so"):
        path = "/".join(path.split("/")[:-1]).rstrip('/') + '/'

    # Add node.
    try:
        node = make_link_node(rawtext=rawtext, app=app, path=path, lineno=lineno,
                              options=options, anchor=text, settings=inliner.document.settings)
    except (ValueError, AttributeError) as e:  # pragma: no cover
        msg = inliner.reporter.error(
            'githublink_options must be set to a dictionary with keys '
            '(user, project)\n%s' % str(e), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    if node is None:
        return [], []
    return [node], []


def setup(app):
    """
    setup for ``githublink`` (:epkg:`sphinx`)
    """
    app.add_role('githublink', githublink_role)
    app.add_role('gitlink', githublink_role)
    app.add_config_value('githublink_options', None, 'env')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
