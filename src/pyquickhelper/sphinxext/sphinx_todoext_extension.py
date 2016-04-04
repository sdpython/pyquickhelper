# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to give a title to a todo,
inspired from `todo.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/todo.py>`_.

.. versionadded:: 1.4
"""

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
    """

    node_class = todoext_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'title': directives.unchanged,
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

        if not self.options.get('class'):
            self.options['class'] = ['admonition-todoext']

        (todoext,) = super(TodoExt, self).run()
        if isinstance(todoext, nodes.system_message):
            return [todoext]

        title = self.options.get('title', "").strip()
        if len(title) > 0:
            title = ": " + title
        prefix = TITLES[language_code]["todo"]

        todoext.insert(0, nodes.title(text=_(prefix + title)))
        set_source_info(self, todoext)

        env = self.state.document.settings.env
        targetid = 'index-%s' % env.new_serialno('index')
        targetnode = nodes.target(legend, legend, ids=[targetid])
        return [targetnode, todoext]


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
        del newnode['ids']
        env.todoext_all_todosext.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'todoext': newnode,
            'target': targetnode,
        })


class TodoExtList(Directive):
    """
    A list of all todoext entries.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        """
        Simply insert an empty todoextlist node which will be replaced later
        when process_todoext_nodes is called
        """
        return [todoextlist('')]


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

    if not hasattr(env, 'todoext_all_todosext'):
        env.todoext_all_todosext = []

    for node in doctree.traverse(todoextlist):
        if not app.config['todoext_include_todosext']:
            node.replace_self([])
            continue

        content = []

        for todoext_info in env.todoext_all_todosext:
            para = nodes.paragraph(classes=['todoext-source'])
            if app.config['todoext_link_only']:
                description = _('<<original entry>>')
            else:
                description = (
                    _('(The <<original entry>> is located in %s, line %d.)') %
                    (todoext_info['source'], todoext_info['lineno'])
                )
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis(
                _('original entry'), _('original entry'))
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
    visit_todoext_node
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
    app.add_config_value('todoext_include_todosext', False, 'html')
    app.add_config_value('todoext_link_only', False, 'html')

    app.add_node(todoextlist)
    app.add_node(todoext_node,
                 html=(visit_todoext_node, depart_todoext_node),
                 latex=(visit_todoext_node, depart_todoext_node),
                 text=(visit_todoext_node, depart_todoext_node),
                 man=(visit_todoext_node, depart_todoext_node),
                 texinfo=(visit_todoext_node, depart_todoext_node))

    app.add_directive('todoext', TodoExt)
    app.add_directive('todoextlist', TodoExtList)
    app.connect('doctree-read', process_todoext_nodes)
    app.connect('doctree-resolved', process_todoext_nodes)
    app.connect('env-purge-doc', purge_todosext)
    app.connect('env-merge-info', merge_infoext)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
