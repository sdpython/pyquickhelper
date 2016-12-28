
.. blogpost::
    :title: Export a notebook with no code
    :keywords: notebook, nbconvert
    :date: 2016-10-10
    :categories: notebook

    Sometimes, you just want to remove all codes from your report.
    You can just reasd the json of a notebook and remove all codes by yourself
    or you can add an extra preprocessor which removes all the code
    in a notebook. We do something similar to this
    `example <https://github.com/jupyter/nbconvert-examples/tree/master/custom_preprocessor>`_.
    First we create a preprocessor:

    ::

        from nbconvert.preprocessors import Preprocessor

        class LatexNoCodePreprocessor(Preprocessor):
            def preprocess_cell(self, cell, resources, cell_index):
                if cell.cell_type == 'code':
                    if isinstance(cell.code, list):
                        cell.source = []
                    else:
                        cell.source = ""
                return cell, resources

    And then a configuration file ``config.py`` for
    `nbconvert <https://nbconvert.readthedocs.io/en/latest/>`_:

    ::

        c = get_config()
        c.Exporter.preprocessors = [
            'custom_nbconvert_preprocessor.LatexNoCodePreprocessor']

    And finally the command line:

    ::

        nbconvert --config config.py --to latex --template article <notebook.ipynb> --output <notebook.tex>

    To avoid import issues, the command line must be run from the folder
    which contains ``config.py`` and ``custom_nbconvert_preprocessor.py``.