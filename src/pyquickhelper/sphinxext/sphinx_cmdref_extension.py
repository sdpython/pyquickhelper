# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to keep track of *cmd*.
"""
from io import StringIO
from docutils import nodes
import sphinx
from sphinx.util import logging
from docutils.parsers.rst import directives
from ..loghelper import run_script, noLOG
from .sphinx_blocref_extension import BlocRef, process_blocrefs_generic, BlocRefList, process_blocref_nodes_generic
from .import_object_helper import import_object


class cmdref_node(nodes.admonition):
    """
    defines ``cmdref`` node
    """
    pass


class cmdreflist(nodes.General, nodes.Element):
    """
    defines ``cmdreflist`` node
    """
    pass


class CmdRef(BlocRef):
    """
    A ``cmdref`` entry, displayed in the form of an admonition.
    It is used to reference a script a module is added as a command line.
    It takes the following options:

    * *title*: a title for the bloc
    * *tag*: a tag to have several categories of blocs, if not specified, it will be equal to *cmd*
    * *lid* or *label*: a label to refer to
    * *index*: to add an additional entry to the index (comma separated)
    * *name*: command line name, if populated, the directive displays the output of
      ``name --help``.
    * *path*: used if the command line startswith ``-m``

    It works the same way as @see cl BlocRef. The command line can be
    something like ``-m <module> <command> ...``. The extension
    will call :epkg:`python` in a separate process.

   .. todoext::
        :title: cmdref does not display anything if the content is empty.
        :tag: bug
        :issue: 51
    """

    node_class = cmdref_node
    name_sphinx = "cmdref"

    option_spec = dict(cmd=directives.unchanged,
                       path=directives.unchanged,
                       **BlocRef.option_spec)

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
            self.options["tag"] = "cmd"
        if "index" not in self.options:
            self.options["index"] = title
        else:
            self.options["index"] += "," + title
        path = self.options.get('path', None)

        res, cont = BlocRef.private_run(self, add_container=True)
        name = self.options.get("cmd", None)

        if name is not None and len(name) > 0:
            self.reporter = self.state.document.reporter
            try:
                source, lineno = self.reporter.get_source_and_line(self.lineno)
            except AttributeError:  # pragma: no cover
                source = lineno = None

            # object name
            if name.startswith("-m"):
                # example: -m pyquickhelper clean_files --help
                out, err = run_script(
                    name, fLOG=noLOG, wait=True, change_path=path)
                if err:
                    lines = err.split('\n')
                    err = []
                    for line in lines:
                        if 'is already registered, it will be overridden' in line:
                            continue
                        err.append(line)
                    err = "\n".join(err).strip('\n\r\t ')
                if err:
                    out = "--SCRIPT--{}\n--OUT--\n{}\n--ERR--\n{}\n--PATH--\n{}".format(
                        name, out, err, path)
                    logger = logging.getLogger("CmdRef")
                    logger.warning("[CmdRef] cmd failed '{0}'".format(name))
                elif out in (None, ''):
                    out = "--SCRIPT--{}\n--EMPTY OUTPUT--\n--PATH--\n{}".format(
                        name, path)
                    logger = logging.getLogger("CmdRef")
                    logger.warning("[CmdRef] cmd empty '{0}'".format(name))
                content = "python " + name
                cont += nodes.paragraph('<<<', '<<<')
                pout = nodes.literal_block(content, content)
                cont += pout
                cont += nodes.paragraph('>>>', '>>>')
                pout = nodes.literal_block(out, out)
                cont += pout
            else:
                if ":" not in name:
                    logger = logging.getLogger("CmdRef")
                    logger.warning(
                        "[CmdRef] cmd '{0}' should contain ':': <full_function_name>:<cmd_name> as specified in the setup.".format(name))
                    if lineno is not None:
                        logger.warning(
                            '   File "{0}", line {1}'.format(source, lineno))

                # example: pyquickhelper.cli.pyq_sync_cli:pyq_sync
                spl = name.strip("\r\n\t ").split(":")
                if len(spl) != 2:
                    logger = logging.getLogger("CmdRef")
                    logger.warning(
                        "[CmdRef] cmd(*= '{0}' should contain ':': <full_function_name>:<cmd_name> as specified in the setup.".format(name))
                    if lineno is not None:
                        logger.warning(
                            '   File "{0}", line {1}'.format(source, lineno))

                # rename the command line
                if "=" in spl[0]:
                    name_cmd, fullname = spl[0].split('=')
                    name_fct = spl[1]
                else:
                    fullname, name_cmd = spl
                    name_fct = name_cmd

                name_fct = name_fct.strip()
                fullname = fullname.strip()
                name_cmd = name_cmd.strip()

                fullname = "{0}.{1}".format(fullname, name_fct)
                try:
                    obj, name = import_object(fullname, kind="function")
                except ImportError:  # pragma: no cover
                    logger = logging.getLogger("CmdRef")
                    logger.warning(
                        "[CmdRef] unable to import '{0}'".format(fullname))
                    if lineno is not None:
                        logger.warning(
                            '   File "{0}", line {1}'.format(source, lineno))
                    obj = None

                if obj is not None:
                    stio = StringIO()

                    def local_print(*li):
                        "local function"
                        stio.write(" ".join(str(_) for _ in li) + "\n")
                    obj(args=['--help'], fLOG=local_print)

                    content = "{0} --help".format(name_cmd)
                    pout = nodes.paragraph(content, content)
                    cont += pout

                    content = stio.getvalue()
                    if len(content) == 0:
                        logger = logging.getLogger("CmdRef")
                        logger.warning(
                            "[CmdRef] empty output for '{0}'".format(fullname))
                        if lineno is not None:
                            logger.warning(
                                '   File "{0}", line {1}'.format(source, lineno))
                        out = "--SCRIPT--{}\n--EMPTY OUTPUT--\n--PATH--\n{}".format(
                            name, path)
                        logger = logging.getLogger("CmdRef")
                        logger.warning("[CmdRef] cmd empty '{0}'".format(name))
                    else:
                        start = 'usage: ' + name_fct
                        if content.startswith(start):
                            content = "usage: {0}{1}".format(
                                name_cmd, content[len(start):])
                    pout = nodes.literal_block(content, content)
                    cont += pout

        return res


def process_cmdrefs(app, doctree):
    """
    Collect all cmdrefs in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions.
    """
    process_blocrefs_generic(
        app, doctree, bloc_name="cmdref", class_node=cmdref_node)


class CmdRefList(BlocRefList):
    """
    A list of all *cmdref* entries, for a specific tag.

    * tag: a tag to have several categories of *cmdref*
    * contents: add a bullet list with links to added blocs
    """
    name_sphinx = "cmdreflist"
    node_class = cmdreflist

    def run(self):
        """
        calls run from @see cl BlocRefList and add default tag if not present
        """
        if "tag" not in self.options:
            self.options["tag"] = "cmd"
        return BlocRefList.run(self)


def process_cmdref_nodes(app, doctree, fromdocname):
    """
    process_cmdref_nodes
    """
    process_blocref_nodes_generic(app, doctree, fromdocname, class_name='cmdref',
                                  entry_name="cmdmes", class_node=cmdref_node,
                                  class_node_list=cmdreflist)


def purge_cmdrefs(app, env, docname):
    """
    purge_cmdrefs
    """
    if not hasattr(env, 'cmdref_all_cmdrefs'):
        return
    env.cmdref_all_cmdrefs = [cmdref for cmdref in env.cmdref_all_cmdrefs
                              if cmdref['docname'] != docname]


def merge_cmdref(app, env, docnames, other):
    """
    merge_cmdref
    """
    if not hasattr(other, 'cmdref_all_cmdrefs'):
        return
    if not hasattr(env, 'cmdref_all_cmdrefs'):
        env.cmdref_all_cmdrefs = []
    env.cmdref_all_cmdrefs.extend(other.cmdref_all_cmdrefs)


def visit_cmdref_node(self, node):
    """
    visit_cmdref_node
    """
    self.visit_admonition(node)


def depart_cmdref_node(self, node):
    """
    *depart_cmdref_node*,
    see `sphinx/writers/html.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py>`_.
    """
    self.depart_admonition(node)


def visit_cmdreflist_node(self, node):
    """
    visit_cmdreflist_node
    see `sphinx/writers/html.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py>`_.
    """
    self.visit_admonition(node)


def depart_cmdreflist_node(self, node):
    """
    *depart_cmdref_node*
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``cmdref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('cmdref', cmdref_node)
        app.add_mapping('cmdreflist', cmdreflist)

    app.add_config_value('cmdref_include_cmdrefs', True, 'html')
    app.add_config_value('cmdref_link_only', False, 'html')

    app.add_node(cmdreflist,
                 html=(visit_cmdreflist_node, depart_cmdreflist_node),
                 epub=(visit_cmdreflist_node, depart_cmdreflist_node),
                 elatex=(visit_cmdreflist_node, depart_cmdreflist_node),
                 latex=(visit_cmdreflist_node, depart_cmdreflist_node),
                 text=(visit_cmdreflist_node, depart_cmdreflist_node),
                 md=(visit_cmdreflist_node, depart_cmdreflist_node),
                 rst=(visit_cmdreflist_node, depart_cmdreflist_node))
    app.add_node(cmdref_node,
                 html=(visit_cmdref_node, depart_cmdref_node),
                 epub=(visit_cmdref_node, depart_cmdref_node),
                 elatex=(visit_cmdref_node, depart_cmdref_node),
                 latex=(visit_cmdref_node, depart_cmdref_node),
                 text=(visit_cmdref_node, depart_cmdref_node),
                 md=(visit_cmdref_node, depart_cmdref_node),
                 rst=(visit_cmdref_node, depart_cmdref_node))

    app.add_directive('cmdref', CmdRef)
    app.add_directive('cmdreflist', CmdRefList)
    app.connect('doctree-read', process_cmdrefs)
    app.connect('doctree-resolved', process_cmdref_nodes)
    app.connect('env-purge-doc', purge_cmdrefs)
    app.connect('env-merge-info', merge_cmdref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
