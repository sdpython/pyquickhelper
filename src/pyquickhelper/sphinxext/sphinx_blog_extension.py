# -*- coding: utf-8 -*-
"""
@file
@brief Defines blogpost directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_,
`Creating reStructuredText Directives <http://docutils.readthedocs.org/en/sphinx-docs/howto/rst-directives.html>`_
"""
import os
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.locale import _ as _locale
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.util.nodes import set_source_info, process_index_entry
from sphinx.util.nodes import nested_parse_with_titles
from .blog_post import BlogPost
from ..texthelper.texts_language import TITLES


class blogpost_node(nodes.Element):

    """
    Defines *blogpost* node.
    """
    pass


class blogpostagg_node(nodes.Element):

    """
    Defines *blogpostagg* node.
    """
    pass


class BlogPostDirective(Directive):

    """
    Extracts information about a blog post described by a directive ``.. blogpost::``
    and modifies the documentation if *env* is not null. The directive handles the following
    options:

    * *date*: date of the blog (mandatory)
    * *title*: title (mandatory)
    * *keywords*: keywords, comma separated (mandatory)
    * *categories*: categories, comma separated (mandatory)
    * *author*: author (optional)
    * *blog_background*: can change the blog background (boolean, default is True)
    * *lid* or *label*: an id to refer to (optional)
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
                   'lid': directives.unchanged,
                   'label': directives.unchanged,
                   }
    has_content = True
    add_index = True
    add_share = True
    blogpost_class = blogpost_node
    default_config_bg = "blog_background_page"

    def suffix_label(self):
        """
        returns a suffix to add to a label,
        it should not be empty for aggregated pages

        @return     str
        """
        return ""

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
            docname = "___unknown_docname___"
            config = None
            blog_background = False
            sharepost = None
        else:
            # otherwise, it means sphinx is running
            docname = env.docname
            # settings and configuration
            config = env.config
            try:
                blog_background = getattr(
                    config, self.__class__.default_config_bg)
            except AttributeError as e:
                raise AttributeError("Unable to find '{1}' in \n{0}".format(
                    "\n".join(sorted(config.values)), self.__class__.default_config_bg)) from e
            sharepost = config.sharepost if self.__class__.add_share else None

        # post
        p = {
            'docname': docname,
            'lineno': self.lineno,
            'date': self.options["date"],
            'title': self.options["title"],
            'keywords': [a.strip() for a in self.options["keywords"].split(",")],
            'categories': [a.strip() for a in self.options["categories"].split(",")],
            'blog_background': self.options.get("blog_background", str(blog_background)).strip() in ("True", "true", "1"),
            'lid': self.options.get("lid", self.options.get("label", None)),
        }

        tag = BlogPost.build_tag(p["date"], p["title"]) if p[
            'lid'] is None else p['lid']
        targetnode = nodes.target(p['title'], '', ids=[tag])
        p["target"] = targetnode
        idbp = tag + "-container"

        if env is not None:
            if not hasattr(env, 'blogpost_all'):
                env.blogpost_all = []
            env.blogpost_all.append(p)

        # build node
        node = self.__class__.blogpost_class(ids=[idbp], year=p["date"][:4],
                                             rawfile=self.options.get(
                                                 "rawfile", None),
                                             linktitle=p["title"], lg=language_code,
                                             blog_background=p["blog_background"])

        return self.fill_node(node, env, tag, p, language_code, targetnode, sharepost)

    def fill_node(self, node, env, tag, p, language_code, targetnode, sharepost):
        """
        Fills the content of the node.
        """
        # add a label
        suffix_label = self.suffix_label() if not p['lid'] else ""
        tag = "{0}{1}".format(tag, suffix_label)
        tnl = [".. _{0}:".format(tag), ""]
        title = "{0} {1}".format(p["date"], p["title"])
        tnl.append(title)
        tnl.append("=" * len(title))
        tnl.append("")
        if sharepost is not None:
            tnl.append("")
            tnl.append(":sharenet:`{0}`".format(sharepost))
            tnl.append('')
        tnl.append('')
        content = StringList(tnl)
        content = content + self.content
        try:
            nested_parse_with_titles(self.state, content, node)
        except Exception as e:  # pragma: no cover
            from sphinx.util import logging
            logger = logging.getLogger("blogpost")
            logger.warning(
                "[blogpost] unable to parse '{0}' - {1}".format(title, e))
            raise e

        # final
        p['blogpost'] = node
        self.exe_class = p.copy()
        p["content"] = content
        node['classes'] += ["blogpost"]

        # for the instruction tocdelay.
        node['toctitle'] = title
        node['tocid'] = tag
        node['tocdoc'] = env.docname

        # end.
        ns = [node]
        return ns


class BlogPostDirectiveAgg(BlogPostDirective):

    """
    same but for the same post in a aggregated pages
    """
    add_index = False
    add_share = False
    blogpost_class = blogpostagg_node
    default_config_bg = "blog_background"
    option_spec = {'date': directives.unchanged,
                   'title': directives.unchanged,
                   'keywords': directives.unchanged,
                   'categories': directives.unchanged,
                   'author': directives.unchanged,
                   'rawfile': directives.unchanged,
                   'blog_background': directives.unchanged,
                   }

    def suffix_label(self):
        """
        returns a suffix to add to a label,
        it should not be empty for aggregated pages

        @return     str
        """
        if hasattr(self.state.document.settings, "env"):
            env = self.state.document.settings.env
            docname = os.path.split(env.docname)[-1]
            docname = os.path.splitext(docname)[0]
        else:
            env = None
            docname = ""
        return "-agg" + docname

    def fill_node(self, node, env, tag, p, language_code, targetnode, sharepost):
        """
        Fill the node of an aggregated page.
        """
        # add a label
        suffix_label = self.suffix_label()
        container = nodes.container()
        tnl = [".. _{0}{1}:".format(tag, suffix_label), ""]
        content = StringList(tnl)
        self.state.nested_parse(content, self.content_offset, container)
        node += container

        # id section
        if env is not None:
            mid = int(env.new_serialno('indexblog-u-%s' % p["date"][:4])) + 1
        else:
            mid = -1

        # add title
        sids = "y{0}-{1}".format(p["date"][:4], mid)
        section = nodes.section(ids=[sids])
        section['year'] = p["date"][:4]
        section['blogmid'] = mid
        node += section
        textnodes, messages = self.state.inline_text(p["title"], self.lineno)
        section += nodes.title(p["title"], '', *textnodes)
        section += messages

        # add date and share buttons
        tnl = [":bigger:`::5:{0}`".format(p["date"])]
        if sharepost is not None:
            tnl.append(":sharenet:`{0}`".format(sharepost))
        tnl.append('')
        content = StringList(tnl)
        content = content + self.content

        # parse the content into sphinx directive,
        # it adds it to section
        container = nodes.container()
        # nested_parse_with_titles(self.state, content, paragraph)
        self.state.nested_parse(content, self.content_offset, container)
        section += container

        # final
        p['blogpost'] = node
        self.exe_class = p.copy()
        p["content"] = content
        node['classes'] += ["blogpost"]

        # target
        # self.state.add_target(p['title'], '', targetnode, lineno)

        # index (see site-packages/sphinx/directives/code.py, class Index)
        if self.__class__.add_index:
            # it adds an index
            # self.state.document.note_explicit_target(targetnode)
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
    pass


def depart_blogpostagg_node(self, node):
    """
    what to do when leaving a node blogpost,
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_blogpostagg_node_html(self, node):
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
        else:
            self.body.append(
                "%blogpostagg: link to source only available for HTML: '{}'\n".format(type(self)))


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


