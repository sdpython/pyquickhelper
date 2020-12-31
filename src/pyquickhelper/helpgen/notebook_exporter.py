# -*- coding: utf-8 -*-
"""
@file
@brief Customer notebook exporters.

.. versionadded:: 1.7
"""
import os
from textwrap import indent
from traitlets import default
from traitlets.config import Config
from jinja2 import DictLoader
from nbconvert.exporters import RSTExporter
from nbconvert.filters.pandoc import convert_pandoc


def convert_pandoc_rst(source, from_format, to_format, extra_args=None):
    """
    Overwrites `convert_pandoc
    <https://github.com/jupyter/nbconvert/blob/master/nbconvert/filters/pandoc.py>`_.

    @param      source          string to convert
    @param      from_format     from format
    @param      to_format       to format
    @param      extra_args      extra arguments
    @return                     results
    """
    return convert_pandoc(source, from_format, to_format, extra_args=None)


def process_raw_html(source, extra_args=None):
    """
    Replaces the output of
    `add_menu_notebook
    <http://www.xavierdupre.fr/app/jyquickhelper/helpsphinx/jyquickhelper/
    helper_in_notebook.html#jyquickhelper.helper_in_notebook.add_notebook_menu>`_
    by:

    ::

        .. contents::
            :local:
    """
    if source is None:
        return source
    if 'var update_menu = function() {' in source:
        return "\n\n.. contents::\n    :local:\n\n"
    return "\n\n.. raw:: html\n\n" + indent(source, prefix='    ')


class UpgradedRSTExporter(RSTExporter):
    """
    Exports :epkg:`rst` documents.
    Overwrites `RSTExporter <https://github.com/jupyter/
    nbconvert/blob/master/nbconvert/exporters/rst.py>`_.

    * It replaces `convert_pandoc <https://github.com/jupyter/
    nbconvert/blob/master/nbconvert/filters/pandoc.py>`_
      by @see fn convert_pandoc_rst.
    * It converts :epkg:`svg` into :epkg:`png` if possible,
      see @see fn process_raw_html.
    * It replaces some known :epkg:`javascript`. The output of function
      `add_menu_notebook <http://www.xavierdupre.fr/app/jyquickhelper/helpsphinx/jyquickhelper/
      helper_in_notebook.html#jyquickhelper.helper_in_notebook.add_notebook_menu>`_
      is replaced by ``.. contents::``.

    .. index:: notebook export, nbconvert

    It extends the template
    `rst.tpl <https://github.com/jupyter/nbconvert/blob/master/nbconvert/templates/rst.tpl>`_.
    New template is `rst_modified.tpl <https://github.com/sdpython/pyquickhelper/blob/master/
    src/pyquickhelper/helpgen/rst_modified.tpl>`_.
    It follows the hints given at
    `Programatically creating templates
    <https://nbconvert.readthedocs.io/en/latest/
    nbconvert_library.html#Programatically-creating-templates>`_.

    :epkg:`jyquickhelper` should add a string highly recognizable when adding a menu.
    """

    def __init__(self, *args, **kwargs):
        """
        Overwrites the extra loaders to get the right template.
        """
        filename = os.path.join(os.path.dirname(__file__), 'rst_modified.tpl')
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        filename = os.path.join(os.path.dirname(__file__), 'rst.tpl')
        with open(filename, 'r', encoding='utf-8') as f:
            content2 = f.read()

        dl = DictLoader({'rst_modified.tpl': content, 'rst.tpl': content2})
        kwargs['extra_loaders'] = [dl]
        RSTExporter.__init__(self, *args, **kwargs)

    def default_filters(self):
        """
        Overrides in subclasses to provide extra filters.

        This should return an iterable of 2-tuples: (name, class-or-function).
        You should call the method on the parent class and include the filters
        it provides.

        If a name is repeated, the last filter provided wins. Filters from
        user-supplied config win over filters provided by classes.
        """
        for k, v in RSTExporter.default_filters(self):
            yield (k, v)
        yield ('convert_pandoc_rst', convert_pandoc_rst)
        yield ('process_raw_html', process_raw_html)

    output_mimetype = 'text/restructuredtext'
    export_from_notebook = "reST"

    @default('template_file')
    def _template_file_default(self):
        return "rst_modified.tpl"

    @default('file_extension')
    def _file_extension_default(self):
        return '.rst'

    @default('template_name')
    def _template_name_default(self):
        return 'rst'

    @property
    def default_config(self):
        c = Config({
            'ExtractOutputPreprocessor': {
                'enabled': True,
                'output_filename_template': '{unique_key}_{cell_index}_{index}{extension}'
            },
            'HighlightMagicsPreprocessor': {
                'enabled': True
            },
        })
        c.merge(super(UpgradedRSTExporter, self).default_config)
        return c
