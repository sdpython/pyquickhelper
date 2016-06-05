# -*- coding: utf-8 -*-
"""
@file
@brief Functions to call from the notebook

.. versionadded:: 1.1
"""
from IPython.display import Javascript, HTML


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
        var command = "theNotebook = os.path.join(" + "r'"+attribs['data-project'].value+"'," +
                      "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);

    Example::

        from pyquickhelper.ipythonhelper import store_notebook_path
        store_notebook_path()

    In another cell::

        theNotebook

    See notebook :ref:`exempleoffixmenurst`.
    Try function @see fn set_notebook_name_theNotebook if this one does not work.

    .. versionadded:: 1.1
    """
    js = """
        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "{0} = os.path.join(" + "r'"+attribs['data-project'].value+"'," +
                      "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);
        """.replace("        ", "").format(name)
    return Javascript(js)


def set_notebook_name_theNotebook(name="theNotebook"):
    """
    This function must be called from the notebook
    you want to know the name. It relies on
    a javascript piece of code. It populates
    the variable ``theNotebook`` with the notebook name.

    @param      name        name of the variable to create

    This solution was found at
    `How to I get the current IPython Notebook name <http://stackoverflow.com/questions/12544056/how-to-i-get-the-current-ipython-notebook-name>`_.

    The function can be called in a cell.
    The variable ``theNotebook`` will be available in the next cells.

    Try function @see fn store_notebook_path if this one does not work.

    .. versionadded:: 1.1
    """
    code = """var kernel = IPython.notebook.kernel;
              var body = document.body, attribs = body.attributes;
              var command = "__NAME__ = " + "'"+attribs['data-notebook-name'].value+"'";
              kernel.execute(command);""".replace("              ", "").replace("__NAME__", name)

    def get_name():
        from IPython.core.display import Javascript, display
        display(Javascript(code))
    return get_name()


add_notebook_menu_js = """
                function repeat_indent_string(n){
                    var a = "" ;
                    for ( ; n > 0 ; --n) {
                        a += "    ";
                    }
                    return a;
                }
                var update_menu_string = function(begin, lfirst, llast, sformat, send) {
                    var anchors = document.getElementsByClassName("section");
                    if (anchors.length == 0) {
                        anchors = document.getElementsByClassName("text_cell_render rendered_html");
                    }
                    var i,t;
                    var text_menu = begin;
                    var text_memo = "<pre>\\nlength:" + anchors.length + "\\n";
                    var ind = "";
                    var memo_level = 1;
                    var href;
                    var tags = [];
                    for (i = 0; i <= llast; i++) {
                        tags.push("h" + i);
                    }

                    for (i = 0; i < anchors.length; i++) {
                        text_memo += "**" + anchors[i].id + "--\\n";

                        var child = null;
                        for(t = 0; t < tags.length; t++) {
                            var r = anchors[i].getElementsByTagName(tags[t]);
                            if (r.length > 0) {
                                child = r[0];
                                break;
                            }
                        }
                        if (child == null){
                            text_memo += "null\\n";
                            continue;
                        }

                        if (anchors[i].hasAttribute("id")) {
                            // when converted in RST
                            href = anchors[i].id;
                            text_memo += "#1-" + href;
                            // passer à child suivant (le chercher)
                        }
                        else if (child.hasAttribute("id")) {
                            // in a notebook
                            href = child.id;
                            text_memo += "#2-" + href;
                        }
                        else {
                            text_memo += "#3-" + "*" + "\\n";
                            continue;
                        }
                        var title = child.textContent;
                        var level = parseInt(child.tagName.substring(1,2));

                        text_memo += "--" + level + "?" + lfirst + "--" + title + "\\n";

                        if ((level < lfirst) || (level > llast)) {
                            continue ;
                        }
                        if (title.endsWith('¶')) {
                            title = title.substring(0,title.length-1).replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
                        }

                        if (title.length == 0) {
                            continue;
                        }
                        while (level > memo_level) {
                            text_menu += "<ul>\\n";
                            memo_level += 1;
                        }
                        while (level < memo_level) {
                            text_menu += "</ul>\\n";
                            memo_level -= 1;
                        }
                        text_menu += repeat_indent_string(level-2) + sformat.replace("__HREF__", href).replace("__TITLE__", title);
                    }
                    while (1 < memo_level) {
                        text_menu += "</ul>\\n";
                        memo_level -= 1;
                    }
                    text_menu += send;
                    //text_menu += "\\n" + text_memo;
                    return text_menu;
                };
                var update_menu = function() {
                    var sbegin = "__BEGIN__";
                    var sformat = __FORMAT__;
                    var send = "__END__";
                    var text_menu = update_menu_string(sbegin, __FIRST__, __LAST__, sformat, send);
                    var menu = document.getElementById("__MENUID__");
                    menu.innerHTML=text_menu;
                };
                window.setTimeout(update_menu,2000);
            """


def add_notebook_menu(menu_id="my_id_menu_nb", raw=False, format="html", header=None,
                      first_level=2, last_level=4):
    """
    add javascript and HTML to the notebook which gathers all in the notebook and builds a menu

    @param      menu_id         menu_id
    @param      raw             raw HTML and Javascript
    @param      format          *html* or *rst*
    @param      header          title of the menu (None for None)
    @param      first_level     first level to consider
    @param      last_level      last level to consider
    @return                     HTML object

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

    global add_notebook_menu_js
    js = add_notebook_menu_js.replace("                ", "") \
                             .replace("__MENUID__", menu_id) \
                             .replace("__FIRST__", str(first_level)) \
                             .replace("__LAST__", str(last_level))

    full = "{0}\n<script>{1}</script>".format(html, js)

    if format == "html":
        if header is not None and len(header) > 0:
            header = "<b>{0}</b>\n".format(header)
        else:
            header = ""
        full = header + \
            full.replace("__FORMAT__", """'<li><a href="#__HREF__">__TITLE__</a></li>'""") \
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


def load_extension(name):
    """
    install an extension, checks first it exists,
    if not displays an exception with the list of them

    @param      name        extension name
    """
    return Javascript("IPython.utils.load_extensions('%s')" % name)
