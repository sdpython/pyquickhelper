"""
@file
@brief Helpers for markdown functionalities, it requires dependencies on :epkg:`mistune`.
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
    Code from `My rst README is not formatted on pypi.python.org
    <http://stackoverflow.com/questions/16367770/my-rst-readme-is-not-formatted-on-pypi-python-org>`_.

    :param lines: lines to process
    """
    substs = [
        # Selected Sphinx-only Roles.
        #
        (':abbr:`([^`]+)`', '\\1'),
        (':ref:`([^`]+)`', '`\\1`_'),
        (':term:`([^`]+)`', '**\\1**'),
        (':dfn:`([^`]+)`', '**\\1**'),
        (':(samp|guilabel|menuselection):`([^`]+)`', '``\\2``'),

        # Sphinx-only roles:
        #        :foo:`bar`   --> foo(``bar``)
        #        :a:foo:`bar` XXX afoo(``bar``)
        #
        #(r'(:(\w+))?:(\w+):`([^`]*)`', r'\2\3(``\4``)'),
        (':(\\w+):`([^`]*)`', '\\1(``\\2``)'),

        # Sphinx-only Directives.
        #
        ('\\.\\. doctest', 'code-block'),
        ('\\.\\. plot::', '.. '),
        ('\\.\\. seealso', 'info'),
        ('\\.\\. glossary', 'rubric'),
        ('\\.\\. figure::', '.. '),

        # Other
        #
        ('\\|version\\|', 'x.x.x'),
    ]

    regex_subs = [(re.compile(regex, re.IGNORECASE), sub)
                  for (regex, sub) in substs]

    def clean_line(line):
        try:
            for (regex, sub) in regex_subs:
                line = regex.sub(sub, line)
        except Exception as ex:
            raise Exception("[sphinxerror]-A %s, (line(%s)" %
                            (regex, sub)) from ex

        return line

    for line in lines:
        yield clean_line(line)
