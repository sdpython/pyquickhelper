"""
@file
@brief Parse a file *.yml* and convert it into a set of actions.

.. todoext::
    :title: define Jenkins job with .yml
    :tag: enhancement
    :cost: 0.1
    :date: 2016-08-16
    :issue: 29

    The current build system is not easy to read.
    This should make things more clear and easier to maintain.

.. versionadded:: 1.4
"""
import os
import yaml
from ..texthelper.templating import apply_template


def load_yaml(file_or_buffer, context=None, engine="jinja2"):
    """
    loads a yaml file (.yml)

    @param      file_or_buffer      string or physical file
    @param      context             variables to replace in the configuration
    @param      engine              see @see fn apply_template
    @return                         see `PyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_
    """
    typstr = str  # unicode#
    if len(file_or_buffer) < 5000 and os.path.exists(file_or_buffer):
        with open(file_or_buffer, "r", encoding="utf-8") as f:
            file_or_buffer = f.read()
    if context is None:
        context = dict()
    file_or_buffer = apply_template(file_or_buffer, context, engine)
    return yaml.load(file_or_buffer)
