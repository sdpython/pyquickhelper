# -*- coding: utf-8 -*-
"""
@file
@brief Use `jsdifflib <https://github.com/cemerick/jsdifflib>`_
to visualize the differences between two files.
"""
import os
import datetime
from ..filehelper.anyfhelper import read_content_ufs


css_page = """
body {
    font-size: 12px;
    font-family: Sans-Serif;
}
h2 {
    margin: 0.5em 0 0.1em;
    text-align: center;
}
.top {
    text-align: center;
}
.textInput {
    display: block;
    width: 49%;
    float: left;
}
textarea {
    width:100%;
    height:300px;
}
label:hover {
    text-decoration: underline;
    cursor: pointer;
}
.spacer {
    margin-left: 10px;
}
.viewType {
    font-size: 16px;
    clear: both;
    text-align: center;
    padding: 1em;
}
#diffoutput {
    width: 100%;
}
"""

body_page = """
<h1 class="top"><a href="http://github.com/cemerick/jsdifflib">jsdifflib</a> demo</h1>
<div class="top">
    <strong>Context size (optional):</strong> <input type="text" id="contextSize" value="__CONTEXT_SIZE__" />
</div>
<div class="textInput">
    <h2>Base Text</h2>
    <textarea id="baseText">__STRING1__</textarea>
</div>
<div class="textInput spacer">
    <h2>New Text</h2>
    <textarea id="newText">__STRING2__</textarea>
</div>
<div class="viewType">
    <input type="radio" name="_viewtype" id="sidebyside" onclick="diffUsingJS(0);" />
    <label for="sidebyside">Side by Side Diff</label>
    &nbsp; &nbsp;
    <input type="radio" name="_viewtype" id="inline" onclick="diffUsingJS(1);" />
    <label for="inline">Inline Diff</label>
</div>
<div id="__ID__"> </div>
"""

html_page = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1" />
    <title>jsdifflib demo</title>
    <link rel="stylesheet" type="text/css" href="__PATH__diffview.css"/>
    <script type="text/javascript" src="__PATH__diffview.js"></script>
    <script type="text/javascript" src="__PATH__difflib.js"></script>
