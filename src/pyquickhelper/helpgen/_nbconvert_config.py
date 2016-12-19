"""
@file
@brief Custom preprocessor,
see `custom_preprocessor <https://github.com/jupyter/nbconvert-examples/blob/master/custom_preprocessor/>`_
"""
import os
try:
    c = get_config()
except ImportError as e:
    from IPython import get_config
    c = get_config()
c.Exporter.preprocessors = [
    '_nbconvert_preprocessor.LatexRawOutputPreprocessor']
