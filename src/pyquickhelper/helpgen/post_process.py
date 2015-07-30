# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""
import os
import re
import warnings
import sys

from ..loghelper.flog import fLOG
from .utils_sphinx_doc_helpers import HelpGenException

if sys.version_info[0] == 2:
    from codecs import open

template_examples = """

List of programs
++++++++++++++++

.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst

Another list
++++++++++++

"""


def post_process_latex_output(root, doall):
    """
    post process the latex file produced by sphinx

    @param      root        root path or latex file to process
    @param      doall       do all transformations
    """
    if os.path.isfile(root):
        file = root
        with open(file, "r", encoding="utf8") as f:
            content = f.read()
        content = post_process_latex(content, doall)
        with open(file, "w", encoding="utf8") as f:
            f.write(content)
    else:
        build = os.path.join(root, "_doc", "sphinxdoc", "build", "latex")
        if not os.path.exists(build):
            raise FileNotFoundError(build)
        for tex in os.listdir(build):
            if tex.endswith(".tex"):
                file = os.path.join(build, tex)
                fLOG("modify file", file)
                with open(file, "r", encoding="utf8") as f:
                    content = f.read()
                content = post_process_latex(content, doall, info=file)
                with open(file, "w", encoding="utf8") as f:
                    f.write(content)


def post_process_latex_output_any(file):
    """
    post process the latex file produced by sphinx

    @param      file        latex filename
    """
    fLOG("   ** post_process_latex_output_any ", file)
    with open(file, "r", encoding="utf8") as f:
        content = f.read()
    content = post_process_latex(content, True, info=file)
    with open(file, "w", encoding="utf8") as f:
        f.write(content)


