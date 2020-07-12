# -*- coding: utf-8 -*-
"""
sphinxjp.themes.revealjs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author: tell-k <ffk2005@gmail.com>
:copyright: tell-k. All Rights Reserved.

Taken from `github/return42 <https://github.com/return42/sphinxjp.themes.revealjs>`_.
"""

from os import path
from . import directives

__version__ = '0.3.1'

package_dir = path.abspath(path.dirname(__file__))
template_path = path.join(package_dir, 'templates')


def get_path():
    """entry-point for sphinx  theme."""
    return template_path  # pragma: no cover


def setup(app):
    """entry-point for sphinx  directive."""
    directives.setup(app)  # pragma: no cover
