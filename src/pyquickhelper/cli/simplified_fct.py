"""
@file
@brief Simplified function versions.
"""
import os


def sphinx_rst(input="", writer="html", keep_warnings=False,
               directives=None, language="en",
               layout='sphinx', output="output"):
    """
    Converts a string from *RST*
    to *HTML* to *RST* format.

    @param      input               text of filename
    @param      writer              ``'html'`` for :epkg:`HTML` format,
                                    ``'rst'`` for :epkg:`RST` format,
                                    ``'md'`` for :epkg:`MD` format,
                                    ``'elatex'`` for :epkg:`latex` format,
                                    ``'doctree'`` to get the doctree, *writer* can also be a tuple
                                    for custom formats and must be like ``('buider_name', builder_class)``.
    @param      keep_warnings       keep_warnings in the final HTML
    @param      directives          new directives to add, comma separated values
    @param      language            language
    @param      layout              ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    @param      output              document name, the function adds the extension
    @return                         output
    """
    from ..helpgen import rst2html
    from ..filehelper import read_content_ufs
    if output:
        ext = os.path.splitext(output)[-1]
        if not ext:
            output += "." + writer
    if len(input) <= 5000 and (input.startswith('http') or
                               os.path.exists(input)):
        content = read_content_ufs(input)
    else:
        content = input
    if directives:
        raise NotImplementedError("Cannot specify directives yet.")
    split_dir = None
    res = rst2html(content, writer=writer, keep_warnings=keep_warnings,
                   directives=split_dir, language=language, layout=layout,
                   document_name=output)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output)
    return res
