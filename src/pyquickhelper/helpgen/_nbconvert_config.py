"""
@file
@brief Custom preprocessor,
see `custom_preprocessor <https://github.com/jupyter/nbconvert-examples/blob/master/custom_preprocessor/>`_
"""

# -- HELP BEGIN EXCLUDE --

try:
    if c is None:
        pass
except NameError:
    try:  # pragma: no cover
        c = get_config()  # pylint: disable=E0601
    except (ImportError, NameError) as e:  # pragma: no cover
        from traitlets.config import get_config
        c = get_config()
c.Exporter.preprocessors = [
    '_nbconvert_preprocessor.LatexRawOutputPreprocessor']  # pragma: no cover

# -- HELP END EXCLUDE --
