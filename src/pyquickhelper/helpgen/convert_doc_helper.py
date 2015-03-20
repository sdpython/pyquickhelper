"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.0
"""

import io
import re
import textwrap
from docutils import core
from .utils_sphinx_doc import migrating_doxygen_doc
from ..loghelper.flog import noLOG

# -- HELP BEGIN EXCLUDE --

from .utils_sphinx_doc import private_migrating_doxygen_doc

# -- HELP END EXCLUDE --


def rst2html(s, fLOG=noLOG):
    """
    converts a string into HTML format

    @param  s       string to converts
    @param  fLOG    logging function (warnings will be logged)
    @return         HTML format

    .. versionadded:: 1.0
    """

    settings_overrides = {'output_encoding': 'unicode',
                          'doctitle_xform': True,
                          'initial_header_level': 2,
                          'warning_stream': io.StringIO()}

    parts = core.publish_parts(source=s, source_path=None, destination_path=None,
                               writer_name='html', settings_overrides=settings_overrides)

    fLOG(settings_overrides["warning_stream"].getvalue())

    exp = re.sub(
        '(<div class="system-message">(.|\\n)*?</div>)', "", parts["whole"])
    return exp


def correct_indentation(text):
    """
    tries to improve the indentation before running docutil

    @param      text        text to correct
    @return                 corrected text

    .. versionadded:: 1.0
    """
    title = {}
    rows = text.split("\n")
    for row in rows:
        row = row.replace("\t", "    ")
        cr = row.lstrip()
        ind = len(row) - len(cr)

        tit = cr.strip("\r\n\t ")
        if len(tit) > 0 and tit[0] in "-+=*^" and tit == tit[0] * len(tit):
            title[ind] = title.get(ind, 0) + 1

    mint = min(title.keys())
    if mint > 0:
        newrows = []
        for row in rows:
            i = 0
            while i < len(row) and row[i] == ' ':
                i += 1

            rem = min(i, mint)
            if rem > 0:
                newrows.append(row[rem:])
            else:
                newrows.append(row)

        return "\n".join(newrows)
    else:
        return text


def docstring2html(function_or_string, format="html", fLOG=noLOG):
    """
    converts a docstring into a HTML format

    @param      function_or_string      function, class, method or doctring
    @param      format                  output format
    @param      fLOG                    logging function
    @return                             (str) HTML format or (IPython.core.display.HTML)

    @example(Produce HTML documentation for a function or class)

    The following code can display the dosstring in HTML format
    to display it in a notebook.

    @code
    from pyquickhelper import docstring2html
    import sklearn.linear_model
    docstring2html(sklearn.linear_model.LogisticRegression)
    @endcode

    @endexample

    The output format is defined by:

        * html: IPython HTML object
        * rawhtml: HTML as text + style
        * rst: rst
        * text: raw text

    .. versionadded:: 1.0
    """
    if not isinstance(function_or_string, str):
        doc = function_or_string.__doc__
    else:
        doc = function_or_string

    if format == "text":
        return doc

    javadoc = migrating_doxygen_doc(doc, "None", log=False)
    rows = javadoc.split("\n")
    rst = private_migrating_doxygen_doc(
        rows, index_first_line=0, filename="None")
    rst = "\n".join(rst)
    ded = textwrap.dedent(rst)

    if format == "rst":
        return ded

    try:
        html = rst2html(ded, fLOG=fLOG)
    except Exception:
        # we check the indentation
        ded = correct_indentation(ded)
        try:
            html = rst2html(ded, fLOG=fLOG)
        except Exception as e:
            raise Exception("unable to process:\n{0}".format(ded)) from e

    if format == "html":
        from IPython.core.display import HTML
        return HTML(html)
    elif format == "rawhtml":
        return html
    else:
        raise ValueError(
            "unexected format: " + format + ", should be html, rawhtml, text, rst")
