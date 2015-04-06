# -*- coding: utf-8 -*-
"""
@file
@brief Helpers to build RST extra files inserted in the documentation
"""

import os
import shutil
from .blog_post import BlogPost
from .build_rss import build_rss
from .texts_language import TITLES


class BlogPostList:

    """
    defines a list of @see cl BlogPost
    """

    def __init__(self, folder, encoding="utf8", language="en"):
        """
        create a list of BlogPost, we assume each blog post belongs to a sub-folder *YYYY*

        @param      folder          folder when to find files
        @param      encoding        encoding
        @param      language        language

        """
        self._blogposts = []
        sub = os.listdir(folder)
        for s in sub:
            full = os.path.join(folder, s)
            if os.path.isdir(full):
                posts = os.listdir(full)
                for post in posts:
                    fpost = os.path.join(full, post)
                    obj = BlogPost(fpost, encoding=encoding)
                    self._blogposts.append((obj.date, obj))
        self._blogposts.sort(reverse=True)
        self._blogposts = [_[1] for _ in self._blogposts]
        self._encoding = encoding
        self._language = language

    @property
    def Lang(self):
        """
        returns the language
        """
        return self._language

    def __iter__(self):
        """
        iterator on BlogPost
        """
        for obj in self._blogposts:
            yield obj

    def __len__(self):
        """
        returns the number of blog posts
        """
        return len(self._blogposts)

    def get_categories(self):
        """
        extract the categories

        @return     list of sorted categories
        """
        cats = []
        for post in self:
            cats.extend(post.Categories)
        return list(sorted(set(cats)))

    def get_categories_group(self):
        """
        extract the categories with the posts associated to it

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
        extract the categories

        @return     list of sorted keywords
        """
        keys = []
        for post in self:
            keys.extend(post.Keywords)
        return list(sorted(set(keys)))

    def get_months(self):
        """
        extract the months

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            d = "-".join(post.Date.split("-")[:2])
            m.append(d)
        return list(sorted(set(m), reverse=True))

    def get_months_group(self):
        """
        extract the months with the posts associated to it

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
        extract the files

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            m.append(post.FileName)
        return list(sorted(set(m), reverse=True))

    def get_rst_links_up(self):
        """
        builds the rst links to months or categories to displays the beginning of the aggregated pages

        @return         list of rst_links
        """
        links = []
        for m, v in sorted(self.get_categories_group().items()):
            link = ":ref:`{0} ({1}) <ap-cat-{0}-0>`".format(m, len(v))
            links.append(link)
        return links

    def get_rst_links_down(self):
        """
        builds the rst links to months or categories to displays the bottom of the aggregated pages

        @return         list of rst_links
        """
        links = []
        for m, v in sorted(self.get_months_group().items()):
            link = ":ref:`{0} ({1}) <ap-month-{0}-0>`".format(m, len(v))
            links.append(link)
        return links

    def write_aggregated(self, folder, division=10,
                         blog_title="__BLOG_TITLE__",
                         blog_description="__BLOG_DESCRIPTION__",
                         blog_root="__BLOG_ROOT__"):
        """
        writes posts in a aggregated manner (post, categories, months)

        @param      folder              when to write them
        @param      division            add a new page every *division* items
        @param      blog_title          blog title
        @param      blog_description    blog description
        @param      blog_title          blog root (publish url)
        @return                         list of produced files
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
        res.extend(self.write_aggregated_posts(
            folder, division, rst_links_up=link_up, rst_links_down=link_down))
        res.extend(self.write_aggregated_categories(
            folder, division, rst_links_up=link_up, rst_links_down=link_down))
        res.extend(self.write_aggregated_months(
            folder, division, rst_links_up=link_up, rst_links_down=link_down))
        res.append(self.write_aggregated_index(folder, hidden_files=res))
        return res

    def get_image(self, img):
        """
        return the local path to an image in this folder

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

    def write_aggregated_index(self, folder, hidden_files=None):
        """
        writes an index

        @param      folder          where to write the file
        @param      hidden_files    creates an hidden toctree
        @return                     filename
        """
        name = os.path.join(folder, "blogindex.rst")
        with open(name, "w", encoding=self._encoding) as f:
            f.write("\n")
            f.write(".. _l-mainblog:\n")
            f.write("\n")
            f.write("\n")
            f.write("Blog\n")
            f.write("====\n")
            f.write("\n")
            f.write(".. toctree::\n")
            f.write("\n")
            for item in self:
                f.write(
                    "    {0}/{1}\n".format(item.Date[:4], os.path.split(item.FileName)[-1]))
            f.write("\n\n")
            if hidden_files is not None:
                f.write(".. toctree::\n")
                f.write("    :hidden:\n")
                f.write("\n")
                for h in hidden_files:
                    f.write("    " + os.path.split(h)[-1] + "\n")
                f.write("\n")

            f.write("\n")
            f.write(".. image:: feed-icon-16x16.png\n")
            f.write(":download:`{0} rss <rss.xml>`\n".format(
                TITLES[self.Lang]["download"]))
            f.write("\n")

            img = self.get_image("rss")
            shutil.copy(img, folder)

        return name

    def write_aggregated_posts(self, folder, division=10,
                               rst_links_up=None, rst_links_down=None):
        """
        writes posts in a aggregated manner

        @param      folder          when to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @return                     list of produced files
        """
        return BlogPostList.write_aggregated_post_list(folder=folder,
                                                       l=list(_ for _ in self),
                                                       division=division,
                                                       prefix="main",
                                                       encoding=self._encoding,
                                                       rst_links_up=rst_links_up,
                                                       rst_links_down=rst_links_down,
                                                       index_terms=["blog"])

    def write_aggregated_categories(self, folder, division=10,
                                    rst_links_up=None, rst_links_down=None):
        """
        writes posts in a aggregated manner per categories

        @param      folder          when to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @return                     list of produced files
        """
        cats = self.get_categories()
        res = []
        for cat in cats:
            posts = [_ for _ in self if cat in _.Categories]
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          l=posts,
                                                          division=division,
                                                          prefix="cat-" + cat,
                                                          encoding=self._encoding,
                                                          rst_links_up=rst_links_up,
                                                          rst_links_down=rst_links_down,
                                                          index_terms=[cat],
                                                          bold_title=cat)
            res.extend(add)
        return res

    def write_aggregated_months(self, folder, division=10,
                                rst_links_up=None, rst_links_down=None):
        """
        writes posts in a aggregated manner per months

        @param      folder          when to write them
        @param      division        add a new page every *division* items
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @return                     list of produced files
        """
        mo = self.get_months()
        res = []
        for m in mo:
            posts = [_ for _ in self if _.Date.startswith(m)]
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          l=posts,
                                                          division=division,
                                                          prefix="month-" + m,
                                                          encoding=self._encoding,
                                                          rst_links_up=rst_links_up, rst_links_down=rst_links_down,
                                                          index_terms=[m],
                                                          bold_title=m)
            res.extend(add)
        return res

    #################
    # static methods
    #################

    @staticmethod
    def divide_list(l, division):
        """
        divides a list into buckets of *division* items

        @param      l           list of to divide
        @param      division    bucket size
        @return                 list fo buckets
        """
        buckets = []
        current = []
        for obj in l:
            if len(current) < division:
                current.append(obj)
            else:
                buckets.append(current)
                current = []
        if len(current) > 0:
            buckets.append(current)
        return buckets

    @staticmethod
    def write_aggregated_post_list(folder, l, division, prefix, encoding,
                                   rst_links_up=None, rst_links_down=None, index_terms=None,
                                   bold_title=None):
        """
        write list of posts in an aggregated manners

        @param      folder          when to write the aggregated posts
        @param      l               list of posts
        @param      division        bucket size
        @param      prefix          prefix name for the files
        @param      encoding        encoding for the written files
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      index_terms     terms to index on the first bucket
        @param      bold_title      title to display at the beginning of the page
        @return                     list of produced files
        """
        res = []
        buckets = BlogPostList.divide_list(l, division)
        for i, b in enumerate(buckets):
            if bold_title is not None:
                title = "{0} - {1}/{2}".format(bold_title, i + 1, len(buckets))
            else:
                title = None
            name = os.path.join(folder, "%s_%04d.rst" % (prefix, i))
            prev = "ap-%s-%d" % (prefix, i - 1) if i > 0 else None
            this = "ap-%s-%d" % (prefix, i)
            next = "ap-%s-%d" % (prefix, i +
                                 1) if i < len(buckets) - 1 else None
            content = BlogPostList.produce_aggregated_post_page(
                name, b, this, prev, next,
                rst_links_up=rst_links_up,
                rst_links_down=rst_links_down,
                index_terms=index_terms if i == 0 else None,
                bold_title=title)
            with open(name, "w", encoding=encoding) as f:
                f.write(content)
            res.append(name)
        return res

    @staticmethod
    def produce_aggregated_post_page(name, l, this, prev, next, main_page="Blog",
                                     rst_links_up=None, rst_links_down=None,
                                     index_terms=None,
                                     bold_title=None):
        """
        write the content of an aggregate page of blog posts

        @param      name            filename to write
        @param      l               list of posts
        @param      this            reference to this page
        @param      prev            reference to the previous page
        @param      next            reference to the next page
        @param      main_page       name of the main page
        @param      rst_links_up    list of rst_links to add at the beginning of a page
        @param      rst_links_down  list of rst_links to add at the bottom of a page
        @param      index_terms     terms to index
        @param      bold_title      title to display of the beginning of the page
        @return                     content of the page
        """
        direction = "|rss_image| "
        if prev is not None:
            direction += ":ref:`<-- <%s>` " % prev
        if bold_title is not None:
            if len(direction) > 0:
                direction += " "
            direction += "**{0}**".format(bold_title)
        if next is not None:
            if len(direction) > 0:
                direction += " "
            direction += ":ref:`<-- <%s>`" % next
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
        rows.append(direction)
        rows.append("")
        rows.append(".. |rss_image| image:: feed-icon-16x16.png")
        rows.append("    :target: ../_downloads/rss.xml")
        rows.append("    :alt: RSS")
        rows.append("")
        rows.append(".. raw:: html")
        rows.append("")
        rows.append("    <hr />")

        if index_terms is not None:
            rows.append("")
            rows.append(".. index:: " + ",".join(index_terms))
            rows.append("")

        rows.append("")
        rows.append(".. _%s:" % this)
        rows.append("")
        for post in l:
            text = post.post_as_rst()
            rows.append(text)
            rows.append("")
            rows.append("")
            rows.append(":ref:`... <{0}>`".format(post.Tag))
            rows.append("")
            rows.append("")

        rows.append(".. raw:: html")
        rows.append("")
        rows.append("    <hr />")
        rows.append("")
        rows.append("")
        if rst_links_down is not None:
            if len(arrows) > 0:
                arrows += " "
            arrows += " ".join(rst_links_down)
        rows.append(arrows)

        return "\n".join(rows)
