
.. blogpost::
    :title: Create a script to read this blog
    :keywords: script
    :date: 2015-05-10
    :categories: automation, blog

    The module now includes a function
    :func:`write_module_scripts <pyquickhelper.pycode.setup_helper.write_module_scripts>`
    creates a script *auto_rss_server.py* which grabs the latest blog post
    from this stream, runs a server and opens the default browser to read them.
    It uses the module
    `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_.
    Here is the code to read this blog::

        from pyquickhelper import write_module_scripts, __blog__
        write_module_scripts("blog", blog_list=__blog__)

    The blog list can be replaced by any other one.
    Here is its content::

        <?xml version="1.0" encoding="UTF-8"?>
        <opml version="1.0">
            <head>
                <title>blog</title>
            </head>
            <body>
                <outline text="pyquickhelper"
                    title="pyquickhelper"
                    type="rss"
                    xmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_downloads/rss.xml"
                    htmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/blog/main_0000.html" />
            </body>
        </opml>
