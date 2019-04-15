"""
@file
@brief function around missing file for the documentation
"""
import os
import shutil
from ..texthelper.texts_language import TITLES


def add_missing_files(root, conf, blog_list, fLOG):
    """
    Adds missing files for the documentation,
    ``moduletoc.html``, ``blogtoc.html``, ``searchbox.html``.

    @param      root        root
    @param      conf        configuration module (to guess the template folder)
    @param      blog_list   list of recent blog posts to add to the navigational bar (list)
                            or a name for a placeholder (such as ``__INSERT__``)
    @param      theme       theme, missing files depend on it
    @param      fLOG        logging function
    @return                 list of modified files

    The function considers the theme for the searchbox.
    `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_ has
    a different style for the searchbox.
    """
    # settings
    fold = conf.templates_path
    if isinstance(fold, list):
        fold = fold[0]

    if hasattr(conf, "language"):
        language = conf.language
    else:
        language = "en"

    if hasattr(conf, "extensions"):
        lunr = "sphinxcontrib.lunrsearch" in conf.extensions
    else:
        lunr = False

    loc = os.path.join(root, "_doc", "sphinxdoc", "source", fold)
    if not os.path.exists(loc):
        os.makedirs(loc)

    api_index = os.path.join(root, "_doc", "sphinxdoc",
                             "source", "api", "index.rst")
    add_api_link = os.path.exists(api_index)
    if add_api_link:
        api_title = extract_first_title(api_index)

    tocs = []

    # link
    link = '\n<li class="toctree-l1"><a class="reference internal" href="{0}">{1}</a></li>'
    double_link = '\n<li class="toctree-l1"><a class="reference internal" href="{0}">{1}</a></li>' + \
                  '\n<li class="toctree-l1"><a class="reference internal" href="{2}">{3}</a></li>'

    # moduletoc.html
    mt = os.path.join(loc, "moduletoc.html")
    if fLOG:
        fLOG("[add_missing_files] create '{}'".format(mt))
    tocs.append(mt)
    with open(mt, "w", encoding="utf8") as f:
        f.write("\n<h3>{0}</h3>".format(TITLES[language]["toc0"]))
        f.write("\n<ul>")
        f.write(link.format("{{ pathto('',1) }}/blog/main_0000.html", "Blog"))
        f.write(link.format("{{ pathto('',1) }}/genindex.html", "Index"))
        if add_api_link:
            f.write(double_link.format("{{ pathto('',1) }}/py-modindex.html", "Module",
                                       "{{ pathto('',1) }}/api/index.html", api_title))
        else:
            f.write(link.format(
                "{{ pathto('',1) }}/py-modindex.html", "Module"))
        # f.write("""{%- if prev or next %}<li class="toctree-l1">
        #        {%- if prev %}<a href="{{ prev.link|e }}">&lt;--</a>{%- endif %}
        #        {%- if next %}<a href="{{ next.link|e }}">--&gt;</a>{%- endif %}
        #        </li>{%- endif %}""")
        f.write("\n</ul>")
        f.write(
            '\n<h3><a href="{{ pathto(master_doc) }}">%s</a></h3>\n' % TITLES[language]["toc"])
        f.write('{{ toctree() }}')
        f.write("\n<h3>{0}</h3>".format(TITLES[language]["toc1"]))
        f.write("\n<ul>")
        f.write(
            link.format("{{ pathto('',1) }}/i_faq.html", TITLES[language]["FAQ"]))
        f.write(
            link.format("{{ pathto('',1) }}/glossary.html", TITLES[language]["glossary"]))
        f.write(link.format("{{ pathto('',1) }}/README.html", "README"))
        f.write(
            link.format("{{ pathto('',1) }}/filechanges.html", TITLES[language]["changes"]))
        f.write(
            link.format("{{ pathto('',1) }}/license.html", TITLES[language]["license"]))
        f.write("\n</ul>")

    # blogtoc.html
    mt = os.path.join(loc, "blogtoc.html")
    if fLOG:
        fLOG("[add_missing_files] create '{}'".format(mt))
    tocs.append(mt)
    with open(mt, "w", encoding="utf8") as f:
        f.write("""<a href="{{ pathto('',1) }}/genindex.html">Index</a>\n""")
        f.write(
            """<a href="{{ pathto('',1) }}/py-modindex.html">Module</a>\n""")
        f.write(
            """<h3><a href="{{ pathto('',1) }}/blog/main_0000.html">Blog</a></h3>\n""")
        if isinstance(blog_list, str):
            f.write(blog_list)
        elif isinstance(blog_list, list):
            f.write("\n<br />".join(blog_list))
        else:
            raise TypeError(type(blog_list))

    # searchbox.html
    theme = conf.theme
    mt = os.path.join(loc, "searchbox.html")
    if fLOG:
        fLOG("[add_missing_files] create '{}'".format(mt))
    tocs.append(mt)
    with open(mt, "w", encoding="utf8") as f:
        if theme == "sphinx_rtd_theme":
            text = """
                    {%- if builder != 'singlehtml' %}
                    <div role="search">
                      <form id="rtd-search-form" class="wy-form" action="{{ pathto('search') }}" method="get">
                        <input type="text" name="q" placeholder="{{ _('Search docs') }}" />
                        <input type="hidden" name="check_keywords" value="yes" />
                        <input type="hidden" name="area" value="default" />
                      </form>
                    </div>
                    <script type="text/javascript">$('#searchbox').show(0);</script>
                    {%- endif %}
                    """.replace("                    ", "")
        else:
            text = """
                    {%- if pagename != "search" and builder != "singlehtml" %}
                    <div id="searchbox" style="display: none" role="search">
                    <form class="search" action="{{ pathto('search') }}" method="get">
                    <input type="text" name="q" />
                    <input type="submit" value="{{ _('Go') }}" />
                    <input type="hidden" name="check_keywords" value="yes" />
                    <input type="hidden" name="area" value="default" />
                    </form>
                    <p class="searchtip" style="font-size: 10%"> </p>
                    </div>
                    <script type="text/javascript">$('#searchbox').show(0);</script>
                    {%- endif %}
                    """.replace("                    ", "")
        f.write(text)

        if lunr:
            text = """
                <script src="{{ pathto('_static/js/searchbox.js', 1) }}" type="text/javascript"></script>
                <script type="text/javascript" id="lunrsearchindexloader"></script>
                <form class="lunsearch" action="" method="get">
                <input type="hidden" name="check_keywords" value="yes" />
                <input type="hidden" name="area" value="default" />
                <input type="hidden" id="ls_lunrsearch-highlight" value="{{ lunrsearch_highlight }}" />
                <input type="hidden" id="ls_search-index-url" value="{{ pathto('searchindex.js', 1) }}"/>
                <input type="text" class="search-field" id="ls_search-field" name="q" placeholder="Search API" />
                <ul class="results" id="ls_search-results"></ul>
                </form>
                """.replace("                ", "")
            f.write(text)

    missings = []  # ['layout.html', 'page.html']
    import sphinx
    themes = os.path.join(os.path.dirname(sphinx.__file__), "themes", "basic")
    for mis in missings:
        mt = os.path.join(loc, mis)
        if not os.path.exists(mt):
            sr = os.path.join(themes, mis)
            if os.path.exists(sr):
                if fLOG:
                    fLOG("[add_missing_files] create '{}'".format(mt))
                shutil.copy(sr, loc)
    return tocs


def extract_first_title(filename, underline="="):
    """
    Extracts the first title (rst format) in a file.

    @param      filename        filename
    @param      underline       level of the title
    @return                     title name (or raises an exception if not found)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    look = {underline}
    for i, line in enumerate(lines):
        sline = line.strip("\t\r\n ")
        car = set(sline)
        if car == look and i > 0:
            title = lines[i - 1]
            return title.strip("\n\r\t ")
    raise ValueError("Unable to find a title in '{0}'\nCONTENT\n{1}".format(
        filename, "".join(lines)))
