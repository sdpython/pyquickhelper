"""
@file
@brief Function which starts a server to grab and read blog post for a mobule
based on pyqcuikhelper design. It relies on module :epkg:`pyrsslocal`.
"""

import os


def rss_update_run_server(dbfile=None, xml_blogs=None, port=8093, browser=None,
                          period="week", server=None, thread=False):  # pragma: no cover
    """
    Creates a database if it does not exists, add a table for blogs and posts,
    update the database, starts a server and open a browser,
    if *dbfile* is None, it is set to a default values (in your user directory),
    if *xml_blogs* is None, it is given a default value corresponding the the blogs
    the modules developped for these teachings.

    @param      dbfile      (str) sqllite database to create, if None,
                            the function creates a file in the current folder
    @param      xml_blogs   (str) xml description of blogs (google format), if None,
                            the function chooses the string ``__blog__`` of this module,
                            it can be a file or a string
    @param      port        the main page will be ``http://localhost:port/``
    @param      browser     (str) to choose a different browser than the default one
    @param      period      (str) when opening the browser, it can show the results for last day or last week
    @param      server      to set up your own server
    @param      thread      to start the server in a separate thread

    Example::

        from ensae_teaching_cs.automation import rss_teachings_update_run_server
        rss_teachings_update_run_server(browser="firefox")
    """
    from pyrsslocal import rss_update_run_server
    if xml_blogs is None:
        raise ValueError("xml_blogs cannot be None")
    if dbfile is None:
        dbfile = os.path.join(os.path.dirname(xml_blogs), "rss_blog_posts.db3")

    return rss_update_run_server(dbfile=dbfile, xml_blogs=xml_blogs, port=port, browser=browser,
                                 period=period, server=server, thread=thread)