def post_process_rst_output(file, html, pdf, python, slides, is_notebook=False):
    """
    process a RST file generated from the conversion of a notebook

    @param      file            filename
    @param      pdf             if True, add a link to the PDF, assuming it will exists at the same location
    @param      html            if True, add a link to the HTML conversion
    @param      python          if True, add a link to the Python conversion
    @param      slides          if True, add a link to the slides conversion
    @param      is_notebook     does something more if the file is a notebook

    .. versionchanged:: 1.1
        Parameters *slides*, *is_notebook* were added.
    """
    fLOG("    post_process_rst_output", file)

    fold, name = os.path.split(file)
    noext = os.path.splitext(name)[0]
    with open(file, "r", encoding="utf8") as f:
        lines = f.readlines()

    # remove empty lines in inserted code, also add line number
    def startss(line):
        for b in ["::", ".. parsed-literal::", ".. code:: python",
                  ".. code-block:: python"]:
            if line.startswith(b):
                return b
        return None

    codeb = [".. code:: python", ".. code-block:: python"]
    inbloc = False
    for pos, line in enumerate(lines):
        if not inbloc:
            b = startss(line)
            if b is None:
                pass
            else:
                if b in codeb:
                    # we remove line number for the notebooks
                    if "notebook" not in file:
                        lines[pos] = "{0}\n    :linenos:\n\n".format(codeb[-1])
                    else:
                        lines[pos] = "{0}\n\n".format(codeb[-1])
                inbloc = True
                memopos = pos
        else:
            if len(line.strip(" \r\n")) == 0 and pos < len(lines) - 1 and \
                    lines[pos + 1].startswith(" ") and len(lines[pos + 1].strip(" \r\n")) > 0:
                lines[pos] = ""

            elif not line.startswith(" ") and line != "\n":
                inbloc = False

                if lines[memopos].startswith("::"):
                    code = "".join(
                        (_[4:] if _.startswith("    ") else _) for _ in lines[memopos + 1:pos])
                    if len(code) == 0:
                        fLOG("EMPTY-SECTION in ", file)
                    else:
                        try:
                            cmp = compile(code, "", "exec")
                            if cmp is not None:
                                lines[memopos] = "{0}\n    :linenos:\n".format(
                                    ".. code-block:: python")
                        except Exception:
                            pass

                memopos = None

    # code and images
    imgreg = re.compile("[.][.] image:: (.*)")
    for pos in range(0, len(lines)):
        # lines[pos] = lines[pos].replace(".. code:: python","::")
        if lines[pos].strip().startswith(".. image::"):
            # we assume every image should be placed in the same folder as the
            # notebook itself
            img = imgreg.findall(lines[pos])
            if len(img) == 0:
                raise HelpGenException(
                    "unable to extract image name in " + lines[pos])
            nameimg = img[0]
            short = nameimg.replace("%5C", "/")
            short = os.path.split(short)[-1]
            lines[pos] = lines[pos].replace(nameimg, short)

    # title
    pos = 0
    for pos, line in enumerate(lines):
        line = line.strip("\n\r")
        if len(line) > 0 and line == "=" * len(line):
            lines[pos] = lines[pos].replace("=", "*")
            pos2 = pos - 1
            l = len(lines[pos])
            while len(lines[pos2]) != l:
                pos2 -= 1
            sep = "" if lines[pos2].endswith("\n") else "\n"
            lines[pos2] = "{0}{2}{1}".format(lines[pos], lines[pos2], sep)
            for p in range(pos2 + 1, pos):
                if lines[p] == "\n":
                    lines[p] = ""
            break

    pos += 1
    if pos >= len(lines):
        raise HelpGenException("unable to find a title")

    # label
    labelname = name.replace(" ", "").replace("_", "").replace(
        ":", "").replace(".", "").replace(",", "")
    label = "\n.. _{0}:\n\n".format(labelname)
    lines.insert(0, label)

    # links
    links = ['**Links:** :download:`notebook <{0}.ipynb>`'.format(noext)]
    if html:
        links.append(':download:`html <{0}.html>`'.format(noext))
    if pdf:
        links.append(':download:`PDF <{0}.pdf>`'.format(noext))
    if python:
        links.append(':download:`python <{0}.py>`'.format(noext))
    if slides:
        links.append(':download:`slides <{0}.slides.html>`'.format(noext))
    lines[pos] = "{0}\n\n{1}\n\n".format(lines[pos], ", ".join(links))

    # we remove the
    # <div
    # style="position:absolute;
    # ....
    # </div>
    reg = re.compile(
        "([.]{2} raw[:]{2} html[\\n ]+<div[\\n ]+style=.?position:absolute;(.|\\n)*?[.]{2} raw[:]{2} html[\\n ]+</div>)")
    merged = "".join(lines)
    r = reg.findall(merged)
    if len(r) > 0:
        fLOG("    *** remove div absolute in ", file)
        for spa in r:
            rep = spa[0]
            nbl = len(rep.split("\n"))
            merged = merged.replace(rep, "\n" * nbl)
        lines = [(_ + "\n") for _ in merged.split("\n")]

    # bullets
    for pos, line in enumerate(lines):
        if pos == 0:
            continue
        if len(line) > 0 and (line.startswith("- ") or line.startswith("* ")) \
                and pos < len(lines):
            next = lines[pos + 1]
            prev = lines[pos - 1]
            if (next.startswith("- ") or next.startswith("* ")) \
               and not (prev.startswith("- ") or prev.startswith("* ")) \
               and not prev.startswith("  "):
                lines[pos - 1] += "\n"
            elif line.startswith("-  ") and next.startswith("   ") \
                    and not prev.startswith("   ") and not prev.startswith("-  "):
                lines[pos - 1] += "\n"
            elif line.startswith("- "):
                pass

    # remove last ::
    i = len(lines)
    for i in range(len(lines) - 1, 0, -1):
        s = lines[i - 1].strip(" \n\r")
        if len(s) != 0 and s != "::":
            break

    if i < len(lines):
        del lines[i:]

    # specific treatement for notebooks
    if is_notebook:
        # change links <#Alink --> <#alink
        reg = re.compile("(<#[A-Z][a-zA-Z0-9_+-]+>)")
        for i, line in enumerate(lines):
            r = reg.search(line)
            if r:
                memo = r.groups()[0]
                new_memo = "<#" + memo[2].lower() + memo[3:]
                new_memo = new_memo.replace("+", "")
                line = line.replace(memo, new_memo)
                lines[i] = line

    with open(file, "w", encoding="utf8") as f:
        f.write("".join(lines))


def post_process_html_output(file, pdf, python, slides):
    """
    process a HTML file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      python      if True, add a link to the Python conversion
    @param      slides      if True, add a link to the slides conversion

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.

    .. versionchanged:: 1.1
        Parameters *slides* was added.
    """
    fold, name = os.path.split(file)
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    with open(file, "r", encoding="utf8") as f:
        text = f.read()

    # mathjax
    text = text.replace("https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML",
                        "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML")

    with open(file, "w", encoding="utf8") as f:
        f.write(text)


