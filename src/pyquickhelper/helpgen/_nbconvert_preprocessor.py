"""
@file
@brief Custom configuration for nbconvert,
see `custom_preprocessor <https://github.com/jupyter/nbconvert-examples/blob/master/custom_preprocessor/>`_
"""
from nbconvert.preprocessors import Preprocessor


class LatexRawOutputPreprocessor(Preprocessor):
    """
    Custom processor to apply a different style on raw output.
    """

    def __init__(self, *args, **kwargs):
        """
        Overloads the constructor.
        """
        Preprocessor.__init__(self, *args, **kwargs)

    def preprocess_cell(self, cell, resources, cell_index):  # pylint: disable=W0221
        """
        Applies a transformation on each cell. See base.py for details,
        add ``\\begin{verbatim}`` and ``\\end{verbatim}``.
        """
        if cell.cell_type == 'raw':
            if isinstance(cell.source, list):
                cell.source = ["\\begin{verbatim}\n"] + \
                    cell.source + ["\\end{verbatim}\n"]
            else:
                cell.source = "\\begin{verbatim}\n%s\n\\end{verbatim}\n" % cell.source
        return cell, resources
