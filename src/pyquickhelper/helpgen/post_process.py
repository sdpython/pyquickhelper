# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""
import os
import re
import warnings

from ..loghelper.flog import fLOG
from .utils_sphinx_doc_helpers import HelpGenException


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


def post_process_rst_output(file, html, pdf, python):
    """
    process a RST file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
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

    with open(file, "w", encoding="utf8") as f:
        f.write("".join(lines))


def post_process_html_output(file, pdf, python):
    """
    process a HTML file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      python      if True, add a link to the Python conversion

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.

    """
    fold, name = os.path.split(file)
    noext = os.path.splitext(name)[0]
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    with open(file, "r", encoding="utf8") as f:
        text = f.read()

    link = '''
            <div style="position:fixed;text-align:center;align:right;width:15%;bottom:50px;right:20px;background:#DDDDDD;">
            <p>
            {0}
            </p>
            </div>
            '''

    links = [
        '<b>links</b><br /><a href="{0}.ipynb">notebook</a>'.format(noext)]
    if pdf:
        links.append('<a href="{0}.pdf">PDF</a>'.format(noext))
    if python:
        links.append('<a href="{0}.py">python</a>'.format(noext))
    link = link.format("\n<br />".join(links))

    text = text.replace("</body>", link + "\n</body>")
    text = text.replace("<title>[]</title>", "<title>%s</title>" % name)
    if "<h1>" not in text and "<h1 id" not in text:
        text = text.replace("<body>", "<body><h1>%s</h1>" % name)

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

    ..versionchanged:: 0.9
        add parameter *info*, add tableofcontent in the document

    @todo Check latex is properly converted in HTML files
    """
    fLOG("   ** enter post_process_latex", doall, "%post_process_latex" in st)

    # we count the number of times we have \$ (which is unexpected unless the
    # currency is used.
    dollar = st.split("\\$")
    if len(dollar) > 0 and (
            info is None or os.path.splitext(info)[-1] != ".html"):
        # probably an issue, for the time being, we are strict, no dollar as a currency in latex
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
            #raise HelpGenException("\n".join(messages))

        if found == 0:
            raise NotImplementedError(
                "unexpected issue with \\$ in file: {0}".format(info))

    st = st.replace("<br />", "\\\\")
    st = st.replace("»", '"')

    if not doall:
        st = st.replace(
            "\\maketitle", "\\maketitle\n\n\\newchapter{Introduction}")

    st = st.replace("%5C", "/").replace("%3A",
                                        ":").replace("\\includegraphics{notebooks\\", "\\includegraphics{")
    st = st.replace(
        r"\begin{document}", r"\setlength{\parindent}{0cm}%s\begin {document}" % "\n")
    st = st.replace(r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\}}",
                    r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\},fontsize=\small}")
    st = st.replace("\\textquotesingle{}", "'")

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
    if r"\usepackage{multirow}" in st:
        st = st.replace(
            r"\usepackage{multirow}", r"\usepackage{multirow}\usepackage{amssymb}\usepackage{latexsym}\usepackage{amsfonts}\usepackage{ulem}\usepackage{textcomp}")
    elif r"\usepackage{hyperref}" in st:
        st = st.replace(
            r"\usepackage{hyperref}", r"\usepackage{hyperref}\usepackage{amssymb}\usepackage{latexsym}\usepackage{amsfonts}\usepackage{ulem}\usepackage{textcomp}")
    else:
        raise HelpGenException(
            "unable to add new instructions usepackage in file {0}".format(info))

    if r"\usepackage[utf8]" in st:
        st = st.replace(
            r"\usepackage[utf8]{inputenc}", r"\usepackage{ucs}\usepackage[utf8x]{inputenc}")
        st = st.replace(
            r"\DeclareUnicodeCharacter{00A0}{\nobreakspace}", r"%\DeclareUnicodeCharacter{00A0}{\nobreakspace}")

    # add tableofcontents
    lines = st.split("\n")
    for i, line in enumerate(lines):
        if "\\section" in line and "{" in line and "}" in line:
            # shoud be cleaner with regular expressions
            line = line + \
                "\n\n\\tableofcontents\n\n\\noindent\\rule{4cm}{0.4pt}\n\n"
            lines[i] = line
    st = "\n".join(lines)

    return st
