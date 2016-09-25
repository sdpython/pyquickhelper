# -*- coding: utf-8 -*-
"""
@file
@brief Functions to call from the notebook

.. versionadded:: 1.1
"""
import warnings
from jyquickhelper import store_notebook_path as _store_notebook_path
from jyquickhelper.helper_in_notebook import set_notebook_name_theNotebook as _set_notebook_name_theNotebook
from jyquickhelper import add_notebook_menu as _add_notebook_menu
from jyquickhelper.helper_in_notebook import load_extension as _load_extension


def store_notebook_path(name="theNotebook"):
    """
    See  `store_notebook_path <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/jyquickhelper/helpers_in_notebook.html>`_.
    """
    warnings.warn("The function has been moved to jyquickhelper.")
    return _store_notebook_path(name)


def set_notebook_name_theNotebook(name="theNotebook"):
    """
    See  `set_notebook_name_theNotebook <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/jyquickhelper/helpers_in_notebook.html>`_.
    """
    warnings.warn("The function has been moved to jyquickhelper.")
    return _set_notebook_name_theNotebook(name)


def add_notebook_menu(menu_id="my_id_menu_nb", raw=False, format="html", header=None,
                      first_level=2, last_level=4, keep_item=None):
    """
    See  `add_notebook_menu <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/jyquickhelper/helpers_in_notebook.html>`_.
    """
    warnings.warn("The function has been moved to jyquickhelper.")
    return _add_notebook_menu(menu_id=menu_id, raw=raw, format=format, header=header,
                              first_level=first_level, last_level=last_level, keep_item=keep_item)


def load_extension(name):
    """
    See  `load_extension <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/jyquickhelper/helpers_in_notebook.html>`_.
    """
    warnings.warn("The function has been moved to jyquickhelper.")
    return _load_extension(name)
