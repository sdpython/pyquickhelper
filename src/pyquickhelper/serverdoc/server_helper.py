#-*- coding:utf-8 -*-
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

    .. versionchanged:: 1.3
        Parameter *root* accepts a list of foldes or tuples.
    """
    if not isinstance(root, list):
        roots = [root]
    else:
        roots = root

    maps = {}
    for root in roots:
        if isinstance(root, tuple):
            prefix, root = root
        else:
            prefix, root = "", root
        root = os.path.abspath(root)
        sub = os.listdir(root)
        for s in sub:
            fold = os.path.join(root, s)
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
        warnings.warn("unable to find any folder in: " + root)
    return maps
