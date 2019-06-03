# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to give a title to a todo,
inspired from `todo.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/todo.py>`_.
"""
import os
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.frontend import Values

import sphinx
from sphinx.locale import _ as locale_
from sphinx.errors import NoUri
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from sphinx.util.nodes import set_source_info, process_index_entry
from sphinx import addnodes
from ..texthelper.texts_language import TITLES
from .sphinxext_helper import try_add_config_value


class todoext_node(nodes.admonition):
    """
    Defines ``todoext`` node.
    """
    pass


class todoextlist(nodes.General, nodes.Element):
    """
    Defines ``todoextlist`` node.
    """
    pass


class TodoExt(BaseAdmonition):
    """
    A ``todoext`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title:* a title for the todo (mandatory)
    * *tag:* a tag to have several categories of todo (mandatory)
    * *issue:* the issue requires `extlinks <http://www.sphinx-doc.org/en/stable/ext/extlinks.html#confval-extlinks>`_
      to be defined and must contain key ``'issue'`` (optional)
    * *cost:* a cost if the todo were to be fixed (optional)
    * *priority:* to prioritize items (optional)
    * *hidden:* if true, the todo does not appear where it is inserted but it
      will with a todolist (optional)
    * *date:* date (optional)
    * *release:* release number (optional)

    Example::

        .. todoext::
            :title: title for the todo
            :tag: issue
            :issue: issue number

            Description of the todo

    .. todoext::
        :title: add option hidden to hide the item
        :tag: done
        :date: 2016-06-23
        :hidden:
        :issue: 17
        :release: 1.4
        :cost: 0.2

        Once an item is done, it can be hidden from the documentation
        and show up in a another page.

    If the option ``issue`` is filled, the configuration must contain a key in ``extlinks``:

        extlinks=dict(issue=('https://link/%s',
                             'issue {0} on somewhere')))
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
        'cost': directives.unchanged,
        'priority': directives.unchanged,
        'hidden': directives.unchanged,
        'date': directives.unchanged,
        'release': directives.unchanged,
        'index': directives.unchanged,
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
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
            legend = "{0}:{1}".format(docname, lineno)
        else:
            legend = ''

        if not self.options.get('class'):
            self.options['class'] = ['admonition-todoext']

        # link to issue
        issue = self.options.get('issue', "").strip()
        if issue is not None and len(issue) > 0:
            if hasattr(sett, "extlinks"):
                extlinks = sett.extlinks
            elif env is not None and hasattr(env.config, "extlinks"):
                extlinks = env.config.extlinks
            else:
                available = "\n".join(sorted(sett.__dict__.keys()))
                available2 = "\n".join(
                    sorted(env.config.__dict__.keys())) if env is not None else "-"
                mes = "extlinks (wih a key 'issue') is not defined in the documentation settings, available in sett\n{0}\nCONFIG\n{1}"
                raise ValueError(mes.format(available, available2))

            if "issue" not in extlinks:
                raise KeyError("key 'issue' is not present in extlinks")
            url, label = extlinks["issue"]
            url = url % str(issue)
            lab = label.format(issue)
            linkin = nodes.reference(lab, locale_(lab), refuri=url)
            link = nodes.paragraph()
            link += linkin
        else:
            link = None

        # cost
        cost = self.options.get('cost', "").strip()
        if cost:
            try:
                fcost = float(cost)
            except ValueError:
                raise ValueError(
                    "unable to convert cost '{0}' into float".format(cost))
        else:
            fcost = 0.0

        # priority
        prio = self.options.get('priority', "").strip()

        # hidden
        hidden = self.options.get('hidden', "false").strip().lower() in {
            'true', '1', ''}

        # body
        (todoext,) = super(TodoExt, self).run()
        if isinstance(todoext, nodes.system_message):
            return [todoext]

        # link
        if link:
            todoext += link

        # title
        title = self.options.get('title', "").strip()
        todotag = self.options.get('tag', '').strip()
        if len(title) > 0:
            title = ": " + title

        # prefix
        prefix = TITLES[language_code]["todo"]
        tododate = self.options.get('date', "").strip()
        todorelease = self.options.get('release', "").strip()
        infos = []
        if len(todotag) > 0:
            infos.append(todotag)
        if len(prio) > 0:
            infos.append('P=%s' % prio)
        if fcost > 0:
            if int(fcost) == fcost:
                infos.append('C=%d' % int(fcost))
            else:
                infos.append('C=%1.1f' % fcost)
        if todorelease:
            infos.append('v{0}'.format(todorelease))
        if tododate:
            infos.append(tododate)
        if infos:
            prefix += "({0})".format(" - ".join(infos))

        # main node
        title = nodes.title(text=locale_(prefix + title))
        todoext.insert(0, title)
        todoext['todotag'] = todotag
        todoext['todocost'] = fcost
        todoext['todoprio'] = prio
        todoext['todohidden'] = hidden
        todoext['tododate'] = tododate
        todoext['todorelease'] = todorelease
        todoext['todotitle'] = self.options.get('title', "").strip()
        set_source_info(self, todoext)

        if hidden:
            todoext['todoext_copy'] = todoext.deepcopy()
            todoext.clear()

        if env is not None:
            targetid = 'indextodoe-%s' % env.new_serialno('indextodoe')
            targetnode = nodes.target(legend, '', ids=[targetid])
            set_source_info(self, targetnode)
            self.state.add_target(targetid, '', targetnode, lineno)

            # index node
            index = self.options.get('index', None)
            if index is not None:
                indexnode = addnodes.index()
                indexnode['entries'] = ne = []
                indexnode['inline'] = False
                set_source_info(self, indexnode)
                for entry in index.split(","):
                    ne.extend(process_index_entry(entry, targetid))
            else:
                indexnode = None
        else:
            targetnode = None
            indexnode = None

        return [a for a in [indexnode, targetnode, todoext] if a is not None]


