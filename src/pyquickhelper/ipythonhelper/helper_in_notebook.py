"""
@file
@brief Functions to call from the notebook

.. versionadded:: 1.1
"""

from IPython.display import Javascript, HTML, display_html


def store_notebook_path(name="theNotebook"):
    """
    return Javascript object to execute in order to store
    the notebook file name into a variable
    available from the notebook

    @param      name        name of the variable
    @return                 Javascript object

    The function uses the following code to get the notebook path::

        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "theNotebook = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);

    Example::

        from pyquickhelper.ipythonhelper import store_notebook_path
        store_notebook_path()

    In another cell::

        theNotebook

    See notebook :ref:`exempleoffixmenurst`.
    Same function as @see fn set_notebook_name_theNotebook.

    .. versionadded:: 1.1
    """
    js = """
        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "{0} = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);
        """.replace("        ", "").format(name)
    return Javascript(js)


def set_notebook_name_theNotebook():
    """
    This function must be called from the notebook
    you want to know the name. It relies on
    a javascript piece of code. It populates
    the variable ``theNotebook`` with the notebook name.

    This solution was found at
    `How to I get the current IPython Notebook name <http://stackoverflow.com/questions/12544056/how-to-i-get-the-current-ipython-notebook-name>`_.

    The function can be called in a cell.
    The variable ``theNotebook`` will be available in the next cells.

    Same function as @see fn store_notebook_path.

    .. versionadded:: 1.1
    """
    code = """var kernel = IPython.notebook.kernel;
              var body = document.body, attribs = body.attributes;
              var command = "theNotebook = " + "'"+attribs['data-notebook-name'].value+"'";
              kernel.execute(command);""".replace("              ", "")

    def get_name():
        from IPython.core.display import Javascript, display
        display(Javascript(code))
    return get_name()


def add_notebook_menu(menu_id="my_id_menu_nb", raw=False, format="html", level="h3"):
    """
    add javascript and HTML to the notebook which gathers all in the notebook and builds a menu

    @param      menu_id     menu_id
    @param      raw         raw HTML and Javascript
    @param      format      *html* or *rst*
    @param      level       tag to look for
    @return                 HTML object

    In a notebook, it is easier to do by using a magic command
    ``%%html`` for the HTML and another one
    ``%%javascript`` for the Javascript.
    This function returns a full text with HTML and
    Javascript.

    If the format is RST, the menu can be copied/pasted in a text cell.

    On the notebook, the instruction would work::

        var anchors = document.getElementsByClassName("anchor-link");

    But it fails during the conversion from a notebook to format RST.
    """
    html = '<div id="{0}">run previous cell, wait for 2 seconds</div>'.format(
        menu_id)

    rst_level = "h" + str(int(level.strip("h")) - 1)

    js = """
        var update_menu = function() {
            var els = document.getElementsByClassName("sphinxsidebar");
            var level;
            if (els.length > 0) level = "__RSTLEVEL__";
            else level = "__LEVEL__";
            var anchors = document.getElementsByTagName(level);
            var menu = document.getElementById("__MENUID__");
            var i;
            var text_menu = "<ul>";
            var href;
            for (i = 0; i < anchors.length; i++) {
                var title = anchors[i].textContent;
                title = title.substring(0,title.length-1);
                if (anchors[i].hasAttribute("id"))
                    href = anchors[i].id;
                else
                    href = anchors[i].parentNode.id;
                text_menu += __FORMAT__;
            }
            text_menu += "</ul>"
            menu.innerHTML=text_menu;
        };
        window.setTimeout(update_menu,2000);
        """.replace("        ", "") \
           .replace("__MENUID__", menu_id) \
           .replace("__LEVEL__", level) \
           .replace("__RSTLEVEL__", rst_level)

    full = "{0}\n<script>{1}</script>".format(html, js)

    if format == "html":
        full = full.replace("__FORMAT__",
                            """'<li><a href="#' + href + '">' + title + '</a></li>'""")
    elif format == "rst":
        full = full.replace("__FORMAT__",
                            """'* [' + title + '](#' + href + ')\\n'""") \
            .replace("<ul>", "<pre>") \
            .replace("</ul>", "</pre>")
    else:
        raise ValueError("format must be html or rst")

    if raw:
        return full
    else:
        return HTML(full)
