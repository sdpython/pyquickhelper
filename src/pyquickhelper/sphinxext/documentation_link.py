"""
@file
@brief Automated link to documentation.
"""


def python_link_doc(m, o=None, format="rst"):
    """
    Returns a url about :epkg:`Python` documentation.

    .. runpython::
        :showcode:

        from pyquickhelper.sphinxext import python_link_doc
        print(python_link_doc("io"))

    @param      m           Python module
    @param      o           function name or class name
    @param      format      'rst' or 'raw'
    @return                 str or tuple
    """
    if format == "raw":
        if o is None:
            return m, f"https://docs.python.org/3/library/{m}.html"
        return (f"{m}.{o}",
                "https://docs.python.org/3/library/{0}.html#{0}.{1}".format(m, o))
    if format == "rst":
        name, url = python_link_doc(m, o, format="raw")
        return f"`{name} <{url}>`_"
    raise ValueError(  # pragma: no cover
        f"Unexpected format '{format}'")
