# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to give a title to a todo,
inspired from `todo.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/todo.py>`_.

.. versionadded:: 1.4
"""
import sys
import os
from docutils import nodes
from docutils.parsers.rst import directives

import sphinx
from sphinx.locale import _
from sphinx.environment import NoUri
from sphinx.util.nodes import set_source_info
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from ..texthelper.texts_language import TITLES


class todoext_node(nodes.admonition):
    """
    defines ``todoext`` ndoe
    """
    pass


class todoextlist(nodes.General, nodes.Element):
    """
    defines ``todoextlist`` node
    """
    pass


class TodoExt(BaseAdmonition):
    """
    A ``todoext`` entry, displayed in the form of an admonition.
    It takes the following options:

    * title: a title for the todo
    * tag: a tag to have several categories of todo
    * issue: the issue requires `extlinks <http://www.sphinx-doc.org/en/stable/ext/extlinks.html#confval-extlinks>`_
      to be defined and must contain key ``'issue'``

    Example::

        .. todoext::
                :title: title for the todo
                :tag: issue
                :issue: issue number

                Description of the todo
    """

    node_class = todoext_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'title': directives.unchanged,
        'tag': directives.unchanged,
        'issue': directives.unchanged,
    }

    def run(self):
        """
        builds the todo text
        """
        sett = self.state.document.settings
        language_code = sett.language_code
        lineno = self.lineno

        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        docname = None if env is None else env.docname
        if docname is None:
            docname = docname.replace("\\", "/").split("/")[-1]
            legend = "{0}:{1}".format(docname, lineno)
        else:
            legend = ''

        if env is None:
            extlinks = None
        else:
            extlinks = env.config.extlinks if hasattr(env.config, 'extlinks') else None

        if not self.options.get('class'):
            self.options['class'] = ['admonition-todoext']

        (todoext,) = super(TodoExt, self).run()
        if isinstance(todoext, nodes.system_message):
            return [todoext]

        title = self.options.get('title', "").strip()
        issue = self.options.get('issue', "").strip()
        todotag = self.options.get('tag', '').strip()
        if len(title) > 0:
            title = ": " + title
        prefix = TITLES[language_code]["todo"]
        if len(todotag) > 0:
            prefix += ' (%s) ' % todotag

        title = nodes.title(text=_(prefix + title))
        todoext.insert(0, title)
        todoext['todotag'] = todotag
        set_source_info(self, todoext)

        if issue is not None and len(issue) > 0:
            if extlinks is None:
                available = "\n".join(sorted(sett.__dict__.keys()))
                raise ValueError("extlinks is not defined in the documentation settings, available:\n" + available)
            if "issue" not in extlinks:
                raise KeyError("key 'issue' is not present in extlinks")
            url, label = extlinks["issue"]
            url = url % str(issue)
            link = nodes.reference(label, _(label), refuri=url)
            title.append(link)

        if env is not None:
            targetid = 'index-%s' % env.new_serialno('index')
            targetnode = nodes.target(legend, legend, ids=[targetid])
            return [targetnode, todoext]
        else:
            return [todoext]


def process_todoexts(app, doctree):
    """
    collect all todos in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    env = app.builder.env
    if not hasattr(env, 'todoext_all_todosext'):
        env.todoext_all_todosext = []
    for node in doctree.traverse(todoext_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError
        except IndexError:
            targetnode = None
        newnode = node.deepcopy()
        todotag = newnode['todotag']
        del newnode['ids']
        del newnode['todotag']
        env.todoext_all_todosext.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'todoext': newnode,
            'target': targetnode,
            'todotag': todotag,
        })


