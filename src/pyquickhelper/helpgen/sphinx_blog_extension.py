# -*- coding: utf-8 -*-
"""
@file
@brief Defines blogpost directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_
"""

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.compat import make_admonition
from sphinx.locale import _ as _locale
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.util.nodes import explicit_title_re, set_source_info, process_index_entry, nested_parse_with_titles
from docutils.statemachine import ViewList

languages = {
    'en': {"blogpost": "blogpost",
           },
    'fr': {"blogpost": "article",
           }
}


class BlogPostDirective(Directive):

    """
    extracts information about a blog post described by a directive ``.. blogpost::``
    and modifies the documentation if *env* is not null
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'date': directives.unchanged,
                   'title': directives.unchanged,
                   'keywords': directives.unchanged,
                   'categories': directives.unchanged,
                   'author': directives.unchanged,
                   }
    has_content = True
    add_index = True

    def run(self):
        """
        extracts the information in a dictionary and displays it
        if the environment is not null
        """
        sett = self.state.document.settings

        if hasattr(sett, "out_blogpostlist"):
            sett.out_blogpostlist.append(self)

        if hasattr(self.state.document.settings, "env"):
            env = self.state.document.settings.env
        else:
            env = None

        if env is None:
            return []

        targetid = "blogpost-%d" % env.new_serialno('blogpost')
        targetnode = nodes.target('', '', ids=[targetid])

        ad = make_admonition(blogpost_node, self.name,
                             [_locale(self.options["date"])],
                             self.options,
                             self.content,
                             self.lineno,
                             self.content_offset,
                             self.block_text,
                             self.state,
                             self.state_machine)

        if not hasattr(env, 'blogpost_all'):
            env.blogpost_all = []

        p = {
            'docname': env.docname,
            'lineno': self.lineno,
            'blogpost': ad[0].deepcopy(),
            'target': targetnode,
            'date': self.options["date"],
            'title': self.options["title"],
            'keywords': [_.strip() for _ in self.options["keywords"].split(",")],
            'categories': [_.strip() for _ in self.options["categories"].split(",")],
        }
        env.blogpost_all.append(p)

        # we add a title (does not work)
        section = nodes.section()
        section += nodes.title(text=p["title"])

        # index (see site-packages/sphinx/directives/code.py, class Index)
        if self.__class__.add_index:

            # we add an index
            self.state.document.note_explicit_target(targetnode)
            indexnode = addnodes.index()
            indexnode['entries'] = ne = []
            indexnode['inline'] = False
            set_source_info(self, indexnode)
            for entry in set(p["keywords"] + p["categories"] + [p["date"]]):
                ne.extend(process_index_entry(entry, targetid))
            ns = [indexnode, targetnode, section]
        else:
            ns = [targetnode, section]

        return ns + ad


class BlogPostDirectiveAgg(BlogPostDirective):

    """
    same but for the same post in a aggregated pages
    """
    add_index = False


class blogpost_node(nodes.Admonition, nodes.Element):

    """
    defines *blogpost* node
    """
    pass


class blogpostlist_node(nodes.General, nodes.Element):

    """
    defines *blogpostlist* node
    """
    pass


def visit_blogpost_node(self, node):
    """
    what to do when visiting a node blogpost
    """
    #self.body.append ( ... )
    self.visit_admonition(node)


def depart_blogpost_node(self, node):
    """
    what to do when leaving a node blogpost
    """
    #self.body.append ( ... )
    self.depart_admonition(node)

######################
# not really used yet
######################


class BlogPostListDirective(Directive):

    def run(self):
        return [BlogPostListDirective.blogpostlist('')]


def purge_blogpost(app, env, docname):
    if not hasattr(env, 'blogpost_all'):
        return
    env.blogpost_all = [post for post in env.blogpost_all
                        if post['docname'] != docname]


def process_blogpost_nodes(app, doctree, fromdocname):
    if not app.config.blogpost_include_s:
        for node in doctree.traverse(blogpost):
            node.parent.remove(node)

    # Replace all blogpostlist nodes with a list of the collected blogposts.
    # Augment each blogpost with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(blogpostlist):
        if not app.config.blogpost_include_s:
            node.replace_self([])
            continue

        content = []

        for post_info in env.blogpost_all:
            para = nodes.paragraph()
            filename = env.doc2path(post_info['docname'], base=None)
            description = (
                _locale('(The original entry is located in %s, line %d and can be found ') %
                (filename, post_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis(_locale('here'), _locale('here'))
            newnode['refdocname'] = post_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, post_info['docname'])
            newnode['refuri'] += '#' + post_info['target']['refid']
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the blogpostlist
            content.append(post_info['blogpost'])
            content.append(para)

        node.replace_self(content)
