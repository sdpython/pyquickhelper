# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension which proposes a new version of ``.. toctree::``
which takes into account titles dynamically added.
"""
import os
import re
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging
from sphinx.errors import NoUri
import sphinx


class tocdelay_node(nodes.paragraph):
    """
    defines ``tocdelay`` node
    """
    pass


class TocDelayDirective(Directive):
    """
    Defines a :epkg:`sphinx` extension which proposes a new version of ``.. toctree::``
    which takes into account titles dynamically added. It only considers
    one level.

    Example::

        .. tocdelay::

            document

    Directive ``.. toctree::`` only considers titles defined by the user,
    not titles dynamically created by another directives.

    .. warning:: It is not recommended to dynamically insert
        such a directive. It is not recursive.

    Parameter *rule* implements specific behaviors.
    It contains the name of the node which holds
    the document name, the title, the id. In case of the blog,
    the rule is: ``blogpost_node,toctitle,tocid,tocdoc``.
    That means the *TocDelayDirective* will look for nodes
    ``blogpost_node`` and fetch attributes
    *toctitle*, *tocid*, *tocdoc* to fill the toc contents.
    No depth is allowed at this point.
    The previous value is the default value.
    Option *path* is mostly used to test the directive.
    """

    node_class = tocdelay_node
    name_sphinx = "tocdelay"
    has_content = True
    regex_title = re.compile("(.*) +[<]([/a-z_A-Z0-9-]+)[>]")
    option_spec = {'rule': directives.unchanged,
                   'path': directives.unchanged}

    def run(self):
        """
        Just add a @see cl tocdelay_node and list the documents to add.

        @return          of nodes or list of nodes, container
        """
        lineno = self.lineno

        settings = self.state.document.settings
        env = settings.env if hasattr(settings, "env") else None
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
        else:
            docname = ''

        ret = []

        # It analyses rule.
        rule = self.options.get("rule", "blogpost_node,toctitle,tocid,tocdoc")
        spl = rule.split(",")
        if len(spl) > 4:
            ret.append(self.state.document.reporter.warning(
                "tocdelay rule is wrong: '{0}' ".format(rule) +
                'document %r' % docname, line=self.lineno))
        elif len(spl) == 4:
            rule = tuple(spl)
        else:
            defa = ("blogpost_node", "toctitle", "tocid", "tocdoc")
            rule = tuple(spl) + defa[4 - len(spl):]

        # It looks for the documents to add.
        documents = []
        for line in self.content:
            sline = line.strip()
            if len(sline) > 0:
                documents.append(sline)

        # It checks their existence.
        loc = self.options.get("path", None)
        if loc is None:
            loc = os.path.join(env.srcdir, os.path.dirname(env.docname))
            osjoin = os.path.join
        else:
            osjoin = os.path.join
        keep_list = []
        for name in documents:
            if name.endswith(">"):
                # title <link>
                match = TocDelayDirective.regex_title.search(name)
                if match:
                    gr = match.groups()
                    title = gr[0].strip()
                    name = gr[1].strip()
                else:
                    ret.append(self.state.document.reporter.warning(
                        "tocdelay: wrong format for '{0}' ".format(name) +
                        'document %r' % docname, line=self.lineno))
            else:
                title = None

            docname = osjoin(loc, name)
            if not docname.endswith(".rst"):
                docname += ".rst"
            if not os.path.exists(docname):
                ret.append(self.state.document.reporter.warning(
                    'tocdelay contains reference to nonexisting '
                    'document %r' % docname, line=self.lineno))
            else:
                keep_list.append((name, docname, title))

        if len(keep_list) == 0:
            raise ValueError("No found document in '{0}'\nLIST:\n{1}".format(
                loc, "\n".join(documents)))

        # It updates internal references in env.
        entries = []
        includefiles = []
        for name, docname, title in keep_list:
            entries.append((None, docname))
            includefiles.append(docname)

        node = tocdelay_node()
        node['entries'] = entries
        node['includefiles'] = includefiles
        node['tdlineno'] = lineno
        node['tddocname'] = env.docname
        node['tdfullname'] = docname
        node["tdprocessed"] = 0
        node["tddocuments"] = keep_list
        node["tdrule"] = rule
        node["tdloc"] = loc

        wrappernode = nodes.compound(classes=['toctree-wrapper'])
        wrappernode.append(node)
        ret.append(wrappernode)
        return ret


def process_tocdelay(app, doctree):
    """
    Collect all *tocdelay* in the environment.
    Look for the section or document which contain them.
    Put them into the variable *tocdelay_all_tocdelay* in the config.
    """
    for node in doctree.traverse(tocdelay_node):
        node["tdprocessed"] += 1


def transform_tocdelay(app, doctree, fromdocname):
    """
    The function is called by event ``'doctree_resolved'``. It looks for
    every section in page stored in *tocdelay_all_tocdelay*
    in the configuration and builds a short table of contents.
    The instruction ``.. toctree::`` is resolved before every directive in
    the page is executed, the instruction ``.. tocdelay::`` is resolved after.

    @param      app             Sphinx application
    @param      doctree         doctree
    @param      fromdocname     docname

    Thiis directive should be used if you need to capture a section
    which was dynamically added by another one. For example @see cl RunPythonDirective
    calls function ``nested_parse_with_titles``. ``.. tocdelay::`` will capture the
    new section this function might eventually add to the page.
    """
    post_list = list(doctree.traverse(tocdelay_node))
    if len(post_list) == 0:
        return

    env = app.env
    logger = logging.getLogger("tocdelay")

    for node in post_list:
        if node["tdprocessed"] == 0:
            logger.warning("[tocdelay] no first loop was ever processed: 'tdprocessed'={0} , File '{1}', line {2}".format(
                node["tdprocessed"], node["tddocname"], node["tdlineno"]))
            continue
        if node["tdprocessed"] > 1:
            # logger.warning("[tocdelay] already processed: 'tdprocessed'={0} , File '{1}', line {2}".format(
            #     node["tdprocessed"], node["tddocname"], node["tdlineno"]))
            continue

        docs = node["tddocuments"]
        if len(docs) == 0:
            # No document to look at.
            continue

        main_par = nodes.paragraph()
        # node += main_par
        bullet_list = nodes.bullet_list()
        main_par += bullet_list

        nodedocname = node["tddocname"]
        dirdocname = os.path.dirname(nodedocname)
        clname, toctitle, tocid, tocdoc = node["tdrule"]

        logger.info("[tocdelay] transform_tocdelay '{0}' from '{1}'".format(
            nodedocname, fromdocname))
        node["tdprocessed"] += 1

        for name, subname, extitle in docs:
            if not os.path.exists(subname):
                raise FileNotFoundError(
                    "Unable to find document '{0}'".format(subname))

            # The doctree it needs is not necessarily accessible from the main node
            # as they are not necessarily attached to it.
            subname = "{0}/{1}".format(dirdocname, name)
            doc_doctree = env.get_doctree(subname)
            if doc_doctree is None:
                logger.info("[tocdelay] ERROR (4): No doctree found for '{0}' from '{1}'".format(
                    subname, nodedocname))

            # It finds a node sharing the same name.
            diginto = []
            for n in doc_doctree.traverse():
                if n.__class__.__name__ == clname:
                    diginto.append(n)
            if len(diginto) == 0:
                logger.info(
                    "[tocdelay] ERROR (3): No node '{0}' found for '{1}'".format(clname, subname))
                continue

            # It takes the first one available.
            subnode = None
            for d in diginto:
                if 'tocdoc' in d.attributes and d['tocdoc'].endswith(subname):
                    subnode = d
                    break
            if subnode is None:
                found = list(
                    sorted(set(map(lambda x: x.__class__.__name__, diginto))))
                ext = diginto[0].attributes if len(diginto) > 0 else ""
                logger.warning("[tocdelay] ERROR (2): Unable to find node '{0}' in {1} [{2}]".format(
                    subname, ", ".join(map(str, found)), ext))
                continue

            rootnode = subnode

            if tocid not in rootnode.attributes:
                logger.warning(
                    "[tocdelay] ERROR (7): Unable to find 'tocid' in '{0}'".format(rootnode))
                continue
            if tocdoc not in rootnode.attributes:
                logger.warning(
                    "[tocdelay] ERROR (8): Unable to find 'tocdoc' in '{0}'".format(rootnode))
                continue
            refid = rootnode[tocid]
            refdoc = rootnode[tocdoc]

            subnode = list(rootnode.traverse(nodes.title))
            if not subnode:
                logger.warning(
                    "[tocdelay] ERROR (5): Unable to find a title in '{0}'".format(subname))
                continue
            subnode = subnode[0]

            try:
                refuri = app.builder.get_relative_uri(nodedocname, refdoc)
                logger.info(
                    "[tocdelay] add link for '{0}' - '{1}' from '{2}'".format(refid, refdoc, nodedocname))
            except NoUri:
                docn = list(sorted(app.builder.docnames))
                logger.info("[tocdelay] ERROR (9): unable to find a link for '{0}' - '{1}' from '{2}` -- {3} - {4}".format(
                    refid, refdoc, nodedocname, type(app.builder), docn))
                refuri = ''

            use_title = extitle or subnode.astext()
            par = nodes.paragraph()
            ref = nodes.reference(refid=refid, reftitle=use_title, text=use_title,
                                  internal=True, refuri=refuri)
            par += ref
            bullet = nodes.list_item()
            bullet += par
            bullet_list += bullet

        node.replace_self(main_par)


def _print_loop_on_children(node, indent="", msg="-"):
    logger = logging.getLogger("tocdelay")
    if hasattr(node, "children"):
        logger.info(
            "[tocdelay] '{0}' - {1} - {2}".format(type(node), msg, node))
        for child in node.children:
            logger.info("[tocdelay]       {0}{1} - '{2}'".format(indent, type(child),
                                                                 child.astext().replace("\n", " #EOL# ")))
            _print_loop_on_children(child, indent + "    ")


def visit_tocdelay_node(self, node):
    """
    does nothing
    """
    _print_loop_on_children(node, msg="visit")


def depart_tocdelay_node(self, node):
    """
    does nothing
    """
    _print_loop_on_children(node, msg="depart")


def setup(app):
    """
    setup for ``tocdelay`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('tocdelay', tocdelay_node)

    app.add_node(tocdelay_node,
                 html=(visit_tocdelay_node, depart_tocdelay_node),
                 epub=(visit_tocdelay_node, depart_tocdelay_node),
                 elatex=(visit_tocdelay_node, depart_tocdelay_node),
                 latex=(visit_tocdelay_node, depart_tocdelay_node),
                 text=(visit_tocdelay_node, depart_tocdelay_node),
                 md=(visit_tocdelay_node, depart_tocdelay_node),
                 rst=(visit_tocdelay_node, depart_tocdelay_node))

    app.add_directive('tocdelay', TocDelayDirective)
    app.connect('doctree-read', process_tocdelay)
    app.connect('doctree-resolved', transform_tocdelay)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
