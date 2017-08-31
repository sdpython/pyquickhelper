# coding:utf-8
"""
@file
@brief Buid the RSS stream.
"""
import datetime
import os
from xml.sax.saxutils import escape

modelForARSSFeed = """<rss version="2.0">
                        <channel>
                            <title>{0.blogtitle}</title>
                            <link>{0.root}/blog/main_0000.html</link>
                            <description>{0.description}</description>
                            """.replace("                        ", "")

modelForARSSRow = """<item>
            <title>{0.title}</title>
            <link>{0.root}/blog/{0.year}/{0.name}.html</link>
            <guid isPermaLink="true">{0.root}/blog/{0.year}/{0.name}.html</guid>
            <description>{0.decription}</description>
            <pubDate>{0.date}</pubDate>
        </item>"""

modelForARSSChannel = """\n</channel>\n</rss>\n"""


def build_rss(posts,
              blog_title="__BLOG_TITLE__",
              blog_root="__BLOG_ROOT__",
              blog_description="__BLOG_DESCRIPTION__",
              now=datetime.datetime.now(),
              model_feed=modelForARSSFeed,
              model_row=modelForARSSRow,
              model_channel=modelForARSSChannel):
    """
    Build a RSS file, the function keeps the blog post (HTML format) from the last month.
    The summary will only contains the part included in those two comments.

    @param  posts               list of posts to include
    @param  blog_title          title of the blog
    @param  blog_description    description of the blog
    @param  blog_root           url root
    @param  now                 date to use as a final date, only blog post between one month now and now will be kept
    @param  model_feed          see model_channel
    @param  model_row           see model_row
    @param  model_channel       the part related to a post in the rss stream is composed
                                by the concatenation of the three stream:
                                *model_feed*, *model_row*, *model_channel*.
                                You should see the default value to see how you can replace them.
    @return                     2-uple: content of the file
    """

    class EmptyClass:
        pass

    obj = EmptyClass()
    obj.blogtitle = blog_title
    obj.root = blog_root
    obj.description = blog_description

    rows = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>"]
    rows.append(modelForARSSFeed.format(obj))

    for post in posts:
        obj = EmptyClass()
        obj.title = escape(post.Title)
        obj.date = post.Date
        obj.year = post.Date[:4]
        obj.name = escape(
            os.path.splitext(os.path.split(post.FileName)[-1])[0])
        obj.decription = escape("\n".join(post.Content))
        obj.root = blog_root
        row = modelForARSSRow.format(obj)
        rows.append(row)

    rows.append(modelForARSSChannel)
    content = "\n".join(rows)

    return content
