# -*- coding: utf-8 -*-
"""
@file
@brief Helpers to build :epkg:`RST` extra files inserted in the documentation.
"""
import os
import shutil
from .blog_post import BlogPost
from .build_rss import build_rss
from ..texthelper.texts_language import TITLES
from ..texthelper.diacritic_helper import remove_diacritics
from ..loghelper import noLOG


class BlogPostList:

    """
    Defines a list of @see cl BlogPost.
    """

    def __init__(self, folder, encoding="utf8", language="en", extensions=None, fLOG=noLOG):
        """
        Creates a list of @see cl BlogPost, we assume each blog
        post belongs to a subfolder ``YYYY``.

        @param      folder          folder when to find files
        @param      encoding        encoding
        @param      language        language
        @param      extensions      list of extension to use to parse the content of the blog,
                                    if None, it will consider a default list
                                    (@see cl BlogPost and @see fn get_default_extensions)
        @param      fLOG            logging function
        """
        self._blogposts = []
        sub = os.listdir(folder)
        for s in sorted(sub):
            full = os.path.join(folder, s)
            if os.path.isdir(full):
                fLOG("[BlogPostList]    reading folder", full)
                posts = os.listdir(full)
                for post in sorted(posts):
                    if os.path.splitext(post)[-1] in [".rst"]:
                        fpost = os.path.join(full, post)
                        fLOG("    reading post", fpost)
                        obj = BlogPost(fpost, encoding=encoding,
                                       extensions=extensions)
                        self._blogposts.append((obj.date, obj))
        fLOG("[BlogPostList]    end reading post")
        self._blogposts.sort(reverse=True)
        self._blogposts = [_[1] for _ in self._blogposts]
        self._encoding = encoding
        self._language = language

    def __getitem__(self, key):
        """
        usual
        """
        return self._blogposts[key]

    @staticmethod
    def category2url(cat):
        """
        Removes accents and spaces to get a clean url.

        @param      cat     category name
        @return             cleaned category
        """
        return remove_diacritics(cat).replace(" ", "_")

    @property
    def Lang(self):
        """
        Returns the language.
        """
        return self._language

    def __iter__(self):
        """
        Iterates on @see cl BlogPost.
        """
        for obj in self._blogposts:
            yield obj

    def __len__(self):
        """
        Returns the number of blog posts.
        """
        return len(self._blogposts)

    def get_categories(self):
        """
        Extracts the categories.

        @return     list of sorted categories
        """
        cats = []
        for post in self:
            cats.extend(post.Categories)
        return list(sorted(set(cats)))

    def get_categories_group(self):
        """
        Extracts the categories with the posts associated to it.

        @return     dictionary (category, list of posts)
        """
        m = {}
        for post in self:
            for cat in post.Categories:
                if cat not in m:
                    m[cat] = []
                m[cat].append(post)
        return m

    def get_keywords(self):
        """
        Extracts the categories.

        @return     list of sorted keywords
        """
        keys = []
        for post in self:
            keys.extend(post.Keywords)
        return list(sorted(set(keys)))

    def get_months(self):
        """
        Extracts the months.

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            d = "-".join(post.Date.split("-")[:2])
            m.append(d)
        return list(sorted(set(m), reverse=True))

    def get_months_group(self):
        """
        Extracts the months with the posts associated to it.

        @return     dictionary (months, list of posts)
        """
        m = {}
        for post in self:
            d = "-".join(post.Date.split("-")[:2])
            if d not in m:
                m[d] = []
            m[d].append(post)
        return m

    def get_files(self):
        """
        Extracts the files.

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            m.append(post.FileName)
        return list(sorted(set(m), reverse=True))

    def get_rst_links_up(self):
        """
        Builds the :epkg:`rst` links to months or categories to displays
        at the beginning of the aggregated pages.

        @return         list of rst_links
        """
        ens = self.get_categories_group()
        if len(ens) > 5:
            sorted_end = list(sorted((v, m) for m, v in ens.items()))
            ens = {}
            for v, m in sorted_end[-5:]:
                ens[m] = v

        links = []
        for m, v in sorted(ens.items()):
            if len(v) <= 2:
                # we skip categories with less than 2 blog post
                continue
            link = ":ref:`{0} ({1}) <ap-cat-{0}-0>`".format(
                BlogPostList.category2url(m), len(v))
            links.append(link)
        return links

    def get_rst_links_down(self):
        """
        Builds the :epkg:`rst` links to months or categories to displays
        the bottom of the aggregated pages.

        @return         list of rst_links
        """
        ens = self.get_months_group()
        if len(ens) > 5:
            sorted_end = list(sorted((m, v) for m, v in ens.items()))
            ens = {}
            for m, v in sorted_end[-5:]:
                ens[m] = v

        links = []
        for m, v in sorted(ens.items()):
            link = ":ref:`{0} ({1}) <ap-month-{0}-0>`".format(m, len(v))
            links.append(link)
        return links

    def write_aggregated(self, folder, division=10,
                         blog_title="__BLOG_TITLE__",
                         blog_description="__BLOG_DESCRIPTION__",
                         blog_root="__BLOG_ROOT__",
                         only_html_index=True,
                         only_html_agg=False):
        """
        Writes posts in a aggregated manner (post, categories, months).

        @param      folder              where to write them
        @param      division            add a new page every *division* items
        @param      blog_title          blog title
        @param      blog_description    blog description
        @param      blog_root           blog root (publish url)
        @param      only_html_index     add item ``.. only:: html`` and indent everything
                                        after the main index
        @param      only_html_agg       add item ``.. only:: html`` and indent everything
                                        for aggregated pages
        @return                         list of produced files

        .. versionchanged:: 1.7
            Splits *only_html* into *only_html_index*
            and *only_html_agg*.
        """
        link_up = self.get_rst_links_up()
        link_down = self.get_rst_links_down()

        # rss
        rss = os.path.join(folder, "rss.xml")
        keep = []
        for _ in self:
            if len(keep) >= 10:
                break
            keep.append(_)
        c = build_rss(keep, blog_title=blog_title,
                      blog_description=blog_description,
                      blog_root=blog_root)
        with open(rss, "w", encoding=self._encoding) as f:
            f.write(c)

        # aggregated pages
        res = []
        res.extend(self.write_aggregated_posts(folder, division, rst_links_up=link_up,
                                               rst_links_down=link_down, only_html=only_html_agg))
        res.extend(self.write_aggregated_categories(folder, division, rst_links_up=link_up,
                                                    rst_links_down=link_down, only_html=only_html_agg))
        res.extend(self.write_aggregated_months(folder, division, rst_links_up=link_up,
                                                rst_links_down=link_down, only_html=only_html_agg))
        res.append(self.write_aggregated_index(
            folder, hidden_files=None, hidden_files_html=res, only_html=only_html_index))

        # final aggregator
        res.extend(self.write_aggregated_chapters(folder))

        return res

    def get_image(self, img):
        """
        Returns the local path to an image in this folder.

        @param      img     image name (see below)
        @return             local file

        Allowed image names:
            - rss: image for RSS stream
        """
        if img == "rss":
            img = "feed-icon-16x16.png"
            loc = os.path.abspath(os.path.dirname(__file__))
            img = os.path.join(loc, img)
            if not os.path.exists(img):
                raise FileNotFoundError("unable to find: " + img)
            return img
        else:
            raise FileNotFoundError("unable to get image name: " + img)

    def write_aggregated_index(self, folder, hidden_files=None, hidden_files_html=None, only_html=True):
        """
        Writes an index.

        @param      folder              where to write the file
        @param      hidden_files        creates an hidden *toctree* and a @see cl tocdelay_node.
        @param      only_html           add item ``.. only:: html`` and indent everything
                                        after the main index
        @param      hidden_files_html   add item ``.. only:: html`` for these pages
        @return                         filename

        .. versionchanged:: 1.7
            Parameter *hidden_files_html* was added.
        """
        indent = "    " if only_html else ""
        name = os.path.join(folder, "blogindex.rst")
        with open(name, "w", encoding=self._encoding) as f:
            f.write("\n")
            f.write(":orphan:\n")
            f.write("\n")
            f.write(".. _l-mainblog:\n")
            f.write("\n")
            f.write("\n")
            f.write("Blog Gallery\n")
            f.write("============\n")
            f.write("\n")
            f.write(".. tocdelay::\n")
            f.write("\n")
            for item in self:
                name_file = os.path.splitext(
                    os.path.split(item.FileName)[-1])[0]
                f.write("    {0} - {1} <{2}/{3}>\n".format(
                    item.Date, item.Title, item.Date[:4], name_file))
            f.write("\n\n")
            f.write(".. toctree::\n")
            f.write("    :hidden:\n")
            f.write("\n")
            for item_id, item in enumerate(self):
                fl = os.path.split(item.FileName)[-1]
                fl = os.path.splitext(fl)[0]
                f.write(
                    "    blog {2} <{0}/{1}>\n".format(item.Date[:4], fl, item_id))

            if hidden_files is not None:
                f.write("\n\n")
                f.write(".. toctree::\n")
                f.write("    :hidden:\n")
                f.write("\n")
                for hid, h in enumerate(hidden_files):
                    f.write("    blog {1} <{0}>\n".format(
                        os.path.splitext(os.path.split(h)[-1])[0], hid))
                f.write("\n\n")

            if only_html:
                f.write("\n\n")
                f.write(".. only:: html\n\n")

            if hidden_files_html is not None:
                f.write(indent + ".. toctree::\n")
                f.write(indent + "    :hidden:\n")
                f.write("\n")
                for item_id, item in enumerate(self):
                    fl = os.path.split(item.FileName)[-1]
                    fl = os.path.splitext(fl)[0]
                    f.write(
                        indent + "    {2} <{0}/{1}>\n".format(item.Date[:4], fl, item_id))
                for hid, h in enumerate(hidden_files_html):
                    f.write(
                        indent + "    blog {1} <{0}>\n".format(os.path.splitext(os.path.split(h)[-1])[0], hid))
                f.write("\n\n")

            f.write("\n")
            f.write(indent + ".. image:: feed-icon-16x16.png\n\n")
            f.write(
                indent + ":download:`{0} rss <rss.xml>`\n".format(TITLES[self.Lang]["download"]))
            f.write("\n\n\n")

            f.write(
                indent + ":ref:`{0} <hblog-blog>`, ".format(TITLES[self.Lang]["main"]))
            f.write(
                indent + ":ref:`{0} <ap-main-0>`".format(TITLES[self.Lang]["main2"]))
            f.write("\n\n\n")

            img = self.get_image("rss")
            shutil.copy(img, folder)

        return name

    def write_aggregated_posts(self, folder, division=10, rst_links_up=None,
                               rst_links_down=None, only_html=True):
        """
        Writes posts in a aggregated manner.

        @param      folder          where to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      only_html       add item ``.. only:: html`` and indent everything
        @return                     list of produced files
        """
        return BlogPostList.write_aggregated_post_list(folder=folder,
                                                       lp=list(
                                                           _ for _ in self),
                                                       division=division,
                                                       prefix="main",
                                                       encoding=self._encoding,
                                                       rst_links_up=rst_links_up,
                                                       rst_links_down=rst_links_down,
                                                       index_terms=["blog"],
                                                       language=self.Lang,
                                                       bold_title=TITLES[self.Lang]["main_title"],
                                                       only_html=only_html)

    def write_aggregated_categories(self, folder, division=10, rst_links_up=None,
                                    rst_links_down=None, only_html=True):
        """
        Writes posts in a aggregated manner per categories.

        @param      folder          where to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      only_html       add item ``.. only:: html`` and indent everything
        @return                     list of produced files
        """
        cats = self.get_categories()
        res = []
        for cat in cats:
            posts = [_ for _ in self if cat in _.Categories]
            url_cat = BlogPostList.category2url(cat)
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          lp=posts,
                                                          division=division,
                                                          prefix="cat-" + url_cat,
                                                          encoding=self._encoding,
                                                          rst_links_up=rst_links_up,
                                                          rst_links_down=rst_links_down,
                                                          index_terms=[cat],
                                                          bold_title=cat,
                                                          only_html=only_html)
            res.extend(add)
        return res

    def write_aggregated_months(self, folder, division=10, rst_links_up=None,
                                rst_links_down=None, only_html=True):
        """
        Writes posts in a aggregated manner per months.

        @param      folder          where to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      only_html       add item ``.. only:: html`` and indent everything
        @return                     list of produced files
        """
        mo = self.get_months()
        res = []
        for m in mo:
            posts = [_ for _ in self if _.Date.startswith(m)]
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          lp=posts,
                                                          division=division,
                                                          prefix="month-" + m,
                                                          encoding=self._encoding,
                                                          rst_links_up=rst_links_up, rst_links_down=rst_links_down,
                                                          index_terms=[m],
                                                          bold_title=m,
                                                          only_html=only_html)
            res.extend(add)
        return res

    def write_aggregated_chapters(self, folder):
        """
        Writes links to post per categories and per months.

        @param      folder          where to write them
        @return                     list of produced files
        """
        cats = sorted([(k, len(v))
                       for k, v in self.get_categories_group().items()])
        months = sorted(
            [(k, len(v)) for k, v in self.get_months_group().items()], reverse=True)
        res = ["", ":orphan:", "", ".. _hblog-blog:",
               "", "", "Blog", "====", "", ""]
        res.extend(
            ["* :ref:`{0} <ap-main-0>`".format(TITLES[self.Lang]["page1"]), "", ""])
        res.extend([TITLES[self.Lang]["by category:"], "", ""])
        for cat, nb in cats:
            res.append(
                "* :ref:`{0} ({1}) <ap-cat-{0}-0>`".format(BlogPostList.category2url(cat), nb))
        res.extend(["", "", ""])
        res.extend([TITLES[self.Lang]["by month:"], "", ""])
        res.extend(["", "", ""])
        for mon, nb in months:
            res.append("* :ref:`{0} ({1}) <ap-month-{0}-0>`".format(mon, nb))

        res.extend(["", "", ""])
        res.extend([TITLES[self.Lang]["by title:"], "", ""])
        res.extend(
            ["", "", ":ref:`{0} <l-mainblog>`".format(TITLES[self.Lang]["allblogs"]), "", ""])

        filename = os.path.join(folder, "index_blog.rst")
        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(res))
        return [filename]

    #################
    # static methods
    #################

    @staticmethod
    def divide_list(ld, division):
        """
        Divides a list into buckets of *division* items.

        @param      ld          list of to divide
        @param      division    bucket size
        @return                 list fo buckets
        """
        buckets = []
        current = []
        for obj in ld:
            if len(current) < division:
                current.append(obj)
            else:
                buckets.append(current)
                current = [obj]
        if len(current) > 0:
            buckets.append(current)
        return buckets

    @staticmethod
    def write_aggregated_post_list(folder, lp, division, prefix, encoding,
                                   rst_links_up=None, rst_links_down=None, index_terms=None,
                                   bold_title=None, language="en", only_html=True):
        """
        Writes list of posts in an aggregated manners.

        @param      folder          when to write the aggregated posts
        @param      lp              list of posts
        @param      division        bucket size
        @param      prefix          prefix name for the files
        @param      encoding        encoding for the written files
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      index_terms     terms to index on the first bucket
        @param      bold_title      title to display at the beginning of the page
        @param      language        language
        @param      only_html       add item ``.. only:: html`` and indent everything
        @return                     list of produced files
        """
        res = []
        buckets = BlogPostList.divide_list(lp, division)
        for i, b in enumerate(buckets):
            if bold_title is not None:
                title = "{0} - {1}/{2}".format(bold_title, i + 1, len(buckets))
            else:
                title = None
            name = os.path.join(folder, "%s_%04d.rst" % (prefix, i))
            prev = "ap-%s-%d" % (prefix, i - 1) if i > 0 else None
            this = "ap-%s-%d" % (prefix, i)
            next = "ap-%s-%d" % (prefix, i + 1) \
                   if i < len(buckets) - 1 else None
            content = BlogPostList.produce_aggregated_post_page(
                name, b, this, prev, next,
                rst_links_up=rst_links_up,
                rst_links_down=rst_links_down,
                index_terms=index_terms if i == 0 else None,
                bold_title=title, language=language)
            if only_html:
                lines = content.split("\n")
                head = "\n:orphan:\n\n.. only:: html\n\n"
                content = head + "\n".join("    " + _ for _ in lines)
            with open(name, "w", encoding=encoding) as f:
                f.write(content)
            res.append(name)
        return res

    @staticmethod
    def produce_aggregated_post_page(name, lp, this, prev, next, main_page="Blog",
                                     rst_links_up=None, rst_links_down=None,
                                     index_terms=None, bold_title=None, language="en"):
        """
        Writes the content of an aggregate page of blog posts.

        @param      name            filename to write
        @param      lp              list of posts
        @param      this            reference to this page
        @param      prev            reference to the previous page
        @param      next            reference to the next page
        @param      main_page       name of the main page
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      index_terms     terms to index
        @param      bold_title      title to display of the beginning of the page
        @param      language        language
        @return                     content of the page
        """
        direction = "|rss_image| "
        if prev is not None:
            direction += ":ref:`<== <%s>` " % prev
        if bold_title is not None:
            if len(direction) > 0:
                direction += " "
            direction += "**{0}**".format(bold_title)
        if next is not None:
            if len(direction) > 0:
                direction += " "
            direction += ":ref:`==> <%s>`" % next
        arrows = direction
        if main_page is not None:
            if len(direction) > 0:
                direction += " "
            direction += ":ref:`%s <ap-main-0>`" % main_page
        if rst_links_up is not None:
            if len(direction) > 0:
                direction += " "
            direction += " ".join(rst_links_up)

        rows = []
        rows.append("")
        rows.append(":orphan:")
        rows.append("")
        rows.append(direction)
        rows.append("")
        rows.append(".. |rss_image| image:: feed-icon-16x16.png")
        rows.append("    :target: ../_downloads/rss.xml")
        rows.append("    :alt: RSS")
        rows.append("")
        rows.append("----")
        rows.append("")

        if index_terms is not None:
            rows.append("")
            rows.append(".. index:: " + ",".join(index_terms))
            rows.append("")

        rows.append("")
        rows.append(".. _%s:" % this)
        rows.append("")

        if bold_title is not None:
            rows.append(bold_title)
            rows.append("+" * len(bold_title))
            rows.append("")

        for post in lp:
            text = post.post_as_rst(language=language, cut=True)
            rows.append(text)
            rows.append("")
            rows.append("")

        rows.append("")
        rows.append("----")
        rows.append("")
        if rst_links_down is not None:
            if len(arrows) > 0:
                arrows += " "
            arrows += " ".join(rst_links_down)
        rows.append(arrows)

        return "\n".join(rows)
