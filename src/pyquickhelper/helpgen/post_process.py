# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.
"""
import os
import re
import warnings
import glob
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


def update_notebook_link(text, format, nblinks, fLOG):
    """
    A notebook can contain a link ``[anchor](find://...)``
    and it will be converted into: ``:ref:...`` in rst format.

    @param      text        text to look into
    @param      format      format
    @param      nblinks     list of mappings *(reference: url)*
    @param      fLOG        logging function
    @return                 modified text
    """
    def get_url_from_nblinks(nblinks, url, format):
        if isinstance(nblinks, dict):
            if (url, format) in nblinks:
                url = nblinks[url, format]
            elif url in nblinks:
                url = nblinks[url]
            if url.startswith("find://"):
                short = url[7:]
                if (short, format) in nblinks:
                    url = nblinks[short, format]
                elif short in nblinks:
                    url = nblinks[short]
        else:
            url = nblinks(url, format)
        if url.startswith("find://"):
            if format == 'python':
                url = url[7:]
            else:
                snb = "\n".join("'{0}': '{1}'".format(k, v)
                                for k, v in sorted(nblinks.items()))
                extension = "You shoud add links into variable 'nblinks' " \
                            "into documentation configuration file."
                extension += "\nnblinks={0}".format(nblinks)
                raise HelpGenException(
                    "Unable to find a replacement for '{0}' format='{1}' in \n{2}\n{3}".format(
                        url, format, snb, extension))
        return url

    if nblinks is None:
        nblinks = {}
    if format == "rst":
        def reprst(le):
            anc, url = le.groups()
            url = get_url_from_nblinks(nblinks, url, format)
            if "://" in url:
                new_url = "`{0} <{1}>`_".format(anc, url)
            else:
                new_url = ":ref:`{0} <{1}>`".format(anc, url)
            if fLOG:
                fLOG("      [update_notebook_link]1 add in ",
                     format, ":", new_url)
            return new_url
        reg = re.compile("`([^`]+?) <find://([^`<>]+?)>`_")
        new_text = reg.sub(reprst, text)
    elif format in ("html", "slides", "slides2"):
        def rephtml(le):
            anc, url = le.groups()
            url = get_url_from_nblinks(nblinks, url, format)
            new_url = "<a href=\"{0}.html\">{1}</a>".format(anc, url)
            if fLOG:
                fLOG("      [update_notebook_link]2 add in ",
                     format, ":", new_url)
            return new_url
        reg = re.compile("<a href=\\\"find://([^\\\"]+?)\\\">([^`<>]+?)</a>")
        new_text = reg.sub(rephtml, text)
    elif format in ("ipynb", "python"):
        def repipy(le):
            anc, url = le.groups()
            url = get_url_from_nblinks(nblinks, "find://" + url, format)
            if not url.startswith("http"):
                mes = "\n".join("{0}: '{1}'".format(k, v)
                                for k, v in sorted(nblinks.items()))
                extension = "You should add this link into the documentation " \
                            "configuration file in variable 'nblinks'."
                raise HelpGenException(
                    "A reference was not found: '{0}' - '{1}' "
                    "format={2}, nblinks=\n{3}\n{4}".format(
                        anc, url, format, mes, extension))
            new_url = "[{0}]({1})".format(anc, url)
            if fLOG:
                fLOG("      [update_notebook_link]3 add in ",
                     format, ":", new_url)
            return new_url
        reg = re.compile("[\\[]([^[]+?)[\\]][(]find://([^ ]+)[)]")
        new_text = reg.sub(repipy, text)
    elif format in ("latex", "elatex"):
        def replat(le):
            url, anc = le.groups()
            url = get_url_from_nblinks(nblinks, url, format)
            if not url.endswith(".html") and not url.endswith(".js") and not url.endswith(".css"):
                url += ".html"
            new_url = "\\href{{{0}}}{{{1}}}".format(url, anc)
            if fLOG:
                fLOG("      [update_notebook_link]4 add in ",
                     format, ":", new_url)
            return new_url
        reg = re.compile("\\\\href{find://([^{} ]+?)}{([^{}]+)}")
        new_text = reg.sub(replat, text)
        # {\hyperref[\detokenize{c_classes/classes:chap-classe}]
        # {\sphinxcrossref{\DUrole{std,std-ref}{Classes}}}}
    else:
        raise NotImplementedError(  # pragma: no cover
            "Unsupported format '{0}'\n{1}".format(format, text))
    return new_text


def _notebook_replacements(nbtext, notebook_replacements, fLOG=None):
    """
    Makes some replacements in a notebook.

    @param      nbtext                  text to process
    @param      notebook_replacements   dictionary of replacements
    @param      fLOG                    logging function
    @return                             text
    """
    if notebook_replacements is None:
        return nbtext
    for k, v in notebook_replacements:
        if k in nbtext:
            fLOG(
                "[_notebook_replacements] replace '{0}' -> '{1}'".format(k, v))
            nbtext = nbtext.replace(k, v)
    if '"nbformat": 4,' in nbtext:
        rep = ['"nbformat_minor": 0', '"nbformat_minor": 1',
               '"nbformat_minor": 2']
        for r in rep:
            if r in nbtext:
                nbtext = nbtext.replace(r, '"nbformat_minor": 4')
    return nbtext


def post_process_latex_output(root, doall, latex_book=False, exc=True,
                              custom_latex_processing=None, nblinks=None,
                              remove_unicode=True, fLOG=None, notebook_replacements=None):
    """
    Postprocesses the latex file produced by :epkg:`sphinx`.

    @param      root                        root path or latex file to process
    @param      doall                       do all transformations
    @param      latex_book                  customized for a book
    @param      exc                         raises an exception or a warning
    @param      custom_latex_processing     function which does some post processing of the full latex file
    @param      nblinks                     dictionary ``{ ref : url }`` where to look for references
    @param      remove_unicode              remove unicode characters (fails with latex)
    @param      notebook_replacements       string replacement in notebooks
    @param      fLOG                        logging function
    """
    if os.path.isfile(root):
        file = root
        with open(file, "r", encoding="utf8") as f:
            content = f.read()
        with open(file + ".tex1~", "w", encoding="utf8") as f:
            f.write(content)
        content = post_process_latex(
            content, doall, latex_book=latex_book, exc=exc,
            custom_latex_processing=custom_latex_processing, nblinks=nblinks,
            file=file, remove_unicode=remove_unicode, fLOG=fLOG,
            notebook_replacements=notebook_replacements)
        with open(file, "w", encoding="utf8") as f:
            f.write(content)
    else:
        build = os.path.join(root, "_doc", "sphinxdoc", "build", "latex")
        if not os.path.exists(build):
            raise FileNotFoundError(build)
        for tex in os.listdir(build):
            if tex.endswith(".tex"):
                file = os.path.join(build, tex)
                fLOG("[post_process_latex_output] modify file", file)
                with open(file, "r", encoding="utf8") as f:
                    content = f.read()
                with open(file + ".tex2~", "w", encoding="utf8") as f:
                    f.write(content)
                content = post_process_latex(
                    content, doall, info=file, latex_book=latex_book, exc=exc,
                    custom_latex_processing=custom_latex_processing, nblinks=nblinks,
                    file=file, remove_unicode=remove_unicode, fLOG=fLOG,
                    notebook_replacements=notebook_replacements)
                with open(file, "w", encoding="utf8") as f:
                    f.write(content)


def post_process_python_output(root, doall, exc=True, nblinks=None, fLOG=None, notebook_replacements=None):
    """
    Postprocesses the python file produced by :epkg:`sphinx`.

    @param      root                    root path or python file to process
    @param      doall                   unused
    @param      exc                     raise an exception if needed
    @param      nblinks                 dictionary ``{ref: url}``
    @param      notebook_replacements   string replacement in notebooks
    @param      fLOG                    logging function
    """
    if os.path.isfile(root):
        file = root
        with open(file, "r", encoding="utf8") as f:
            content = f.read()
        content = post_process_python(
            content, doall, nblinks=nblinks, file=file, fLOG=fLOG,
            notebook_replacements=notebook_replacements)
        with open(file, "w", encoding="utf8") as f:
            f.write(content)
    else:
        build = os.path.join(root, "_doc", "sphinxdoc", "build", "latex")
        if not os.path.exists(build) and exc:
            raise FileNotFoundError(build)
        for tex in os.listdir(build):
            if tex.endswith(".tex"):
                file = os.path.join(build, tex)
                fLOG("[post_process_python_output] modify file", file)
                with open(file, "r", encoding="utf8") as f:
                    content = f.read()
                content = post_process_python(
                    content, doall, info=file, nblinks=nblinks, file=file, fLOG=fLOG)
                with open(file, "w", encoding="utf8") as f:
                    f.write(content)


def post_process_latex_output_any(file, custom_latex_processing, nblinks=None,
                                  remove_unicode=False, fLOG=None, notebook_replacements=None):
    """
    Postprocesses the latex file produced by :epkg:`sphinx`.

    @param      file                        latex filename
    @param      custom_latex_processing     function which does some post processing of the full latex file
    @param      nblinks                     dictionary ``{url: link}``
    @param      remove_unicode              remove unicode characters
    @param      notebook_replacements       string replacement in notebooks
    @param      fLOG                        logging function
    """
    if fLOG:
        fLOG("[post_process_latex_output_any]   ** post_process_latex_output_any ", file)
    if not os.path.exists(file):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}', other files in the same folder\n{}".format(
                file, "\n".join(os.listdir(os.path.dirname(file)))))
    with open(file, "r", encoding="utf8") as f:
        content = f.read()
    with open(file + ".tex3.u{0}~".format(1 if remove_unicode else 0), "w", encoding="utf8") as f:
        f.write(content)
    content = post_process_latex(content, True, info=file, nblinks=nblinks, file=file,
                                 remove_unicode=remove_unicode, fLOG=fLOG,
                                 notebook_replacements=notebook_replacements)
    with open(file, "w", encoding="utf8") as f:
        f.write(content)


def post_process_rst_output(file, html, pdf, python, slides, is_notebook=False,
                            exc=True, github=False, notebook=None, nblinks=None, fLOG=None,
                            notebook_replacements=None):
    """
    Processes a :epkg:`rst` file generated from the conversion of a notebook.

    @param      file                    filename
    @param      pdf                     if True, add a link to the :epkg:`pdf`,
                                        assuming it will exists at the same location
    @param      html                    if True, add a link to the :epkg:`html` conversion
    @param      python                  if True, add a link to the :epkg:`Python` conversion
    @param      slides                  if True, add a link to the slides conversion
    @param      is_notebook             does something more if the file is a notebook
    @param      exc                     raises an exception (True) or a warning (False)
    @param      github                  add a link to the notebook on :epkg:`github`
    @param      notebook                location of the notebook, file might be a copy
    @param      nblinks                 links added to a notebook, dictionary ``{ref: url}``
    @param      notebook_replacements   string replacement in notebooks
    @param      fLOG                    logging function

    The function adds the following replacement
    ``st = st.replace("\\\\mathbb{1}", "\\\\mathbf{1\\\\!\\\\!1}")``.
    and checks that audio is only included in :epkg:`HTML`.
    """
    if fLOG:
        fLOG("[post_process_rst_output] %r" % file)

    name = os.path.split(file)[1]
    noext = os.path.splitext(name)[0]
    with open(file, "r", encoding="utf8") as f:
        lines = f.readlines()
    with open(file + "~", "w", encoding="utf8") as f:
        f.write("".join(lines))

    # Probably not the best way to fix that.
    # For some reason, nbconvert adds None as the first row.
    if lines[0] == 'None\n':
        lines[0] = '\n'

    if any(line == 'None\n' for line in lines):
        raise HelpGenException(  # pragma: no cover
            "One row unexpectedly contains only None in '{}'\n{}".format(
                file, "".join(lines[:20])))

    # Removes empty lines in inserted code, also adds line number.
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
                        fLOG("[post_process_rst_output] EMPTY-SECTION in ", file)
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
                raise HelpGenException(  # pragma: no cover
                    "Unable to extract image name in '{0}'".format(lines[pos]))
            nameimg = img[0]
            short = nameimg.replace("%5C", "/")
            short = os.path.split(short)[-1]
            lines[pos] = lines[pos].replace(nameimg, short)

    # title
    for pos, line in enumerate(lines):
        line = line.strip("\n\r")
        if len(line) > 0 and line == "=" * len(line):
            # lines[pos] = lines[pos].replace("=", "*")
            pos2 = pos - 1
            li = len(lines[pos])
            while len(lines[pos2]) != li:
                pos2 -= 1
            sep = "" if lines[pos2].endswith("\n") else "\n"
            lines[pos2] = "{0}{2}{1}".format(lines[pos], lines[pos2], sep)
            for p in range(pos2 + 1, pos):
                if lines[p] == "\n":
                    lines[p] = ""
            break

    pos += 1
    if pos >= len(lines):
        mes = "Unable to find a title in notebook '{0}'".format(file)
        if exc:
            raise HelpGenException(mes)  # pragma: no cover
        warnings.warn(mes, UserWarning)

    # label
    labelname = name.replace(" ", "").replace("_", "").replace(
        ":", "").replace(".", "").replace(",", "")
    label = "\n.. _{0}:\n\n".format(labelname)
    lines.insert(0, label)

    # links
    links = ['**Links:** :download:`notebook <{0}.ipynb>`'.format(noext)]
    if html:
        links.append(':downloadlink:`html <{0}2html.html>`'.format(noext))
    if pdf:
        links.append(':download:`PDF <{0}.pdf>`'.format(noext))
    if python:
        links.append(':download:`python <{0}.py>`'.format(noext))
    if slides:
        links.append(':downloadlink:`slides <{0}.slides.html>`'.format(noext))

    if github:
        if notebook is None:
            raise ValueError(  # pragma: no cover
                "Cannot add a link on github, notebook is None for file='{0}'".format(file))
        docname = notebook
        folder = docname
        git = os.path.join(folder, ".git")
        while len(folder) > 0 and not os.path.exists(git):
            folder = os.path.split(folder)[0]
            git = os.path.join(folder, ".git")
        if len(folder) > 0:
            path = docname[len(folder):]
        if path.strip('/\\').startswith('build'):
            # The notebook may be in a build folder but is not
            # the original notebooks. The function does something
            # if the path starts with `build`.
            subfolds = os.listdir(folder)
            for sub in subfolds:
                fulls = os.path.join(folder, sub)
                if not os.path.isdir(fulls):
                    continue
                if not ('doc' in sub or 'notebook' in sub or 'example' in sub):
                    continue
                # Search for another version of the file.
                last_name = os.path.split(docname)[-1]
                selected = glob.glob(
                    fulls + "/**/" + last_name, recursive=True)
                if len(selected) != 1:
                    docname = selected[0]
                    path = docname[len(folder):]
                    break
        links.append(
            ":githublink:`GitHub|{0}|*`".format(path.replace("\\", "/").lstrip("/")))
    lines[pos] = "{0}\n\n.. only:: html\n\n    {1}\n\n".format(
        lines[pos], ", ".join(links))

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
        fLOG("[post_process_rst_output]    *** remove div absolute in ", file)
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
                and pos < len(lines) - 1:
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
    for i in range(len(lines), 1, -1):
        s = lines[i - 1].strip(" \n\r")
        if len(s) != 0 and s != "::":
            break

    if i < len(lines):
        del lines[i:]

    # specific treatment for notebooks
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

    # checking for find://
    content = "".join(lines)
    content = update_notebook_link(content, "rst", nblinks=nblinks, fLOG=fLOG)
    if "find://" in content:
        raise HelpGenException(  # pragma: no cover
            "find:// was found in '{0}'.\nYou should "
            "add or extend 'nblinks' in conf.py.".format(file))

    # notebooks replacements
    content = _notebook_replacements(content, notebook_replacements, fLOG)

    # replaces the function
    content = content.replace("\\mathbb{1}", "\\mathbf{1\\!\\!1}")

    with open(file, "w", encoding="utf8") as f:
        f.write(content)


def post_process_html_output(file, pdf, python, slides, exc=True,
                             nblinks=None, fLOG=None,
                             notebook_replacements=None):
    """
    Processes a HTML file generated from the conversion of a notebook.

    @param      file                    filename
    @param      pdf                     if True, add a link to the PDF, assuming it will exists
                                        at the same location
    @param      python                  if True, add a link to the Python conversion
    @param      slides                  if True, add a link to the slides conversion
    @param      exc                     raises an exception (True) or a warning (False)
    @param      nblinks                 dictionary ``{ref: url}``
    @param      notebook_replacements   string replacement in notebooks
    @param      fLOG                    logging function
    """
    if not os.path.exists(file):
        raise FileNotFoundError(file)  # pragma: no cover
    with open(file, "r", encoding="utf8") as f:
        text = f.read()

    # mathjax
    text = text.replace("https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML",
                        "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML")

    # notebook replacements
    if fLOG:
        fLOG("[post_process_html_output] ", notebook_replacements)
    text = _notebook_replacements(text, notebook_replacements, fLOG)

    text = update_notebook_link(text, "html", nblinks=nblinks, fLOG=fLOG)
    if "find://" in text:
        raise HelpGenException(  # pragma: no cover
            "find:// was found in '{0}'.\nYou should add "
            "or extend 'nblinks' in conf.py.".format(file))

    with open(file, "w", encoding="utf8") as f:
        f.write(text)


def post_process_slides_output(file, pdf, python, slides, exc=True,
                               nblinks=None, fLOG=None,
                               notebook_replacements=None):
    """
    Processes a :epkg:`HTML` file generated from the conversion of a notebook.

    @param      file                    filename
    @param      pdf                     if True, add a link to the PDF, assuming it will
                                        exists at the same location
    @param      python                  if True, add a link to the Python conversion
    @param      slides                  if True, add a link to the slides conversion
    @param      exc                     raises an exception (True) or a warning (False)
    @param      nblinks                 dictionary ``{ref: url}``
    @param      notebook_replacements   string replacement in notebooks
    @param      fLOG                    logging function
    """
    if (len(file) > 5000 or not os.path.exists(file)) and "<html" in file:
        text = file
        save = False
    else:
        if not os.path.exists(file):
            raise FileNotFoundError(file)
        # fold, name = os.path.split(file)
        with open(file, "r", encoding="utf8") as f:
            text = f.read()
        save = True

    # reveal.js
    require = "require(" in text
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
        if lines[i] == "</script>" and require:
            lines[i] += '\n<script src="require.js"></script>'
            require = False
    text = "\n".join(lines)

    # mathjax
    text = text.replace("https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML",
                        "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML")
    text = update_notebook_link(text, "slides", nblinks=nblinks, fLOG=fLOG)
    if "find://" in text:
        raise HelpGenException(  # pragma: no cover
            "find:// was found in '{0}'.\nYou should add "
            "or extend 'nblinks' in conf.py.".format(file))

    # notebook replacements
    text = _notebook_replacements(text, notebook_replacements, fLOG)

    if save:
        with open(file, "w", encoding="utf8") as f:
            f.write(text)
    return text


def post_process_latex(st, doall, info=None, latex_book=False, exc=True,
                       custom_latex_processing=None, nblinks=None, file=None,
                       remove_unicode=False, fLOG=None, notebook_replacements=None):
    """
    Modifies a :epkg:`latex` file after its generation by :epkg:`sphinx`.

    @param      st                      string
    @param      doall                   do all transformations
    @param      info                    for more understandable error messages
    @param      latex_book              customized for a book
    @param      exc                     raises an exception or a warning
    @param      custom_latex_processing function which takes and returns a string,
                                        final post processing
    @param      nblinks                 dictionary ``{ref: url}``
    @param      file                    only used when an exception is raised
    @param      remove_unicode          remove unicode character (fails when converting into PDF)
    @param      notebook_replacements   string replacement in notebooks
    @param      fLOG                    logging function
    @return                             string

    *SVG* included in a notebook (or in *RST* file) usually do not word.
    :epkg:`Inkscape` should be used to convert them into Latex.
    The function is less strict on the checking of `$`.
    The function replaces ``\\mathbb{1}`` by ``\\mathbf{1\\!\\!1}``.

    .. index:: chinese characters, latex, unicode

    .. faqref::
        :title: Why a ¿ is showing the final PDF?

        Unicode, chinese characters are an issue because the latex compiler
        prompts on those if the necessary packages are not installed.
        `pdflatex <https://en.wikipedia.org/w/index.php?title=PdfTeX&redirect=no>`_
        does not accepts inline chinese
        characters, `xetex <https://en.wikipedia.org/wiki/XeTeX>`_
        should be used instead:
        see `How to input Traditional Chinese in pdfLaTeX
        <http://tex.stackexchange.com/questions/200449/how-to-input-traditional-chinese-in-pdflatex>`_.
        Until this is being implemented, the unicode will unfortunately be removed
        in this function.

    .. versionchanged:: 1.9
        Removes the uses of package `parskip
        <https://ctan.org/pkg/parskip?lang=en>`_, it uses command
        ``\\DeclareRelease`` which is not always recognized.
    """
    if fLOG:
        fLOG("[post_process_latex]   ** enter post_process_latex",
             doall, "%post_process_latex" in st)
    weird_character = set(chr(i) for i in range(1, 9))

    def clean_unicode(c):
        if c == "’":
            return "'"
        if c == "…":
            return "..."
        if ord(c) >= 255 or c in weird_character:
            return "\\textquestiondown "
        return c

    def clean_line(line):
        if line.startswith("\\documentclass"):
            line = line.replace("{None}", "{report}")
        return line

    lines = st.split("\n")
    lines = list(map(clean_line, lines))
    st = "\n".join("".join(map(clean_unicode, line)) for line in lines)

    # we count the number of times we have \$ (which is unexpected unless the
    # currency is used.
    dollar = st.split("\\$")
    if len(dollar) > 0 and (
            info is None or os.path.splitext(info)[-1] != ".html"):
        # it could be an issue, for the time being, we raise
        # an exception if a formula is too long
        exp = re.compile(r"(.{200}[\\]\$\$)")
        found = 0
        records = []
        for m in exp.finditer(st):
            found += 1
            p1, p2 = m.start(), m.end()
            sub = st[p1:p2].strip(" \r\n").replace(
                "\n", " ").replace("\r", "").replace("\t", " ")
            sub2 = sub[-10:]
            records.append((info, p1, p2, sub, sub2, ""))
        if len(records) > 0:
            messages = [str(i) + ":" + ("unexpected \\$ in a latex file:\n    {0}\n" +
                                        "at position: {1},{2}\n    substring: {3}\n    " +
                                        "around: {4}\n    temp=[{5}]").format(*rec)
                        for i, rec in enumerate(records)]
            for mes in messages:
                warnings.warn(mes, UserWarning)

    st = st.replace("<br />", "\\\\")
    st = st.replace("»", '"')
    st = st.replace("\\mathbb{1}", "\\mathbf{1\\!\\!1}")
    st = st.replace(
        "\\documentclass[11pt]{article}", "\\documentclass[10pt]{article}")

    if not doall and not latex_book:
        st = st.replace(
            "\\maketitle", "\\maketitle\n\n\\newchapter{Introduction}")

    st = st.replace("%5C", "/") \
           .replace("%3A", ":") \
           .replace("\\includegraphics{notebooks\\", "\\includegraphics {")
    st = st.replace(
        "\\begin{document}", "\\setlength{\\parindent}{0cm}%s\\begin {document}" % "\n")
    st = st.replace("DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\\\\{\\}}",
                    "DefineVerbatimEnvironment{Highlighting}{Verbatim} {commandchars=\\\\\\{\\},fontsize=\\small}")
    st = st.replace("\\textquotesingle{}", "'")
    st = st.replace("\u0001", "\\u1")
    st = st.replace("\\begin{notice}{note}\\end{notice}", "")

    # hyperref
    if doall and "%post_process_latex" not in st:
        st = "%post_process_latex\n" + st
        reg = re.compile("hyperref[\\[]([a-zA-Z0-9]+)[\\]][\\{](.*?)[\\}]")
        allhyp = reg.findall(st)
        sections = []
        for id, section in allhyp:
            sec = r"\subsection{%s} \label{%s}" % (section, id)
            sections.append((id, section, sec))
    elif not doall and not latex_book:
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

    if not latex_book:
        st = st.replace("\\chapter", "\\section")
        st = st.replace("\\newchapter", "\\chapter")

    comment_out = [
        '\\usepackage{parskip}',
        '\\usepackage{fontspec}',
        '\\begin{center}\\rule{0.5\\linewidth}{\\linethickness}\\end{center}\n',
    ]
    for co in comment_out:
        if co in st:
            st = st.replace(co, "%" + co)
    if "\\usepackage{multirow}" in st:
        st = st.replace(
            "\\usepackage{svg}\\usepackage{multirow}",
            "\\usepackage{multirow}\\usepackage{amssymb}\\usepackage{latexsym}\\usepackage{amsfonts}\\usepackage{ulem}\\usepackage{textcomp}")
    elif "\\usepackage{hyperref}" in st:
        st = st.replace(
            "\\usepackage{svg}\\usepackage{hyperref}",
            "\\usepackage{hyperref}\\usepackage{amssymb}\\usepackage{latexsym}\\usepackage{amsfonts}\\usepackage{ulem}\\usepackage{textcomp}")
    else:
        raise HelpGenException(
            "unable to add new instructions usepackage in file {0}".format(info))

    # SVG does not work unless it is converted (nbconvert should handle that
    # case)
    reg = re.compile("([\\\\]includegraphics[{].*?[.]svg[}])")
    fall = reg.findall(st)
    for found in fall:
        st = st.replace(found, "%" + found)

    # fix references
    st = update_notebook_link(st, "latex", nblinks=nblinks, fLOG=fLOG)
    if "find://" in st:
        raise HelpGenException(  # pragma: no cover
            "find:// was found in '{0}'\nYou should add or extend "
            "'nblinks' in conf.py.\n{1}".format(file, st))

    # notebook replacements
    st = _notebook_replacements(st, notebook_replacements, fLOG)

    # end
    if custom_latex_processing is not None:
        st = custom_latex_processing(st)

    if remove_unicode:
        encoding = 'ascii'
    else:
        encoding = 'utf-8'
    st0 = st
    bst = st.encode(encoding, errors='replace')
    st = bst.decode(encoding, errors='replace')
    if st0 != st and fLOG:
        fLOG("[post_process_latex] characters were removed for encoding", encoding)
    return st


def post_process_python(st, doall, info=None, nblinks=None, file=None, fLOG=None, notebook_replacements=None):
    """
    Modifies a python file after its generation by :epkg:`sphinx`.

    @param      st                      string
    @param      doall                   do all transformations
    @param      info                    for more understandable error messages
    @param      nblinks                 dictionary ``{ref: url}``
    @param      file                    used only when an exception is raised
    @param      fLOG                    logging function
    @param      notebook_replacements   string replacement in notebooks
    @return                             string
    """
    st = st.strip("\n \r\t")
    st = st.replace("# coding: utf-8", "# -*- coding: utf-8 -*-")
    st = update_notebook_link(st, "python", nblinks=nblinks, fLOG=fLOG)
    if "find://" in st:
        raise HelpGenException(  # pragma: no cover
            "find:// was found in '{0}'.\nYou should add or extend "
            "'nblinks' in conf.py.".format(file))

    # notebook replacements
    st = _notebook_replacements(st, notebook_replacements, fLOG)

    return st


def remove_character_under32(s):
    """
    Removes :epkg:`ASCII` characters in *[0..31]*.

    @param      s       string to process
    @return             filtered string
    """
    ls = ""
    for c in s:
        d = ord(c)
        if 0 <= d < 32:
            ls += " "
        else:
            ls += c
    return ls
