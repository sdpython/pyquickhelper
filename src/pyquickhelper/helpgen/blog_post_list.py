# -*- coding: utf-8 -*-
"""
@file
@brief Helpers to build RST extra files inserted in the documentation
"""

import os
from .blog_post import BlogPost


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
        extract the categories

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            d = "-".join(post.Date.split("-")[:2])
            m.append(d)
        return list(sorted(set(m), reverse=True))

    def get_files(self):
        """
        extract the files

        @return     list of sorted months (more recent first)
        """
        m = []
        for post in self:
            m.append(post.FileName)
        return list(sorted(set(m), reverse=True))

    def write_aggregated(self, folder, division=10):
        """
        writes posts in a aggregated manner (post, categories, months)

        @param      folder      when to write them
        @param      division    add a new page every *division* items
        @return                 list of produced files
        """
        res = []
        res.extend(self.write_aggregated_posts(folder, division))
        res.extend(self.write_aggregated_categories(folder, division))
        res.extend(self.write_aggregated_months(folder, division))
        res.append(self.write_aggregated_index(folder))
        return res

    def write_aggregated_index(self, folder):
        """
        writes an index

        @param      folder      where to write the file
        @return                 filename
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
        return name

    def write_aggregated_posts(self, folder, division=10):
        """
        writes posts in a aggregated manner

        @param      folder      when to write them
        @param      division    add a new page every *division* items
        @return                 list of produced files
        """
        return BlogPostList.write_aggregated_post_list(folder=folder,
                                                       l=list(_ for _ in self),
                                                       division=division, prefix="main",
                                                       encoding=self._encoding)

    def write_aggregated_categories(self, folder, division=10):
        """
        writes posts in a aggregated manner per categories

        @param      folder      when to write them
        @param      division    add a new page every *division* items
        @return                 list of produced files
        """
        cats = self.get_categories()
        res = []
        for cat in cats:
            posts = [_ for _ in self if cat in _.Categories]
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          l=posts,
                                                          division=division, prefix="cat",
                                                          encoding=self._encoding)
            res.extend(add)
        return res

    def write_aggregated_months(self, folder, division=10):
        """
        writes posts in a aggregated manner per months

        @param      folder      when to write them
        @param      division    add a new page every *division* items
        @return                 list of produced files
        """
        mo = self.get_months()
        res = []
        for m in mo:
            posts = [_ for _ in self if _.Date.startswith(m)]
            add = BlogPostList.write_aggregated_post_list(folder=folder,
                                                          l=posts,
                                                          division=division, prefix="month",
                                                          encoding=self._encoding)
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
                curent = []
        if len(current) > 0:
            buckets.append(current)
        return buckets

    @staticmethod
    def write_aggregated_post_list(folder, l, division, prefix, encoding):
        """
        write list of posts in an aggregated manners

        @param      folder      when to write the aggregated posts
        @param      l           list of posts
        @param      division    bucket size
        @param      prefix      prefix name for the files
        @param      encoding    encoding for the written files
        @return                 list of produced files
        """
        res = []
        buckets = BlogPostList.divide_list(l, division)
        for i, b in enumerate(buckets):
            name = os.path.join(folder, "%s_%04d.rst" % (prefix, i))
            prev = "ap-%s-%d" % (prefix, i - 1) if i > 0 else None
            this = "ap-%s-%d" % (prefix, i)
            next = "ap-%s-%d" % (prefix, i +
                                 1) if i < len(buckets) - 1 else None
            content = BlogPostList.produce_aggregated_post_page(
                name, b, this, prev, next)
            with open(name, "w", encoding=encoding) as f:
                f.write(content)
            res.append(name)
        return res

    @staticmethod
    def produce_aggregated_post_page(name, l, this, prev, next, main_page="Blog"):
        """
        write the content of an aggregate page of blog posts

        @param      name        filename to write
        @param      l           list of posts
        @param      this        reference to this page
        @param      prev        reference to the previous page
        @param      next        reference to the next page
        @param      main_page   name of the main page
        @return                 content of the page
        """
        rows = []
        rows.append("")
        rows.append(":ref:`%s <ap-main_-0>`" % main_page)
        rows.append("")
        rows.append(".. _%s:" % this)
        rows.append("")
        for post in l:
            text = post.post_as_rst()
            rows.append(text)
            rows.append("")
            rows.append("")

        rows.append(".. raw::")
        rows.append("")
        rows.append("    <hr />")
        rows.append("")
        rows.append("")
        line = ""
        if prev is not None:
            line += ":ref:`<-- <%s>`" % prev
        if prev is not None and next is not None:
            line += " . "
        if next is not None:
            line += ":ref:`<-- <%s>`" % next
        rows.append(line)
        rows.append("")

        return "\n".join(rows)
