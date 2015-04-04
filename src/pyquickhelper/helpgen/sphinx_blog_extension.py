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

languages = {
    'en': {"blogpost": "blogpost",
           },
    'fr': {"blogpost": "article",
           }
}


class BlogPostInfoDirective(Directive):

    """
    extracts information about a blog post described by a directive ``..blogpost::``.
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

    def run(self):
        """
        extracts the information in a dictionary
        """
        sett = self.state.document.settings

        if hasattr(sett, "out_blogpostlist"):
            sett.out_blogpostlist.append(self)

        # print(sett.out_blogpostlist)
        # print(self.state)
        # print(self.state_machine)
        #lineno = self.lineno
        #name = self.name
        #content = self.content
        #block_text = self.block_text
        #options = self.options
        return []


class blogpost(nodes.Admonition, nodes.Element):

    """
    defines *blogpost* node
    """
    pass


class blogpostlist(nodes.General, nodes.Element):

    """
    defines *blogpostlist* node
    """
    pass


def visit_blogpost_node(self, node):
    """
    what to do when visiting a node blogpost
    """
    print("[visit]", node)
    self.visit_admonition(node)


def depart_blogpost_node(self, node):
    """
    what to do when leaving a node blogpost
    """
    print("[depart]", node)
    self.depart_admonition(node)


class BlogPostListDirective(Directive):

    def run(self):
        print("[run]")
        return [BlogPostListDirective.blogpostlist('')]


class BlogPostDirective(BlogPostInfoDirective):

    # this enables content in the directive
    has_content = True

    def run(self):
        print("[BlogPostDirective.run]")
        env = self.state.document.settings.env

        targetid = "blogpost-%d" % env.new_serialno('blogpost')
        targetnode = nodes.target('', '', ids=[targetid])

        ad = make_admonition(blogpost, self.name, [_locale('BlogPost')],
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
            'date': "?",
            'title': "??",
            'keywords': "???",
            'categories': "????",
        }
        env.blogpost_all.append(p)
        print(p)

        return [targetnode] + ad


def purge_blogpost(app, env, docname):
    if not hasattr(env, 'blogpost_all'):
        return
    print("[purge_blogpost]")
    env.blogpost_all = [post for post in env.blogpost_all
                        if post['docname'] != docname]


def process_blogpost_nodes(app, doctree, fromdocname):
    print("[process_blogpost_nodes]")
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
            print("post_info", post_info)
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
