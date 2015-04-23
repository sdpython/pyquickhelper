# -*- coding: utf-8 -*-
"""
@file
@brief Quick and dirty trick to use `jsdifflib <https://github.com/cemerick/jsdifflib>`_
to visualize the differences between two files.
"""

import os
import warnings
import sys
import datetime
from ..filehelper.anyfhelper import read_content_ufs

if sys.version_info[0] == 2:
    from codecs import open
    FileNotFoundError = OSError

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

js_page = """
function diffUsingJS(viewType) {
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

body_page = """
<h1 class="top"><a href="http://github.com/cemerick/jsdifflib">jsdifflib</a> demo</h1>
<div class="top">
    <strong>Context size (optional):</strong> <input type="text" id="contextSize" value="" />
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


def create_visual_diff_through_html(string1, string2, notebook=False):
    """
    The function uses `jsdifflib <https://github.com/cemerick/jsdifflib>`_
    to create a visual diff.
    If it was not already done, the function downloads
    the tool using
    `pymyinstall <https://github.com/sdpython/pymyinstall>`_.

    @param      string1     first string (anything such as an url, a file, a string, a stream)
    @param      string2     second string (anything such as an url, a file, a string, a stream)
    @param      notebook    if True, the function assumes the outcome will be displayed from a notebook and does
                            things accordingly, see below
    @return                 html page or (`HTML <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?highlight=display#IPython.display.HTML>`_,
                            `Javascript <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?highlight=display#IPython.display.Javascript>`_) object if *notebook* is True

    @example(Visualize the difference between two text files or strings)
    @code
    with open("file1.txt","r",encoding="utf8") as f : text1 = f.read()
    with open("file2.txt","r",encoding="utf8") as f : text2 = f.read()
    pg = create_visual_diff_through_html(text1,text2)
    with open("page.html","w",encoding="utf8") as f : f.write(pg)
    import webbrowser
    webbrowser.open("page.html")
    @endcode
    @endexample

    .. versionchanged:: 1.1
        Parameter *notebook* was added.
        The function now uses @see fn read_content_ufs to retrieve the content.
    """
    string1 = read_content_ufs(string1)
    string2 = read_content_ufs(string2)

    fold = os.path.abspath(os.path.split(__file__)[0])
    if not os.path.exists(fold):
        raise FileNotFoundError("unable to find jsdifflib in: " + fold)
    global html_page, css_page, body_page, js_page

    def cleanh(s):
        return s.replace("&", "&amp;").replace(
            "<", "&lt;").replace(">", "&gt;")

    if notebook:
        rep_path = ""
    else:
        rep_path = fold + "/"

    if notebook:
        from IPython.core.display import HTML, Javascript
        from IPython.display import FileLink
        did = "diffid_" + \
            str(datetime.datetime.now()).replace(
                ":", "_").replace("/", "_").replace(".", "_")
        html = HTML(body_page.replace("__STRI" + "NG1__", cleanh(string1))
                             .replace("__STRI" + "NG2__", cleanh(string2))
                             .replace("__ID__", did))
        lib = [os.path.join(fold, "diffview.js"),
               os.path.join(fold, "difflib.js"), ]
        css = [os.path.join(fold, "diffview.css"), ],

        js = Javascript(data=js_page, lib=lib, css=css)
        return html, js
    else:

        page = html_page.replace("__PATH__", rep_path) \
                        .replace("__BODY__", body_page) \
                        .replace("__STRI" + "NG1__", cleanh(string1)) \
                        .replace("__STRI" + "NG2__", cleanh(string2)) \
                        .replace("__JS__", js_page) \
                        .replace("__CSS__", css_page) \
                        .replace("__ID__", "diffoutput")

        return page


def create_visual_diff_through_html_files(file1,
                                          file2,
                                          encoding="utf8",
                                          page=None,
                                          browser=False,
                                          notebook=False):
    """
    calls function @see fn create_visual_diff_through_html
    with the content of two files

    @param      string1     first string (anything such as an url, a file, a string, a stream)
    @param      string2     second string (anything such as an url, a file, a string, a stream)
    @param      page        if not None, saves the results in file
    @param      browser     open browser ?
    @param      notebook    if True, the function assumes the outcome will be displayed from a notebook and does
                            things accordingly
    @return                 html page or (`HTML <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?highlight=display#IPython.display.HTML>`_,
                            `Javascript <https://ipython.org/ipython-doc/stable/api/generated/IPython.display.html?highlight=display#IPython.display.Javascript>`_) object if *notebook* is True

    .. versionchanged:: 1.1
        Parameter *notebook* was added.
        The function now uses @see fn read_content_ufs to retrieve the content.
    """
    diff = create_visual_diff_through_html(file1, file2, notebook=notebook)
    if page is not None:
        with open(page, "w", encoding="utf8") as f:
            f.write(diff)
    if browser:
        if page is None:
            raise AttributeError("browser is True, page must be True")
        import webbrowser
        webbrowser.open(page)
    return diff
