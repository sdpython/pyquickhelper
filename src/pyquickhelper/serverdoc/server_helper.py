# -*- coding:utf-8 -*-
"""
@file
@brief Helpers about a documentation.
"""

import os
import warnings


def get_jenkins_mappings(root, loc="dist"):
    """
    we assume jobs were set up through a jenkins server,
    the function looks into folder *root* and list
    folder ``root/.*/dist/html.*``

    @param      root        folder or list of folders or list of tuple ``(prefix, folder)``
    @param      loc         *dist* by default (dist in the folder mentioned above),
                            it could also be ``_doc/sphinxdoc/build``
    @return                 dictionary { "name":folder }
    """
    if not isinstance(root, list):
        roots = [root]
    else:
        roots = root

    maps = {}
    for ro in roots:
        if isinstance(ro, tuple):
            prefix, ro = ro
        else:
            prefix, ro = "", ro  # pylint: disable=W0127
        ro = os.path.abspath(ro)
        sub = os.listdir(ro)
        for s in sub:
            fold = os.path.join(ro, s)
            if os.path.isdir(fold):
                dist = os.path.join(fold, loc)
                if os.path.exists(dist):
                    ht = os.listdir(dist)
                    for h in ht:
                        if h.startswith("html"):
                            index = os.path.join(dist, h, "index.html")
                            if os.path.exists(index):
                                name = prefix + s + "-" + \
                                    h.replace("/", "_").replace("\\", "_")
                                maps[name] = os.path.join(dist, h)

    if len(maps) == 0:
        warnings.warn(  # pragma: no cover
            "Unable to find any folder in '{0}'".format(root), UserWarning)
    return maps
