"""
@file
@brief Helpers for markdown functionalities, it requires dependencies on `mistune <https://pypi.python.org/pypi/mistune>`_.
"""
import re


def parse_markdown(text):
    """
    parse markdown text and return the markdown object

    @param      text        markdown text
    @return
    """
    import mistune
    markdown = mistune.Markdown()
    r = markdown(text)
    return r


def yield_sphinx_only_markup_for_pipy(lines):
    """
    code from `My rst README is not formatted on pypi.python.org <http://stackoverflow.com/questions/16367770/my-rst-readme-is-not-formatted-on-pypi-python-org>`_

    :param file_inp:     a `filename` or ``sys.stdin``?
    :param file_out:     a `filename` or ``sys.stdout`?`

    """
    substs = [
        # Selected Sphinx-only Roles.
        #
        (r':abbr:`([^`]+)`',        r'\1'),
        (r':ref:`([^`]+)`',         r'`\1`_'),
        (r':term:`([^`]+)`',        r'**\1**'),
        (r':dfn:`([^`]+)`',         r'**\1**'),
        (r':(samp|guilabel|menuselection):`([^`]+)`',        r'``\2``'),


        # Sphinx-only roles:
        #        :foo:`bar`   --> foo(``bar``)
        #        :a:foo:`bar` XXX afoo(``bar``)
        #
        #(r'(:(\w+))?:(\w+):`([^`]*)`', r'\2\3(``\4``)'),
        (r':(\w+):`([^`]*)`', r'\1(``\2``)'),


        # Sphinx-only Directives.
        #
        (r'\.\. doctest',           r'code-block'),
        (r'\.\. plot::',            r'.. '),
        (r'\.\. seealso',           r'info'),
        (r'\.\. glossary',          r'rubric'),
        (r'\.\. figure::',          r'.. '),


        # Other
        #
        (r'\|version\|',              r'x.x.x'),
    ]

    regex_subs = [(re.compile(regex, re.IGNORECASE), sub)
                  for (regex, sub) in substs]

    def clean_line(line):
        try:
            for (regex, sub) in regex_subs:
                line = regex.sub(sub, line)
        except Exception as ex:
            raise Exception("ERROR: %s, (line(%s)" % (regex, sub)) from ex

        return line

    for line in lines:
        yield clean_line(line)
