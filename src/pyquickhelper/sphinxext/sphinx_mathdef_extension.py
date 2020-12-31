# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to give a title to a mathematical
definition, theorem...
Inspired from `math.py <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/math.py>`_.
"""
import os
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.frontend import Values

import sphinx
from sphinx.locale import _
try:
    from sphinx.errors import NoUri
except ImportError:  # pragma: no cover
    from sphinx.environment import NoUri
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.statemachine import StringList
from sphinx.util.nodes import set_source_info, process_index_entry
from sphinx import addnodes
from ..texthelper.texts_language import TITLES


class mathdef_node(nodes.admonition):
    """
    Defines ``mathdef`` node.
    """
    pass


class mathdeflist(nodes.General, nodes.Element):
    """
    Defines ``mathdeflist`` node.
    """
    pass


class MathDef(BaseAdmonition):
    """
    A ``mathdef`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *title*: a title for the math
    * *tag*: a tag to have several categories of math
    * *lid* or *label*: a label to refer to
    * *index*: to add an entry to the index (comma separated)

    Example::

        .. mathdef::
            :title: title
            :tag: definition or theorem or ...
            :lid: id (used for further reference)

            Description of the math
    """

    node_class = mathdef_node
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

    def run(self):
        """
        Builds the mathdef text.
        """
        # sett = self.state.document.settings
        # language_code = sett.language_code
        lineno = self.lineno

        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]
            legend = "{0}:{1}".format(docname, lineno)
        else:
            legend = ''

        if hasattr(env, "settings") and hasattr(env.settings, "mathdef_link_number"):
            number_format = env.settings.mathdef_link_number
        elif hasattr(self.state.document.settings, "mathdef_link_number"):
            number_format = self.state.document.settings.mathdef_link_number
        elif hasattr(env, "config") and hasattr(env.config, "mathdef_link_number"):
            number_format = env.config.mathdef_link_number
        else:
            raise ValueError(  # pragma: no cover
                "mathdef_link_number is not defined in the configuration")

        if not self.options.get('class'):
            self.options['class'] = ['admonition-mathdef']

        # body
        (mathdef,) = super(MathDef, self).run()
        if isinstance(mathdef, nodes.system_message):
            return [mathdef]

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
        mathtag = self.options.get('tag', '').strip()
        if len(mathtag) == 0:
            raise ValueError("tag is empty")  # pragma: no cover
        if env is not None:
            mid = int(env.new_serialno('indexmathe-u-%s' % mathtag)) + 1
        else:
            mid = -1

        # id of the section
        first_letter = mathtag[0].upper()
        number = mid
        try:
            label_number = number_format.format(
                number=number, first_letter=first_letter)
        except ValueError as e:  # pragma: no cover
            raise Exception(
                "Unable to interpret format '{0}'.".format(number_format)) from e

        # title
        title = self.options.get('title', "").strip()
        if len(title) > 0:
            title = "{0} {1} : {2}".format(mathtag, label_number, title)
        else:
            raise ValueError("title is empty")  # pragma: no cover

        # main node
        ttitle = title
        title = nodes.title(text=_(title))
        if container is not None:
            mathdef.insert(0, title)
            mathdef.insert(0, container)
        else:
            mathdef.insert(0, title)
        mathdef['mathtag'] = mathtag
        mathdef['mathmid'] = mid
        mathdef['mathtitle'] = ttitle
        set_source_info(self, mathdef)

        if env is not None:
            targetid = 'indexmathe-%s%s' % (mathtag,
                                            env.new_serialno('indexmathe%s' % mathtag))
            ids = [targetid]
            targetnode = nodes.target(legend, '', ids=ids[0])
            set_source_info(self, targetnode)
            try:
                self.state.add_target(targetid, '', targetnode, lineno)
            except Exception as e:  # pragma: no cover
                raise Exception(
                    "Issue in\n  File '{0}', line {1}\ntid={2}\ntnode={3}".format(
                        None if env is None else env.docname, lineno,
                        targetid, targetnode)) from e

            # index node
            index = self.options.get('index', None)
            imposed = ",".join(a for a in [mathtag, ttitle] if a)
            if index is None or len(index.strip()) == 0:
                index = imposed
            else:
                index += "," + imposed
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

        return [a for a in [indexnode, targetnode, mathdef] if a is not None]


def process_mathdefs(app, doctree):
    """
    collect all mathdefs in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    env = app.builder.env
    if not hasattr(env, 'mathdef_all_mathsext'):
        env.mathdef_all_mathsext = []
    for node in doctree.traverse(mathdef_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError  # pragma: no cover
        except IndexError:  # pragma: no cover
            targetnode = None
        newnode = node.deepcopy()
        mathtag = newnode['mathtag']
        mathtitle = newnode['mathtitle']
        mathmid = newnode['mathmid']
        del newnode['ids']
        del newnode['mathtag']
        env.mathdef_all_mathsext.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'mathdef': newnode,
            'target': targetnode,
            'mathtag': mathtag,
            'mathtitle': mathtitle,
            'mathmid': mathmid,
        })


class MathDefList(Directive):
    """
    A list of all mathdef entries, for a specific tag.

    * tag: a tag to have several categories of mathdef
    * contents: add a bullet list with links to added blocs

    Example::

        .. mathdeflist::
            :tag: issue
            :contents:
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'tag': directives.unchanged,
        'contents': directives.unchanged,
    }

    def run(self):
        """
        Simply insert an empty mathdeflist node which will be replaced later
        when process_mathdef_nodes is called
        """
        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        tag = self.options.get('tag', '').strip()
        contents = self.options.get(
            'contents', False) in (True, "True", "true", 1, "1", "", None, "None")
        if env is not None:
            targetid = 'indexmathelist-%s' % env.new_serialno('indexmathelist')
            targetnode = nodes.target('', '', ids=[targetid])
            n = mathdeflist('')
            n["mathtag"] = tag
            n["mathcontents"] = contents
            n['docname'] = env.docname if env else "none"
            return [targetnode, n]

        n = mathdeflist('')
        n["mathtag"] = tag
        n["mathcontents"] = contents
        n['docname'] = env.docname if env else "none"
        return [n]


def process_mathdef_nodes(app, doctree, fromdocname):
    """
    process_mathdef_nodes
    """
    if not app.config['mathdef_include_mathsext']:
        for node in doctree.traverse(mathdef_node):
            node.parent.remove(node)

    # Replace all mathdeflist nodes with a list of the collected mathsext.
    # Augment each mathdef with a backlink to the original location.
    env = app.builder.env
    if hasattr(env, "settings") and hasattr(env.settings, "language_code"):
        lang = env.settings.language_code
    else:
        lang = "en"

    orig_entry = TITLES[lang]["original entry"]
    mathmes = TITLES[lang]["mathmes"]

    if not hasattr(env, 'mathdef_all_mathsext'):
        env.mathdef_all_mathsext = []

    for ilist, node in enumerate(doctree.traverse(mathdeflist)):
        if 'ids' in node:
            node['ids'] = []
        if not app.config['mathdef_include_mathsext']:
            node.replace_self([])
            continue

        nbmath = 0
        content = []
        mathtag = node["mathtag"]
        add_contents = node["mathcontents"]
        mathdocname = node["docname"]

        if add_contents:
            bullets = nodes.enumerated_list()
            content.append(bullets)

        double_list = [(info.get('mathtitle', ''), info)
                       for info in env.mathdef_all_mathsext]
        double_list.sort(key=lambda x: x[:1])
        for n, mathdef_info_ in enumerate(double_list):
            mathdef_info = mathdef_info_[1]
            if mathdef_info["mathtag"] != mathtag:
                continue

            nbmath += 1
            para = nodes.paragraph(classes=['mathdef-source'])
            if app.config['mathdef_link_only']:
                description = _('<<%s>>' % orig_entry)
            else:
                description = (
                    _(mathmes) %
                    (orig_entry, os.path.split(mathdef_info['source'])[-1],
                     mathdef_info['lineno'])
                )
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis('', _(orig_entry))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, mathdef_info['docname'])
                try:
                    newnode['refuri'] += '#' + mathdef_info['target']['refid']
                except Exception as e:  # pragma: no cover
                    raise KeyError("refid in not present in '{0}'".format(
                        mathdef_info['target'])) from e
            except NoUri:  # pragma: no cover
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the mathdef content
            mathdef_entry = mathdef_info['mathdef']
            idss = ["index-mathdef-%d-%d" % (ilist, n)]
            # Insert into the mathreflist
            if add_contents:
                title = mathdef_info['mathtitle']
                item = nodes.list_item()
                p = nodes.paragraph()
                item += p
                newnode = nodes.reference('', '', internal=True)
                innernode = nodes.paragraph(text=title)
                try:
                    newnode['refuri'] = app.builder.get_relative_uri(
                        fromdocname, mathdocname)
                    newnode['refuri'] += '#' + idss[0]
                except NoUri:  # pragma: no cover
                    # ignore if no URI can be determined, e.g. for LaTeX output
                    pass
                newnode.append(innernode)
                p += newnode
                bullets += item

            mathdef_entry["ids"] = idss

            if not hasattr(mathdef_entry, "settings"):
                mathdef_entry.settings = Values()
                mathdef_entry.settings.env = env
            # If an exception happens here, see blog 2017-05-21 from the
            # documentation.
            env.resolve_references(mathdef_entry, mathdef_info['docname'],
                                   app.builder)

            # Insert into the mathdeflist
            content.append(mathdef_entry)
            content.append(para)

        node.replace_self(content)


def purge_mathsext(app, env, docname):
    """
    purge_mathsext
    """
    if not hasattr(env, 'mathdef_all_mathsext'):
        return
    env.mathdef_all_mathsext = [mathdef for mathdef in env.mathdef_all_mathsext
                                if mathdef['docname'] != docname]


def merge_mathdef(app, env, docnames, other):
    """
    merge_mathdef
    """
    if not hasattr(other, 'mathdef_all_mathsext'):
        return
    if not hasattr(env, 'mathdef_all_mathsext'):
        env.mathdef_all_mathsext = []
    env.mathdef_all_mathsext.extend(other.mathdef_all_mathsext)


def visit_mathdef_node(self, node):
    """
    visit_mathdef_node
    """
    self.visit_admonition(node)


def depart_mathdef_node(self, node):
    """
    depart_mathdef_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_mathdeflist_node(self, node):
    """
    visit_mathdeflist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_mathdeflist_node(self, node):
    """
    depart_mathdef_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``mathdef`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('mathdef', mathdef_node)
        app.add_mapping('mathdeflist', mathdeflist)

    app.add_config_value('mathdef_include_mathsext', True, 'html')
    app.add_config_value('mathdef_link_only', True, 'html')
    app.add_config_value('mathdef_link_number',
                         "{first_letter}{number}", 'html')

    app.add_node(mathdeflist,
                 html=(visit_mathdeflist_node, depart_mathdeflist_node),
                 epub=(visit_mathdeflist_node, depart_mathdeflist_node),
                 elatex=(visit_mathdeflist_node, depart_mathdeflist_node),
                 latex=(visit_mathdeflist_node, depart_mathdeflist_node),
                 text=(visit_mathdeflist_node, depart_mathdeflist_node),
                 md=(visit_mathdeflist_node, depart_mathdeflist_node),
                 rst=(visit_mathdeflist_node, depart_mathdeflist_node))
    app.add_node(mathdef_node,
                 html=(visit_mathdef_node, depart_mathdef_node),
                 epub=(visit_mathdef_node, depart_mathdef_node),
                 elatex=(visit_mathdef_node, depart_mathdef_node),
                 latex=(visit_mathdef_node, depart_mathdef_node),
                 text=(visit_mathdef_node, depart_mathdef_node),
                 md=(visit_mathdef_node, depart_mathdef_node),
                 rst=(visit_mathdef_node, depart_mathdef_node))

    app.add_directive('mathdef', MathDef)
    app.add_directive('mathdeflist', MathDefList)
    app.connect('doctree-read', process_mathdefs)
    app.connect('doctree-resolved', process_mathdef_nodes)
    app.connect('env-purge-doc', purge_mathsext)
    app.connect('env-merge-info', merge_mathdef)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
