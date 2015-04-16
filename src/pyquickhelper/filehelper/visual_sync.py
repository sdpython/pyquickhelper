# -*- coding: utf-8 -*-
"""
@file
@brief Quick and dirty trick to use `jsdifflib <https://github.com/cemerick/jsdifflib>`_
to visualize the differences between two files.
"""

import os
import warnings
import sys

if sys.version_info[0] == 2:
    from codecs import open
    FileNotFoundError = OSError


html_page = """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1">
        <title>jsdifflib demo</title>
        <link rel="stylesheet" type="text/css" href="__PATH__diffview.css"/>
        <script type="text/javascript" src="__PATH__diffview.js"></script>
        <script type="text/javascript" src="__PATH__difflib.js"></script>
    <style type="text/css">
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
    </style>

    <script type="text/javascript">

    function diffUsingJS(viewType) {
        "use strict";
        var byId = function (id) { return document.getElementById(id); },
            base = difflib.stringAsLines(byId("baseText").value),
            newtxt = difflib.stringAsLines(byId("newText").value),
            sm = new difflib.SequenceMatcher(base, newtxt),
            opcodes = sm.get_opcodes(),
            diffoutputdiv = byId("diffoutput"),
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

    </script>
    </head>
    <body>
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
            <input type="radio" name="_viewtype" id="sidebyside" onclick="diffUsingJS(0);" /> <label for="sidebyside">Side by Side Diff</label>
            &nbsp; &nbsp;
            <input type="radio" name="_viewtype" id="inline" onclick="diffUsingJS(1);" /> <label for="inline">Inline Diff</label>
        </div>
        <div id="diffoutput"> </div>
    </body>
    </html>
    """


def create_visual_diff_through_html(string1, string2):
    """
    The function uses `jsdifflib <https://github.com/cemerick/jsdifflib>`_
    to create a visual diff.
    If it was not already done, the function downloads
    the tool using
    `pymyinstall <https://github.com/sdpython/pymyinstall>`_.

    @param  string1         first string
    @param  string2         second string
    @return                 html page

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
    """
    try:
        from pymyinstall import ModuleInstall
        temp = os.path.join(
            os.path.abspath(os.path.split(__file__)[0]), "temp_difflibjs")
        ModuleInstall("jsdifflib", "github", gitrepo="cemerick",
                      fLOG=lambda *s: None).download(temp_folder=temp)
    except ImportError as e:
        warnings.warn("Unable to import jsdifflib, you should get it from: https://github.com/cemerick/jsdifflib\n"
                      "The page will be generated but might not work.\nEXC:\n{0}".format(e))

    fold = os.path.abspath(
        os.path.join(os.path.split(__file__)[0], "temp_difflibjs", "jsdifflib-master"))
    if not os.path.exists(fold):
        raise FileNotFoundError("unable to find jsdifflib in: " + fold)
    global html_page

    def cleanh(s):
        return s.replace("&", "&amp;").replace(
            "<", "&lt;").replace(">", "&gt;")

    page = html_page.replace("__PATH__", fold + "\\") \
                    .replace("__STRI" + "NG1__", cleanh(string1)) \
                    .replace("__STRI" + "NG2__", cleanh(string2))

    return page


def create_visual_diff_through_html_files(file1,
                                          file2,
                                          encoding="utf8",
                                          page=None,
                                          browser=False):
    """
    calls function @see fn create_visual_diff_through_html
    with the content of two files

    @param      file1       first file
    @param      file2       second file
    @param      page        if not None, saves the results in file
    @param      browser     open browser ?

    @return                 HTML page
    """
    with open(file1, "r", encoding=encoding) as f:
        cont1 = f.read()
    with open(file2, "r", encoding=encoding) as f:
        cont2 = f.read()
    diff = create_visual_diff_through_html(cont1, cont2)
    if page is not None:
        with open(page, "w", encoding="utf8") as f:
            f.write(diff)
    if browser:
        if page is None:
            raise AttributeError("browser is True, page must be True")
        import webbrowser
        webbrowser.open(page)
    return diff