<style type="text/css">
__CSS__
</style>
<script type="text/javascript">
__JS__
</script>
</head>
<body>
__BODY__
</body>
</html>
"""

js_page = """
function diffUsingJS (viewType) {

    var byId = function (id) { return document.getElementById(id); },
        base = difflib.stringAsLines(byId("baseText").value),
        newtxt = difflib.stringAsLines(byId("newText").value),
        sm = new difflib.SequenceMatcher(base, newtxt),
        opcodes = sm.get_opcodes(),
        diffoutputdiv = byId("__ID__"),
        contextSize = byId("contextSize").value;

    diffoutputdiv.innerHTML = "";
    contextSize = contextSize || null;

    diffoutputdiv.appendChild(diffview.buildView({
        baseTextLines: base,
        newTextLines: newtxt,
        opcodes: opcodes,
        baseTextName: "Base Text",
        newTextName: "New Text",
        contextSize: contextSize,
        viewType: viewType
    }));
}
"""

js_page_nb = """
function diffUsingJS (viewType, contextSize, baseText, newText) {

    var byId = function (id) { return document.getElementById(id); },
        base = difflib.stringAsLines(baseText),
        newtxt = difflib.stringAsLines(newText),
        sm = new difflib.SequenceMatcher(base, newtxt),
        opcodes = sm.get_opcodes(),
        diffoutputdiv = byId("__ID__");

    diffoutputdiv.innerHTML = "";
    contextSize = contextSize || null;

    diffoutputdiv.appendChild(diffview.buildView({
        baseTextLines: base,
        newTextLines: newtxt,
        opcodes: opcodes,
        baseTextName: "Base Text",
        newTextName: "New Text",
        contextSize: contextSize,
        viewType: viewType
    }));
}
__INSERT_VARIABLES__
diffUsingJS(tview, csize, bt, nt) ;
"""


def create_visual_diff_through_html(string1, string2, notebook=False, context_size=None, inline_view=False):
    """
    The function uses `jsdifflib <https://github.com/cemerick/jsdifflib>`_
    to create a visual diff.
    If it was not already done, the function downloads
    the tool using
    `pymyinstall <https://github.com/sdpython/pymyinstall>`_.

    @param      string1         first string (anything such as an url, a file, a string, a stream)
    @param      string2         second string (anything such as an url, a file, a string, a stream)
    @param      notebook        if True, the function assumes the outcome will be displayed from a notebook and does
                                things accordingly, see below
    @param      context_size    to display everything (None) or just the changes > 0
    @param      inline_view     only for notebook, True: one column, False: two columns
    @return                     html page or (`HTML <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html
                                ?highlight=display#IPython.display.HTML>`_,
                                `Javascript <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html
                                ?highlight=display#IPython.display.Javascript>`_)
                                object if *notebook* is True

    .. exref::
        :title: Visualize the difference between two text files or strings

        ::

            with open("file1.txt","r",encoding="utf8") as f:
                text1 = f.read()
            with open("file2.txt","r",encoding="utf8") as f:
                text2 = f.read()
            pg = create_visual_diff_through_html(text1,text2)
            with open("page.html","w",encoding="utf8") as f:
                f.write(pg)
            import webbrowser
            webbrowser.open("page.html")

    The function uses @see fn read_content_ufs to retrieve the content.
    """
    string1 = read_content_ufs(string1)
    string2 = read_content_ufs(string2)

    fold = os.path.abspath(os.path.split(__file__)[0])
    if not os.path.exists(fold):
        raise FileNotFoundError("unable to find jsdifflib in: " + fold)

    def cleanh(s):
        return s.replace("&", "&amp;").replace(
            "<", "&lt;").replace(">", "&gt;")

    if notebook:
        rep_path = ""
    else:
        rep_path = fold + "/"

    if notebook:
        global js_page_nb
        from IPython.core.display import HTML, Javascript

        did = "diffid_" + \
            str(datetime.datetime.now()).replace(":", "_") \
                                        .replace("/", "_") \
                                        .replace(".", "_") \
                                        .replace(" ", "_")

        lib = [os.path.join(fold, "diffview.js"),
               os.path.join(fold, "difflib.js"), ]
        lib = [read_content_ufs(_) for _ in lib]

        css = os.path.join(fold, "diffview.css")
        css = read_content_ufs(css)

        html = HTML("""<style>__CSS__</style> <div id="__ID__"> populating... </div>"""
                    .replace("__ID__", did)
                    .replace("__CSS__", css))

        vars = ["var tview={0};".format(1 if inline_view else 0),
                "var csize='{0}';".format(
            "" if context_size is None else context_size),
            "var bt = '{0}';".format(
            string1.replace("\n", "\\n").replace("'", "\\'")),
            "var nt = '{0}';".format(string2.replace("\n", "\\n").replace("'", "\\'"))]
        vars = "\n".join(vars)

        data = js_page_nb.replace("__ID__", did) \
                         .replace("__INSERT_VARIABLES__", vars)

        data = "\n".join(lib + [data])

        js = Javascript(data=data, lib=[], css=[])
        return html, js

    else:
        global html_page, css_page, body_page, js_page
        page = html_page.replace("__PATH__", rep_path) \
                        .replace("__BODY__", body_page) \
                        .replace("__STRI" + "NG1__", cleanh(string1)) \
                        .replace("__STRI" + "NG2__", cleanh(string2)) \
                        .replace("__JS__", js_page) \
                        .replace("__CSS__", css_page) \
                        .replace("__CONTEXT_SIZE__", "" if context_size is None else str(context_size)) \
                        .replace("__ID__", "diffoutput")

        return page


def create_visual_diff_through_html_files(file1, file2, encoding="utf8", page=None,
                                          browser=False, notebook=False, context_size=None,
                                          inline_view=False):
    """
    Calls function @see fn create_visual_diff_through_html
    with the content of two files.

    :param file1: first file (anything such as an url, a file, a string, a stream)
    :param file2: second file (anything such as an url, a file, a string, a stream)
    :param encoding: encoding
    :param page: if not None, saves the results in file
    :param browser: open browser ?
    :param notebook: if True, the function assumes the outcome
        will be displayed from a notebook and does
        things accordingly
    :param context_size: to display everything (None) or just the changes > 0
    :param inline_view: only for notebook, True: one column, False: two columns
    :return: html page or (`HTML
        <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?
        highlight=display#IPython.display.HTML>`_,
        `Javascript <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?
        highlight=display#IPython.display.Javascript>`_)
        object if *notebook* is True

    An example of the results is shown in blog post :ref:`b-diffview`.
    The function now uses @see fn read_content_ufs to retrieve the content.

    .. cmdref::
        :title: Compares two files
        :cmd: -m pyquickhelper visual_diff --help

        The command calls function @see fn create_visual_diff_through_html_files
        and produces a :epkg:`HTML` page with shows the differences between two
        files. Example::

            python -m pyquickhelper visual_diff -f <file1> -fi <file2> --browser=1 --page=diff.html

        It works better with :epkg:`chrome`.
    """
    diff = create_visual_diff_through_html(file1, file2, notebook=notebook,
                                           context_size=context_size, inline_view=inline_view)
    if page is not None:
        with open(page, "w", encoding="utf8") as f:
            f.write(diff)
    if browser:
        if page is None:
            raise AttributeError("browser is True, page must be True")
        import webbrowser
        webbrowser.open(page)
        return None
    return diff