class TodoExtList(Directive):
    """
    A list of all todoext entries, for a specific tag.

    * tag: a tag to have several categories of todo

    Example::

        .. todoextlist::
                :tag: issue
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'tag': directives.unchanged,
    }

    def run(self):
        """
        Simply insert an empty todoextlist node which will be replaced later
        when process_todoext_nodes is called
        """
        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        tag = self.options.get('tag', '').strip()
        if env is not None:
            targetid = 'index-%s' % env.new_serialno('index')
            targetnode = nodes.target('', '', ids=[targetid])
            n = todoextlist('')
            n["todotag"] = tag
            return [targetnode, n]
        else:
            n = todoextlist('')
            n["todotag"] = tag
            return [n]


def process_todoext_nodes(app, doctree, fromdocname):
    """
    process_todoext_nodes
    """
    if not app.config['todoext_include_todosext']:
        for node in doctree.traverse(todoext_node):
            node.parent.remove(node)

    # Replace all todoextlist nodes with a list of the collected todosext.
    # Augment each todoext with a backlink to the original location.
    env = app.builder.env
    if hasattr(env, "settings") and hasattr(env.settings, "language_code"):
        lang = env.settings.language_code
    else:
        lang = "en"

    orig_entry = TITLES[lang]["original entry"]
    todomes = TITLES[lang]["todomes"]

    if not hasattr(env, 'todoext_all_todosext'):
        env.todoext_all_todosext = []

    for ilist, node in enumerate(doctree.traverse(todoextlist)):
        if not app.config['todoext_include_todosext']:
            node.replace_self([])
            continue

        content = []
        todotag = node["todotag"]

        for n, todoext_info in enumerate(env.todoext_all_todosext):
            if todoext_info["todotag"] != todotag:
                continue
            para = nodes.paragraph(classes=['todoext-source'])
            if app.config['todoext_link_only']:
                description = _('<<%s>>' % orig_entry)
            else:
                description = (
                    _(todomes) %
                    (orig_entry, os.path.split(todoext_info['source'])[-1],
                     todoext_info['lineno'])
                )
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis(
                _(orig_entry), _(orig_entry))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, todoext_info['docname'])
                newnode['refuri'] += '#' + todoext_info['target']['refid']
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the todoext content
            todoext_entry = todoext_info['todoext']
            todoext_entry["ids"] = ["index-todoext-%d-%d" % (ilist, n)]
            # it apparently requires an attributes ids

            env.resolve_references(todoext_entry, todoext_info['docname'],
                                   app.builder)

            # Insert into the todoextlist
            content.append(todoext_entry)
            content.append(para)

        node.replace_self(content)


def purge_todosext(app, env, docname):
    """
    purge_todosext
    """
    if not hasattr(env, 'todoext_all_todosext'):
        return
    env.todoext_all_todosext = [todoext for todoext in env.todoext_all_todosext
                                if todoext['docname'] != docname]


def merge_infoext(app, env, docnames, other):
    """
    merge_infoext
    """
    if not hasattr(other, 'todoext_all_todosext'):
        return
    if not hasattr(env, 'todoext_all_todosext'):
        env.todoext_all_todosext = []
    env.todoext_all_todosext.extend(other.todoext_all_todosext)


def visit_todoext_node(self, node):
    """
    visit_todoext_node
    """
    self.visit_admonition(node)


def depart_todoext_node(self, node):
    """
    depart_todoext_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_todoextlist_node(self, node):
    """
    visit_todoextlist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_todoextlist_node(self, node):
    """
    depart_todoext_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``todoext`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('todoext', todoext_node)
        app.add_mapping('todoextlist', todoextlist)

    app.add_config_value('todoext_include_todosext', False, 'html')
    app.add_config_value('todoext_link_only', False, 'html')

    app.add_node(todoextlist,
                 html=(visit_todoextlist_node, depart_todoextlist_node),
                 latex=(visit_todoextlist_node, depart_todoextlist_node),
                 text=(visit_todoextlist_node, depart_todoextlist_node),
                 man=(visit_todoextlist_node, depart_todoextlist_node),
                 texinfo=(visit_todoextlist_node, depart_todoextlist_node))
    app.add_node(todoext_node,
                 html=(visit_todoext_node, depart_todoext_node),
                 latex=(visit_todoext_node, depart_todoext_node),
                 text=(visit_todoext_node, depart_todoext_node),
                 man=(visit_todoext_node, depart_todoext_node),
                 texinfo=(visit_todoext_node, depart_todoext_node))

    app.add_directive('todoext', TodoExt)
    app.add_directive('todoextlist', TodoExtList)
    if sys.version_info[0] == 2:
        # Sphinx does not accept unicode here
        app.connect('doctree-read'.encode("ascii"), process_todoexts)
        app.connect('doctree-resolved'.encode("ascii"), process_todoext_nodes)
        app.connect('env-purge-doc'.encode("ascii"), purge_todosext)
        app.connect('env-merge-info'.encode("ascii"), merge_infoext)
    else:
        app.connect('doctree-read', process_todoexts)
        app.connect('doctree-resolved', process_todoext_nodes)
        app.connect('env-purge-doc', purge_todosext)
        app.connect('env-merge-info', merge_infoext)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
