"""
@file
@brief Custom preprocessor,
see `custom_preprocessor <https://github.com/jupyter/nbconvert-examples/blob/master/custom_preprocessor/>`_
"""

# -- HELP BEGIN EXCLUDE --

try:
    c = get_config()  # pylint: disable=E0601
except ImportError as e:
    from IPython import get_config
    c = get_config()
c.Exporter.preprocessors = [
    '_nbconvert_preprocessor.LatexRawOutputPreprocessor']

# -- HELP END EXCLUDE --