def process_blogpost_nodes(app, doctree, fromdocname):  # pragma: no cover
    """
    unused, kept as example
    """
    if not app.config.blogpost_include_s:
        for node in doctree.traverse(blogpost_node):
            node.parent.remove(node)

    # Replace all blogpostlist nodes with a list of the collected blogposts.
    # Augment each blogpost with a backlink to the original location.
    env = app.builder.env
    if hasattr(env, "settings") and hasattr(env.settings, "language_code"):
        lang = env.settings.language_code
    else:
        lang = "en"
    blogmes = TITLES[lang]["blog_entry"]

    for node in doctree.traverse(blogpostlist_node):
        if not app.config.blogpost_include_s:
            node.replace_self([])
            continue

        content = []

        for post_info in env.blogpost_all:
            para = nodes.paragraph()
            filename = env.doc2path(post_info['docname'], base=None)
            description = (_locale(blogmes) % (filename, post_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis(_locale('here'), _locale('here'))
            newnode['refdocname'] = post_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, post_info['docname'])
            try:
                newnode['refuri'] += '#' + post_info['target']['refid']
            except Exception as e:
                raise KeyError("refid in not present in '{0}'".format(
                    post_info['target'])) from e
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the blogpostlist
            content.append(post_info['blogpost'])
            content.append(para)

        node.replace_self(content)


def setup(app):
    """
    setup for ``blogpost`` (sphinx)
    """
    # this command enables the parameter blog_background to be part of the
    # configuration
    app.add_config_value('sharepost', None, 'env')
    app.add_config_value('blog_background', True, 'env')
    app.add_config_value('blog_background_page', False, 'env')
    app.add_config_value('out_blogpostlist', [], 'env')
    if hasattr(app, "add_mapping"):
        app.add_mapping('blogpost', blogpost_node)
        app.add_mapping('blogpostagg', blogpostagg_node)

    # app.add_node(blogpostlist)
    app.add_node(blogpost_node,
                 html=(visit_blogpost_node, depart_blogpost_node),
                 epub=(visit_blogpost_node, depart_blogpost_node),
                 elatex=(visit_blogpost_node, depart_blogpost_node),
                 latex=(visit_blogpost_node, depart_blogpost_node),
                 rst=(visit_blogpost_node, depart_blogpost_node),
                 md=(visit_blogpost_node, depart_blogpost_node),
                 text=(visit_blogpost_node, depart_blogpost_node))

    app.add_node(blogpostagg_node,
                 html=(visit_blogpostagg_node, depart_blogpostagg_node_html),
                 epub=(visit_blogpostagg_node, depart_blogpostagg_node_html),
                 elatex=(visit_blogpostagg_node, depart_blogpostagg_node),
                 latex=(visit_blogpostagg_node, depart_blogpostagg_node),
                 rst=(visit_blogpostagg_node, depart_blogpostagg_node),
                 md=(visit_blogpostagg_node, depart_blogpostagg_node),
                 text=(visit_blogpostagg_node, depart_blogpostagg_node))

    app.add_directive('blogpost', BlogPostDirective)
    app.add_directive('blogpostagg', BlogPostDirectiveAgg)
    #app.add_directive('blogpostlist', BlogPostListDirective)
    #app.connect('doctree-resolved', process_blogpost_nodes)
    #app.connect('env-purge-doc', purge_blogpost)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
