"""
@file
@brief Helpers for markdown functionalities, it requires dependencies on `mistune <https://pypi.python.org/pypi/mistune>`_.
"""


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