def post_process_slides_output(file, pdf, python, slides):
    """
    process a HTML file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      python      if True, add a link to the Python conversion
    @param      slides      if True, add a link to the slides conversion

    .. versionadded:: 1.1
    """
    fold, name = os.path.split(file)
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    with open(file, "r", encoding="utf8") as f:
        text = f.read()

    # reveal.js
    text = text.replace("reveal.js/js/reveal.js", "reveal.js/js/reveal.js")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if '<script src="reveal.js/lib/js/head.min.js"></script>' in line:
            lines[
                i] = '<script src="reveal.js/js/jquery.min.js"></script>\n' + lines[i]
        if '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>' in line:
            lines[i] = ""
        if '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"></script>' in line:
            lines[i] = ""
    text = "\n".join(lines)

    """
        <link rel="stylesheet" href="reveal.js/css/reveal.css">
        <link rel="stylesheet" href="reveal.js/css/theme/solarized.css" id="theme">
        <link rel="stylesheet" href="reveal.js/lib/css/zenburn.css">
        <link rel="stylesheet" href="reveal.js/revealjs.css" type="text/css" />

        <link rel="stylesheet" href="reveal.js/css/reveal.css">
        <link rel="stylesheet" href="reveal.js/css/theme/simple.css" id="theme">

        width: 1076,
        height: 750,

        margin: 0.1,

        minScale: 0.2,
        maxScale: 1.0,

        controls: true,
        progress: true,
        history: false,
        center: true,

        keyboard : true,
        overview: true,
        touch: true,
        loop: false,
        rtl: false,
        fragments: true,

        autoSlide: 0,
        mouseWheel: true,
        rollingLinks: true,
        previewLinks: true,

        transitionSpeed: "default",
        backgroundTransition: "default",

        slideNumber: true,
        embedded: false,
        autoSlideStoppable: true,
        hideAddressBar: true,

        parallaxBackgroundImage: "",
        parallaxBackgroundSize: "",

        focusBodyOnPageVisiblityChange: true,

        viewDistance: 3,

        transition: Reveal.getQueryHash().transition || "linear",

        // Optional libraries used to extend on reveal.js
        dependencies: [
           { src: '_static/lib/js/classList.js', condition: function() { return !document.body.classList; } },
           { src: '_static/plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
           { src: '_static/plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
           { src: '_static/plugin/highlight/highlight.js', async: true, callback: function() { hljs.initHighlightingOnLoad(); } },
           { src: '_static/plugin/zoom-js/zoom.js', async: true, condition: function() { return !!document.body.classList; } },
           { src: '_static/plugin/leap/leap.js', async: true, condition: function() { return !!document.body.classList; } },
           { src: '_static/plugin/multiplex/master.js', async: true, condition: function() { return !!document.body.classList; } },
           { src: '_static/plugin/remotes/remotes.js_static/plugin/notes-server/client.js', async: true, condition: function() { return !!document.body.classList; } },
           { src: '_static/plugin/math/math.js', async: true, condition: function() { return !!document.body.classList; } },
           { src: '_static/plugin/notes/notes.js', async: true, condition: function() { return !!document.body.classList; } }

    """

    # mathjax
    text = text.replace("https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML",
                        "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML")

    with open(file, "w", encoding="utf8") as f:
        f.write(text)


