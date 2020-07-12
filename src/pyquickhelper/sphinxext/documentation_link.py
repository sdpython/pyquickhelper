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
            return m, "https://docs.python.org/3/library/{0}.html".format(m)
        return ("{0}.{1}".format(m, o),
                "https://docs.python.org/3/library/{0}.html{0}.{1}".format(m, o))
    if format == "rst":
        name, url = python_link_doc(m, o, format="raw")
        return "`{0} <{1}>`_".format(name, url)
    raise ValueError(  # pragma: no cover
        "Unexpected format '{0}'".format(format))
