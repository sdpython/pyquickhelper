"""
@file
@brief Some automation helpers about notebooks
"""


class NotebookException(Exception):

    """
    Exception raises when something wrong happened with a notebook.
    """
    pass


class InNotebookException(Exception):

    """
    Exception raises when something wrong happened in a notebook.
    """
    pass


class JupyterException(Exception):

    """
    Exception raises by :epkg:`Jupyter`.
    """
    pass