def post_process_latex(st, doall, info=None):
    """
    modifies a latex file after its generation by sphinx

    @param      st      string
    @param      doall   do all transformations
    @param      info    for more understandable error messages
    @return             string

    SVG included in a notebook (or in RST file) requires `Inkscape <https://inkscape.org/>`_
    to be converted into Latex.

    .. versionchanged:: 0.9
        add parameter *info*, add tableofcontent in the document

    .. versionchanged:: 1.2
        remove ascii character in *[0..31]* in each line, replace them by space.

    @todo Check latex is properly converted in HTML files
    """
    fLOG("   ** enter post_process_latex", doall, "%post_process_latex" in st)

    # we count the number of times we have \$ (which is unexpected unless the
    # currency is used.
    dollar = st.split("\\$")
    if len(dollar) > 0 and (
            info is None or os.path.splitext(info)[-1] != ".html"):
        # probably an issue, for the time being, we are strict,
        # no dollar as a currency in latex
        # we do not check HTML files, for the time being, the formulas appears
        # in pseudo latex
        exp = re.compile(r"(.{3}[\\]\$)")
        found = 0
        records = []
        for m in exp.finditer(st):
            found += 1
            p1, p2 = m.start(), m.end()
            sub = st[p1:p2].strip(" \r\n")
            sub2 = st[max(p1 - 10, 0):min(len(st), p2 + 10)]
            # very quick and dirty
            if sub not in [".*)\\$", "r`\\$}", "ar`\\$", "tt{\\$"] and \
               not sub.endswith("'\\$") and not sub.endswith("{\\$"):
                if p1 > 30:
                    temp = st[p1 - 25:p2]
                else:
                    temp = st[0:p2]
                records.append((info, p1, p2, sub, sub2, temp))

        if len(records) > 0:
            messages = [str(i) + ":" + ("unexpected \\$ in a latex file:\n    {0}\n    at position: {1},{2}\n" +
                                        "    substring: {3}\n    around: {4}\n    temp=[{5}]").format(*rec)
                        for i, rec in enumerate(records)]
            for mes in messages:
                warnings.warn(mes)

    st = st.replace("<br />", "\\\\")
    st = st.replace("»", '"')

    if not doall:
        st = st.replace(
            "\\maketitle", "\\maketitle\n\n\\newchapter{Introduction}")

    st = st.replace("%5C", "/") \
           .replace("%3A", ":") \
           .replace("\\includegraphics{notebooks\\", "\\includegraphics{")
    st = st.replace(
        r"\begin{document}", r"\setlength{\parindent}{0cm}%s\begin {document}" % "\n")
    st = st.replace(r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\}}",
                    r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\},fontsize=\small}")
    st = st.replace("\\textquotesingle{}", "'")
    st = st.replace("\u0001", "\\u1")

    # hyperref
    if doall and "%post_process_latex" not in st:
        st = "%post_process_latex\n" + st
        reg = re.compile("hyperref[[]([a-zA-Z0-9]+)[]][{](.*?)[}]")
        allhyp = reg.findall(st)
        sections = []
        for id, section in allhyp:
            sec = r"\subsection{%s} \label{%s}" % (section, id)
            sections.append((id, section, sec))
    elif not doall:
        sections = []
        # first section
        lines = st.split("\n")
        for i, line in enumerate(lines):
            if "\\section" in line:
                lines[i] = "\\newchapter{Documentation}\n" + lines[i]
                break
        st = "\n".join(lines)
    else:
        sections = []

    if len(sections) > 0:
        lines = st.split("\n")
        for i, line in enumerate(lines):
            for _, section, sec in sections:
                if line.strip("\r\n ") == section:
                    fLOG("   **", section, " --> ", sec)
                    lines[i] = sec
        st = "\n".join(lines)

    st = st.replace("\\chapter", "\\section")
    st = st.replace("\\newchapter", "\\chapter")
    if "\\usepackage{multirow}" in st:
        st = st.replace(
            "\\usepackage{svg}\\usepackage{multirow}", "\\usepackage{multirow}\\usepackage{amssymb}\\usepackage{latexsym}\\usepackage{amsfonts}\\usepackage{ulem}\\usepackage{textcomp}")
    elif "\\usepackage{hyperref}" in st:
        st = st.replace(
            "\\usepackage{svg}\\usepackage{hyperref}", "\\usepackage{hyperref}\\usepackage{amssymb}\\usepackage{latexsym}\\usepackage{amsfonts}\\usepackage{ulem}\\usepackage{textcomp}")
    else:
        raise HelpGenException(
            "unable to add new instructions usepackage in file {0}".format(info))

    if "\\usepackage[utf8]" in st:
        st = st.replace(
            "\\usepackage[utf8]{inputenc}", "\\usepackage{silence}\\usepackage{ucs}\\usepackage[utf8x]{inputenc}")
        st = st.replace(
            "\\DeclareUnicodeCharacter{00A0}{\\nobreakspace}", "%\\DeclareUnicodeCharacter{00A0}{\\nobreakspace}")

    # SVG does not work unless it is converted (nbconvert should handle that
    # case)
    reg = re.compile("([\\\\]includegraphics[{].*?[.]svg[}])")
    fall = reg.findall(st)
    for found in fall:
        st = st.replace(found, "%" + found)

    # end
    return st


def remove_character_under32(s):
    """
    remove ascii characters in *[0..31]*

    @param      s       string to process
    @return             filtered string

    .. versionadded:: 1.2
    """
    l = ""
    for c in s:
        d = ord(c)
        if 0 <= d < 32:
            l += " "
        else:
            l += c
    return l
