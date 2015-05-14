"""
@file
@brief Functions to call from the notebook
"""

from IPython.display import Javascript


def store_notebook_path(name="theNotebook"):
    """
    return Javascript object to execute in order to store
    the notebook file name into a variable
    available from the notebook

    @param      name        name of the variable
    @return                 Javascript object

    The function uses the following code to get the notebook path::

        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "theNotebook = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);

    Example::

        from pyquickhelper.ipythonhelper import store_notebook_path
        store_notebook_path()

    In another cell::

        theNotebook

    See notebook :ref:`exempleoffixmenurst`.
    """
    js = """
        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "{0} = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);
        """.replace("        ", "").format(name)
    return Javascript(js)
