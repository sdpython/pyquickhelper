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
from sphinx.util.nodes import set_source_info, process_index_entry
from .blog_post import BlogPost


class blogpost_node(nodes.Admonition, nodes.Element):

    """
    defines *blogpost* node
    """
    pass


class blogpostagg_node(nodes.Admonition, nodes.Element):

    """
    defines *blogpostagg* node
    """
    pass


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
    blogpost_class = blogpost_node

    def _make_ad(self):
        """
        private function
        """
        # self.content  contains the content of the blog as a list
        # self.block_text contains the raw text including the sphinx command
        ad = make_admonition(self.__class__.blogpost_class,
                             self.name,
                             [_locale(self.options["date"]) + " "],
                             self.options,
                             self.content,
                             self.lineno,
                             self.content_offset,
                             self.block_text,
                             self.state,
                             self.state_machine)
        return ad

    def run(self):
        """
        extracts the information in a dictionary and displays it
        if the environment is not null

        @return      a list of nodes
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

        # post
        p = {
            'docname': env.docname,
            'lineno': self.lineno,
            'date': self.options["date"],
            'title': self.options["title"],
            'keywords': [_.strip() for _ in self.options["keywords"].split(",")],
            'categories': [_.strip() for _ in self.options["categories"].split(",")],
        }

        # label
        #targetid = "blogpost-%d" % env.new_serialno('blogpost')
        #targetnode = nodes.target('', '', ids=[targetid])
        #p["target"] = targetnode

        tag = BlogPost.build_tag(p["date"], p["title"])
        targetnode = nodes.target('', '', ids=[tag])
        p["target"] = targetnode

        ad = self._make_ad()

        p['blogpost'] = ad[0].deepcopy()

        if not hasattr(env, 'blogpost_all'):
            env.blogpost_all = []
        env.blogpost_all.append(p)

        # we add a title
        section = nodes.section()
        section += nodes.title(text=p["title"])

        # create a reference
        refnode = nodes.reference('', '', internal=True)
        refnode['refid'] = tag
        refnode['reftitle'] = p["title"]
        # still does not work

        # index (see site-packages/sphinx/directives/code.py, class Index)
        if self.__class__.add_index:

            # we add an index
            self.state.document.note_explicit_target(targetnode)
            indexnode = addnodes.index()
            indexnode['entries'] = ne = []
            indexnode['inline'] = False
            set_source_info(self, indexnode)
            for entry in set(p["keywords"] + p["categories"] + [p["date"]]):
                ne.extend(process_index_entry(entry, tag))  # targetid))
            ns = [indexnode, targetnode, section]
        else:
            ns = [targetnode, section]

        return ns + ad


class BlogPostDirectiveAgg(BlogPostDirective):

    """
    same but for the same post in a aggregated pages
    """
    add_index = False
    blogpost_class = blogpostagg_node

    def _make_ad(self):
        """
        We could overload the method to
        update what to do.
        """
        # self.content  contains the content of the blog as a list
        # self.block_text contains the raw text including the sphinx command
        ad = make_admonition(self.__class__.blogpost_class,
                             self.name,
                             [_locale(self.options["date"]) + " "],
                             self.options,
                             self.content,
                             self.lineno,
                             self.content_offset,
                             self.block_text,
                             self.state,
                             self.state_machine)
        return ad


def visit_blogpost_node(self, node):
    """
    what to do when visiting a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.visit_admonition(node)


def depart_blogpost_node(self, node):
    """
    what to do when leaving a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.depart_admonition(node)


def visit_blogpostagg_node(self, node):
    """
    what to do when visiting a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.visit_admonition(node)


def depart_blogpostagg_node(self, node):
    """
    what to do when leaving a node blogpost,
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.depart_admonition(node)


######################
# unused, kept as example
######################

class blogpostlist_node(nodes.General, nodes.Element):

    """
    defines *blogpostlist* node,
    unused, kept as example
    """
    pass


class BlogPostListDirective(Directive):

    """
    unused, kept as example
    """

    def run(self):
        return [BlogPostListDirective.blogpostlist('')]


def purge_blogpost(app, env, docname):
    """
    unused, kept as example
    """
    if not hasattr(env, 'blogpost_all'):
        return
    env.blogpost_all = [post for post in env.blogpost_all
                        if post['docname'] != docname]


def process_blogpost_nodes(app, doctree, fromdocname):
    """
    unused, kept as example
    """
    if not app.config.blogpost_include_s:
        for node in doctree.traverse(blogpost_node):
            node.parent.remove(node)

    # Replace all blogpostlist nodes with a list of the collected blogposts.
    # Augment each blogpost with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(blogpostlist_node):
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
