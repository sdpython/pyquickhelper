# -*- coding: utf-8 -*-
"""
@file
@brief Defines blogpost directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_,
`Creating reStructuredText Directives <http://docutils.readthedocs.org/en/sphinx-docs/howto/rst-directives.html>`_
"""
import os
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.locale import _ as _locale
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.util.nodes import set_source_info, process_index_entry
from .blog_post import BlogPost
from .texts_language import TITLES


class blogpost_node(nodes.Structural, nodes.Element):

    """
    defines *blogpost* node
    """
    pass


class blogpostagg_node(nodes.Structural, nodes.Element):

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
                   'blog_background': directives.unchanged,
                   }
    has_content = True
    add_index = True
    blogpost_class = blogpost_node

    def run(self):
        """
        extracts the information in a dictionary and displays it
        if the environment is not null

        @return      a list of nodes
        """
        # settings
        sett = self.state.document.settings
        language_code = sett.language_code
        if hasattr(sett, "out_blogpostlist"):
            sett.out_blogpostlist.append(self)

        # env
        if hasattr(self.state.document.settings, "env"):
            env = self.state.document.settings.env
        else:
            env = None

        if env is None:
            # we need an access to the environment to process the blog post
            # this path is used by the BlogPost class to extract the content of
            # the job
            return []
        else:
            # otherwise, it means sphinx is running
            pass

        # settings and configuration
        config = env.config
        blog_background = config.blog_background

        # post
        p = {
            'docname': env.docname,
            'lineno': self.lineno,
            'date': self.options["date"],
            'title': self.options["title"],
            'keywords': [_.strip() for _ in self.options["keywords"].split(",")],
            'categories': [_.strip() for _ in self.options["categories"].split(",")],
            'blog_background': self.options.get("blog_background", str(blog_background)).strip() in ("True", "true", "1"),
        }

        # label
        #targetid = "blogpost-%d" % env.new_serialno('blogpost')
        #targetnode = nodes.target('', '', ids=[targetid])
        #p["target"] = targetnode

        tag = BlogPost.build_tag(p["date"], p["title"])
        targetnode = nodes.target('', '', ids=[tag])
        p["target"] = targetnode

        if not hasattr(env, 'blogpost_all'):
            env.blogpost_all = []
        env.blogpost_all.append(p)

        # we add a title
        idb = nodes.make_id("hblog-" + p["date"] + "-" + p["title"])
        idbp = nodes.make_id("hblogcl-" + p["date"] + "-" + p["title"])
        section = nodes.section(ids=[idb])

        textnodes, messages = self.state.inline_text(p["title"], self.lineno)
        section += nodes.title(p["title"], '', *textnodes)
        section += messages

        # build node
        node = self.__class__.blogpost_class(ids=[idbp], year=p["date"][:4],
                                             rawfile=self.options.get(
                                                 "rawfile", None),
                                             linktitle=p["title"],
                                             lg=language_code,
                                             blog_background=p["blog_background"])
        node += section

        # we add the date
        content = StringList(["**{0}**".format(p["date"]), ""])
        content = content + self.content

        # parse the content into sphinx directive, we add it to section
        paragraph = nodes.paragraph()
        self.state.nested_parse(content, self.content_offset, paragraph)
        node += paragraph
        p['blogpost'] = node

        # classes
        node['classes'] += "-blogpost"

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
            ns = [indexnode, targetnode, node]
        else:
            ns = [targetnode, node]

        return ns


class BlogPostDirectiveAgg(BlogPostDirective):

    """
    same but for the same post in a aggregated pages
    """
    add_index = False
    blogpost_class = blogpostagg_node
    option_spec = {'date': directives.unchanged,
                   'title': directives.unchanged,
                   'keywords': directives.unchanged,
                   'categories': directives.unchanged,
                   'author': directives.unchanged,
                   'rawfile': directives.unchanged,
                   'blog_background': directives.unchanged,
                   }


def visit_blogpost_node(self, node):
    """
    what to do when visiting a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node["blog_background"]:
        # the node will be in a box
        self.visit_admonition(node)


def depart_blogpost_node(self, node):
    """
    what to do when leaving a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node["blog_background"]:
        # the node will be in a box
        self.depart_admonition(node)


def visit_blogpostagg_node(self, node):
    """
    what to do when visiting a node blogpost
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node["blog_background"]:
        # the node will be in a box
        self.visit_admonition(node)


def depart_blogpostagg_node(self, node):
    """
    what to do when leaving a node blogpost,
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    if node.hasattr("year"):
        rawfile = node["rawfile"]
        if rawfile is not None:
            # there is probably better to do
            # module name is something list doctuils.../[xx].py
            lg = node["lg"]
            name = os.path.splitext(os.path.split(rawfile)[-1])[0]
            name += ".html"
            year = node["year"]
            linktitle = node["linktitle"]
            link = """<p><a class="reference internal" href="{0}/{2}" title="{1}">{3}</a></p>""" \
                .format(year, linktitle, name, TITLES[lg]["more"])
            self.body.append(link)
    if node["blog_background"]:
        # the node will be in a box
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