def process_todoexts(app, doctree):
    """
    collect all todoexts in the environment
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
        todotitle = newnode['todotitle']
        todoext_copy = node.get('todoext_copy', None)
        del newnode['ids']
        del newnode['todotag']
        if todoext_copy is not None:
            del newnode['todoext_copy']
        env.todoext_all_todosext.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'todosource': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'todoext': newnode,
            'target': targetnode,
            'todotag': todotag,
            'todocost': newnode['todocost'],
            'todoprio': newnode['todoprio'],
            'todotitle': todotitle,
            'tododate': newnode['tododate'],
            'todorelease': newnode['todorelease'],
            'todohidden': newnode['todohidden'],
            'todoext_copy': todoext_copy,
        })


class TodoExtList(Directive):
    """
    A list of all todoext entries, for a specific tag.

    * tag: a tag to have several categories of todoext

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
        'sort': directives.unchanged,
    }

    def run(self):
        """
        Simply insert an empty todoextlist node which will be replaced later
        when process_todoext_nodes is called
        """
        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        tag = self.options.get('tag', '').strip()
        tsort = self.options.get('sort', '').strip()
        if env is not None:
            targetid = 'indextodoelist-%s' % env.new_serialno('indextodoelist')
            targetnode = nodes.target('', '', ids=[targetid])
            n = todoextlist('')
            n["todotag"] = tag
            n["todosort"] = tsort
            return [targetnode, n]
        else:
            n = todoextlist('')
            n["todotag"] = tag
            n["todosort"] = tsort
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
    allowed_tsort = {'date', 'prio', 'title', 'release', 'source'}

    if not hasattr(env, 'todoext_all_todosext'):
        env.todoext_all_todosext = []

    for ilist, node in enumerate(doctree.traverse(todoextlist)):
        if 'ids' in node:
            node['ids'] = []
        if not app.config['todoext_include_todosext']:
            node.replace_self([])
            continue

        nbtodo = 0
        fcost = 0
        content = []
        todotag = node["todotag"]
        tsort = node["todosort"]
        if tsort == '':
            tsort = 'source'
        if tsort not in allowed_tsort:
            raise ValueError(
                "option sort must in {0}, '{1}' is not".format(allowed_tsort, tsort))

        double_list = [(info.get('todo%s' % tsort, ''),
                        info.get('todotitle', ''), info)
                       for info in env.todoext_all_todosext]
        double_list.sort(key=lambda x: x[:2])
        for n, todoext_info_ in enumerate(double_list):
            todoext_info = todoext_info_[2]
            if todoext_info["todotag"] != todotag:
                continue

            nbtodo += 1
            fcost += todoext_info.get("todocost", 0.0)

            para = nodes.paragraph(classes=['todoext-source'])
            if app.config['todoext_link_only']:
                description = locale_('<<%s>>' % orig_entry)
            else:
                description = (
                    locale_(todomes) %
                    (orig_entry, os.path.split(todoext_info['source'])[-1],
                     todoext_info['lineno'])
                )
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis('', locale_(orig_entry))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, todoext_info['docname'])
                try:
                    newnode['refuri'] += '#' + todoext_info['target']['refid']
                except Exception as e:
                    raise KeyError("refid in not present in '{0}'".format(
                        todoext_info['target'])) from e
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the todoext content
            todoext_entry = todoext_info.get('todoext_copy', None)
            if todoext_entry is None:
                todoext_entry = todoext_info['todoext']
            todoext_entry["ids"] = ["index-todoext-%d-%d" % (ilist, n)]
            # it apparently requires an attributes ids

            if not hasattr(todoext_entry, "settings"):
                todoext_entry.settings = Values()
                todoext_entry.settings.env = env
            # If an exception happens here, see blog 2017-05-21 from the
            # documentation.
            env.resolve_references(todoext_entry, todoext_info['docname'],
                                   app.builder)

            # Insert into the todoextlist
            content.append(todoext_entry)
            content.append(para)

        if fcost > 0:
            cost = nodes.paragraph()
            lab = "{0} items, cost: {1}".format(nbtodo, fcost)
            cost += nodes.Text(lab)
            content.append(cost)
        else:
            cost = nodes.paragraph()
            lab = "{0} items".format(nbtodo)
            cost += nodes.Text(lab)
            content.append(cost)

        node.replace_self(content)


