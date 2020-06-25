# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to keep track of blocs such as examples, FAQ, ...
"""
import os
from docutils import nodes
from docutils.parsers.rst import directives

import sphinx
from sphinx.locale import _
try:
    from sphinx.errors import NoUri
except ImportError:
    from sphinx.environment import NoUri
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.statemachine import StringList
from docutils.frontend import Values
from sphinx.util.nodes import set_source_info, process_index_entry
from sphinx import addnodes
from ..texthelper.texts_language import TITLES
from .sphinx_ext_helper import info_blocref


class blocref_node(nodes.admonition):
    """
    Defines ``blocref`` node.
    """
    pass


class blocreflist(nodes.General, nodes.Element):
    """
    defines ``blocreflist`` node
    """
    pass


class BlocRef(BaseAdmonition):
    """
    A ``blocref`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title*: a title for the bloc
    * *tag*: a tag to have several categories of blocs
    * *lid* or *label*: a label to refer to
    * *index*: to add an entry to the index (comma separated)

    Example::

        .. blocref::
            :title: example of a blocref
            :tag: example
            :lid: id-you-can-choose

            An example of code::

                print("mignon")

    Which renders as:

    .. blocref::
        :title: example of a blocref
        :tag: dummy_example
        :lid: id-you-can-choose

        An example of code::

            print("mignon")

    All blocs can be displayed in another page by using ``blocreflist``::

        .. blocreflist::
            :tag: dummy_example
            :sort: title

    Only examples tagged as ``dummy_example`` will be inserted here.
    The option ``sort`` sorts items by *title*, *number*, *file*.
    You also link to it by typing ``:ref:'anchor <id-you-can-choose>'`` which gives
    something like :ref:`link_to_blocref <id-you-can-choose>`. The link must receive a name.

    .. blocreflist::
        :tag: dummy_example
        :sort: title

    This directive is used to highlight a bloc about
    anything @see cl BlocRef, a question @see cl FaqRef,
    a magic command @see cl NbRef, an example @see cl ExRef.
    It supports option *index* in most of the extensions
    so that the documentation can refer to it.
    """

    node_class = blocref_node
    name_sphinx = "blocref"
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'title': directives.unchanged,
        'tag': directives.unchanged,
        'lid': directives.unchanged,
        'label': directives.unchanged,
        'index': directives.unchanged,
    }

    def _update_title(self, title, tag, lid):
        """
        Updates the title for the bloc itself.
        """
        return title

    def run(self):
        """
        Builds a node @see cl blocref_node.
        """
        return self.private_run()

    def private_run(self, add_container=False):
        """
        Builds a node @see cl blocref_node.

        @param      add_container       add a container node and return as a second result
        @return                         list of nodes or list of nodes, container
        """
        name_desc = self.__class__.name_sphinx
        lineno = self.lineno

        settings = self.state.document.settings
        env = settings.env if hasattr(settings, "env") else None
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
            legend = "{0}:{1}".format(docname, lineno)
        else:
            legend = ''

        if not self.options.get('class'):
            self.options['class'] = ['admonition-%s' % name_desc]

        # body
        (blocref,) = super(BlocRef, self).run()
        if isinstance(blocref, nodes.system_message):
            return [blocref]

        # add a label
        lid = self.options.get('lid', self.options.get('label', None))
        if lid:
            container = nodes.container()
            tnl = [".. _{0}:".format(lid), ""]
            content = StringList(tnl)
            self.state.nested_parse(content, self.content_offset, container)
        else:
            container = None

        # mid
        breftag = self.options.get('tag', '').strip()
        if len(breftag) == 0:
            raise ValueError("tag is empty")  # pragma: no cover
        if env is not None:
            mid = int(env.new_serialno('index%s-%s' %
                                       (name_desc, breftag))) + 1
        else:
            mid = -1

        # title
        titleo = self.options.get('title', "").strip()
        if len(titleo) == 0:
            raise ValueError("title is empty")  # pragma: no cover
        title = self._update_title(titleo, breftag, mid)

        # main node
        ttitle = title
        title = nodes.title(text=_(title))
        if container is not None:
            blocref.insert(0, title)
            blocref.insert(0, container)
        else:
            blocref.insert(0, title)

        if add_container:
            ret_container = nodes.container()
            blocref += ret_container

        blocref['breftag'] = breftag
        blocref['brefmid'] = mid
        blocref['breftitle'] = ttitle
        blocref['breftitleo'] = titleo
        blocref['brefline'] = lineno
        blocref['breffile'] = docname
        set_source_info(self, blocref)

        if env is not None:
            targetid = 'index%s-%s%s' % (name_desc, breftag,
                                         env.new_serialno('index%s%s' % (name_desc, breftag)))
            blocref["breftargetid"] = targetid
            ids = [targetid]
            targetnode = nodes.target(legend, '', ids=ids)
            set_source_info(self, targetnode)
            try:
                self.state.add_target(targetid, '', targetnode, lineno)
            except Exception as e:  # pragma: no cover
                mes = "Issue in \n  File '{0}', line {1}\ntitle={2}\ntag={3}\ntargetid={4}"
                raise Exception(mes.format(docname, lineno,
                                           title, breftag, targetid)) from e

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

        res = [a for a in [indexnode, targetnode, blocref] if a is not None]
        if add_container:
            return res, ret_container
        return res


def process_blocrefs(app, doctree):
    """
    collect all blocrefs in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    process_blocrefs_generic(
        app, doctree, bloc_name="blocref", class_node=blocref_node)


def process_blocrefs_generic(app, doctree, bloc_name, class_node):
    """
    collect all blocrefs in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    env = app.builder.env
    attr = '%s_all_%ss' % (bloc_name, bloc_name)
    if not hasattr(env, attr):
        setattr(env, attr, [])
    attr_list = getattr(env, attr)
    for node in doctree.traverse(class_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError  # pragma: no cover
        except IndexError:  # pragma: no cover
            targetnode = None
        newnode = node.deepcopy()
        breftag = newnode['breftag']
        breftitle = newnode['breftitle']
        brefmid = newnode['brefmid']
        brefline = newnode['brefline']
        breffile = newnode['breffile']
        del newnode['ids']
        del newnode['breftag']
        attr_list.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'blocref': newnode,
            'target': targetnode,
            'breftag': breftag,
            'breftitle': breftitle,
            'brefmid': brefmid,
            'brefline': brefline,
            'breffile': breffile,
        })


class BlocRefList(Directive):
    """
    A list of all blocref entries, for a specific tag.

    * tag: a tag to filter bloc having this tag
    * sort: a way to sort the blocs based on the title, file, number, default: *title*
    * contents: add a bullet list with links to added blocs

    Example::

        .. blocreflist::
            :tag: issue
            :contents:
    """
    name_sphinx = "blocreflist"
    node_class = blocreflist
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'tag': directives.unchanged,
        'sort': directives.unchanged,
        'contents': directives.unchanged,
    }

    def run(self):
        """
        Simply insert an empty blocreflist node which will be replaced later
        when process_blocref_nodes is called
        """
        name_desc = self.__class__.name_sphinx
        settings = self.state.document.settings
        env = settings.env if hasattr(settings, "env") else None
        docname = None if env is None else env.docname
        tag = self.options.get('tag', '').strip()
        n = self.__class__.node_class('')
        n["breftag"] = tag
        n["brefsort"] = self.options.get('sort', 'title').strip()
        n["brefsection"] = self.options.get(
            'section', True) in (True, "True", "true", 1, "1")
        n["brefcontents"] = self.options.get(
            'contents', False) in (True, "True", "true", 1, "1", "", None, "None")
        n['docname'] = docname
        if env is not None:
            targetid = 'index%slist-%s' % (name_desc,
                                           env.new_serialno('index%slist' % name_desc))
            targetnode = nodes.target('', '', ids=[targetid])
            return [targetnode, n]
        else:
            return [n]


def process_blocref_nodes(app, doctree, fromdocname):
    """
    process_blocref_nodes
    """
    process_blocref_nodes_generic(app, doctree, fromdocname, class_name='blocref',
                                  entry_name="brefmes", class_node=blocref_node,
                                  class_node_list=blocreflist)


def process_blocref_nodes_generic(app, doctree, fromdocname, class_name,
                                  entry_name, class_node, class_node_list):
    """
    process_blocref_nodes and other kinds of nodes,

    If the configuration file specifies a variable ``blocref_include_blocrefs`` equals to False,
    all nodes are removed.
    """
    # logging
    cont = info_blocref(app, doctree, fromdocname, class_name,
                        entry_name, class_node, class_node_list)
    if not cont:
        return

    # check this is something to process
    env = app.builder.env
    attr_name = '%s_all_%ss' % (class_name, class_name)
    if not hasattr(env, attr_name):
        setattr(env, attr_name, [])
    bloc_list_env = getattr(env, attr_name)
    if len(bloc_list_env) == 0:
        return

    # content
    incconf = '%s_include_%ss' % (class_name, class_name)
    if app.config[incconf] and not app.config[incconf]:
        for node in doctree.traverse(class_node):
            node.parent.remove(node)

    # Replace all blocreflist nodes with a list of the collected blocrefs.
    # Augment each blocref with a backlink to the original location.
    if hasattr(env, "settings"):
        settings = env.settings
        if hasattr(settings, "language_code"):
            lang = env.settings.language_code
        else:
            lang = "en"
    else:
        settings = None
        lang = "en"

    orig_entry = TITLES[lang]["original entry"]
    brefmes = TITLES[lang][entry_name]

    for ilist, node in enumerate(doctree.traverse(class_node_list)):
        if 'ids' in node:
            node['ids'] = []
        if not app.config[incconf]:
            node.replace_self([])
            continue

        nbbref = 0
        content = []
        breftag = node["breftag"]
        brefsort = node["brefsort"]
        add_contents = node["brefcontents"]
        brefdocname = node["docname"]

        if add_contents:
            bullets = nodes.enumerated_list()
            content.append(bullets)

        # sorting
        if brefsort == 'title':
            double_list = [(info.get('breftitle', ''), info)
                           for info in bloc_list_env if info['breftag'] == breftag]
            double_list.sort(key=lambda x: x[:1])
        elif brefsort == 'file':
            double_list = [((info.get('breffile', ''), info.get('brefline', '')), info)
                           for info in bloc_list_env if info['breftag'] == breftag]
            double_list.sort(key=lambda x: x[:1])
        elif brefsort == 'number':
            double_list = [(info.get('brefmid', ''), info)
                           for info in bloc_list_env if info['breftag'] == breftag]
            double_list.sort(key=lambda x: x[:1])
        else:
            raise ValueError("sort option should be file, number, title")

        # printing
        for n, blocref_info_ in enumerate(double_list):
            blocref_info = blocref_info_[1]

            nbbref += 1

            para = nodes.paragraph(classes=['%s-source' % class_name])

            # Create a target?
            int_ids = ['index%s-%s' % (blocref_info['target']['refid'],
                                       env.new_serialno(blocref_info['target']['refid']))]
            int_targetnode = nodes.target(
                blocref_info['breftitle'], '', ids=int_ids)
            para += int_targetnode

            # rest of the content
            if app.config['%s_link_only' % class_name]:
                description = _('<<%s>>' % orig_entry)
            else:
                description = (
                    _(brefmes) %
                    (orig_entry, os.path.split(blocref_info['source'])[-1],
                     blocref_info['lineno']))
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            newnode['name'] = _(orig_entry)
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, blocref_info['docname'])
                if blocref_info['target'] is None:
                    raise NoUri  # pragma: no cover
                try:
                    newnode['refuri'] += '#' + blocref_info['target']['refid']
                except Exception as e:  # pragma: no cover
                    raise KeyError("refid in not present in '{0}'".format(
                        blocref_info['target'])) from e
            except NoUri:  # pragma: no cover
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass

            newnode.append(nodes.Text(newnode['name']))

            # para is duplicate of the content of the bloc
            para += newnode
            para += nodes.Text(desc2, desc2)

            blocref_entry = blocref_info['blocref']
            idss = ["index-%s-%d-%d" % (class_name, ilist, n)]

            # Inserts into the blocreflist
            # in the list of links at the beginning of the page.
            if add_contents:
                title = blocref_info['breftitle']
                item = nodes.list_item()
                p = nodes.paragraph()
                item += p
                newnode = nodes.reference('', title, internal=True)
                try:
                    newnode['refuri'] = app.builder.get_relative_uri(
                        fromdocname, brefdocname)
                    newnode['refuri'] += '#' + idss[0]
                except NoUri:  # pragma: no cover
                    # ignore if no URI can be determined, e.g. for LaTeX output
                    pass
                p += newnode
                bullets += item

            # Adds the content.
            blocref_entry["ids"] = idss
            if not hasattr(blocref_entry, "settings"):
                blocref_entry.settings = Values()
                blocref_entry.settings.env = env
            # If an exception happens here, see blog 2017-05-21 from the
            # documentation.
            env.resolve_references(blocref_entry, blocref_info[
                                   'docname'], app.builder)
            content.append(blocref_entry)
            content.append(para)

        node.replace_self(content)


def purge_blocrefs(app, env, docname):
    """
    purge_blocrefs
    """
    if not hasattr(env, 'blocref_all_blocrefs'):
        return
    env.blocref_all_blocrefs = [blocref for blocref in env.blocref_all_blocrefs
                                if blocref['docname'] != docname]


def merge_blocref(app, env, docnames, other):
    """
    merge_blocref
    """
    if not hasattr(other, 'blocref_all_blocrefs'):
        return
    if not hasattr(env, 'blocref_all_blocrefs'):
        env.blocref_all_blocrefs = []
    env.blocref_all_blocrefs.extend(other.blocref_all_blocrefs)


def visit_blocref_node(self, node):
    """
    visit_blocref_node
    """
    self.visit_admonition(node)


def depart_blocref_node(self, node):
    """
    depart_blocref_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_blocreflist_node(self, node):
    """
    visit_blocreflist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_blocreflist_node(self, node):
    """
    depart_blocref_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``blocref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('blocref', blocref_node)
        app.add_mapping('blocreflist', blocreflist)

    app.add_config_value('blocref_include_blocrefs', True, 'html')
    app.add_config_value('blocref_link_only', False, 'html')

    app.add_node(blocreflist,
                 html=(visit_blocreflist_node, depart_blocreflist_node),
                 epub=(visit_blocreflist_node, depart_blocreflist_node),
                 latex=(visit_blocreflist_node, depart_blocreflist_node),
                 elatex=(visit_blocreflist_node, depart_blocreflist_node),
                 text=(visit_blocreflist_node, depart_blocreflist_node),
                 md=(visit_blocreflist_node, depart_blocreflist_node),
                 rst=(visit_blocreflist_node, depart_blocreflist_node))
    app.add_node(blocref_node,
                 html=(visit_blocref_node, depart_blocref_node),
                 epub=(visit_blocref_node, depart_blocref_node),
                 elatex=(visit_blocref_node, depart_blocref_node),
                 latex=(visit_blocref_node, depart_blocref_node),
                 text=(visit_blocref_node, depart_blocref_node),
                 md=(visit_blocref_node, depart_blocref_node),
                 rst=(visit_blocref_node, depart_blocref_node))

    app.add_directive('blocref', BlocRef)
    app.add_directive('blocreflist', BlocRefList)
    app.connect('doctree-read', process_blocrefs)
    app.connect('doctree-resolved', process_blocref_nodes)
    app.connect('env-purge-doc', purge_blocrefs)
    app.connect('env-merge-info', merge_blocref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
