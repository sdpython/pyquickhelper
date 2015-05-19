# -*- coding: utf-8 -*-
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


def add_notebook_menu(menu_id="my_id_menu_nb", raw=False, format="html", header=None):
    """
    add javascript and HTML to the notebook which gathers all in the notebook and builds a menu

    @param      menu_id     menu_id
    @param      raw         raw HTML and Javascript
    @param      format      *html* or *rst*
    @param      header      title of the menu (None for None)
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

    js = """
                function repeat_indent_string(n){
                    var a = "" ;
                    for ( ; n > 0 ; --n) {
                        a += "    ";
                    }
                    return a;
                }
                var update_menu = function() {
                    var anchors = document.getElementsByClassName("section");
                    if (anchors.length == 0) {
                        anchors = document.getElementsByClassName("text_cell_render rendered_html");
                    }
                    var i;
                    var text_menu = "__BEGIN__";
                    var ind = "";
                    var memo_level = 0;
                    var href;
                    for (i = 0; i < anchors.length; i++) {
                        var child = anchors[i].children[0];
                        if (anchors[i].hasAttribute("id")) {
                            href = anchors[i].id;
                        }
                        else if (child.hasAttribute("id")) {
                            href = child.id;
                        }
                        else {
                            continue;
                        }
                        var title = child.textContent;
                        var level = parseInt(child.tagName.substring(1,2));
                        if ((level <= 1) || (level >= 5)) {
                            continue ;
                        }
                        if (title.endsWith('¶')) {
                            title = title.substring(0,title.length-1);
                        }
                        if (title.length == 0) {
                            continue;
                        }
                        if (level > memo_level) {
                            text_menu += "<ul>\\n";
                        }
                        text_menu += repeat_indent_string(level-2) + __FORMAT__;
                        if (level < memo_level) {
                            text_menu += "</ul>\\n";
                        }
                        memo_level = level;
                    }
                    text_menu += "__END__";
                    var menu = document.getElementById("__MENUID__");
                    menu.innerHTML=text_menu;
                };
                window.setTimeout(update_menu,2000);
            """.replace("                ", "") \
               .replace("__MENUID__", menu_id)

    full = "{0}\n<script>{1}</script>".format(html, js)

    if format == "html":
        if header is not None and len(header) > 0:
            header = "<b>{0}</b>\n".format(header)
        else:
            header = ""
        full = header + \
            full.replace("__FORMAT__", """'<li><a href="#' + href + '">' + title + '</a></li>'""") \
            .replace("__BEGIN__", "") \
            .replace("__END__", "")
    elif format == "rst":
        if header is not None and len(header) > 0:
            header = "{0}\n\n".format(header)
        else:
            header = ""
        full = header + \
            full.replace("__FORMAT__", """'* [' + title + '](#' + href + ')\\n'""") \
            .replace("<ul>", "") \
            .replace("</ul>", "") \
            .replace("__BEGIN__", "<pre>\\n") \
            .replace("__END__", "</pre>\\n")
    else:
        raise ValueError("format must be html or rst")

    if raw:
        return full
    else:
        return HTML(full)