def purge_todosext(app, env, docname):
    """
    purge_todosext
    """
    if not hasattr(env, 'todoext_all_todosext'):
        return
    env.todoext_all_todosext = [todoext for todoext in env.todoext_all_todosext
                                if todoext['docname'] != docname]


def merge_todoext(app, env, docnames, other):
    """
    merge_todoext
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
    Setup for ``todoext`` (sphinx).
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('todoext', todoext_node)
        app.add_mapping('todoextlist', todoextlist)

    app.add_config_value('todoext_include_todosext', False, 'html')
    app.add_config_value('todoext_link_only', False, 'html')

    # The following variable is shared with extension
    # `todo <http://www.sphinx-doc.org/en/stable/ext/todo.html>`_.
    try_add_config_value(app, 'extlinks', {}, 'env')

    app.add_node(todoextlist,
                 html=(visit_todoextlist_node, depart_todoextlist_node),
                 epub=(visit_todoextlist_node, depart_todoextlist_node),
                 elatex=(visit_todoextlist_node, depart_todoextlist_node),
                 latex=(visit_todoextlist_node, depart_todoextlist_node),
                 text=(visit_todoextlist_node, depart_todoextlist_node),
                 md=(visit_todoextlist_node, depart_todoextlist_node),
                 rst=(visit_todoextlist_node, depart_todoextlist_node))
    app.add_node(todoext_node,
                 html=(visit_todoext_node, depart_todoext_node),
                 epub=(visit_todoext_node, depart_todoext_node),
                 elatex=(visit_todoext_node, depart_todoext_node),
                 latex=(visit_todoext_node, depart_todoext_node),
                 text=(visit_todoext_node, depart_todoext_node),
                 md=(visit_todoext_node, depart_todoext_node),
                 rst=(visit_todoext_node, depart_todoext_node))

    app.add_directive('todoext', TodoExt)
    app.add_directive('todoextlist', TodoExtList)
    app.connect('doctree-read', process_todoexts)
    app.connect('doctree-resolved', process_todoext_nodes)
    app.connect('env-purge-doc', purge_todosext)
    app.connect('env-merge-info', merge_todoext)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
