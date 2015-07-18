# -*- coding: utf-8 -*-
"""
@file
@brief Function to verify the files produced by Sphinx

"""
import os
import re
import warnings
from ..loghelper.flog import noLOG
from ..filehelper.synchelper import explore_folder_iterfile


class SphinxVerificationException(Exception):

    """
    to format the error message
    """

    def __init__(self, errors):
        """
        @param      file        filename
        @param      line        line
        """
        stack = []
        for name, line, m in errors:
            message = '[SPHINX-ERROR] {2}\n  File "{0}", line {1}'.format(
                name, line + 1, m)
            stack.append(message)
        Exception.__init__(self, "\n" + "\n".join(stack))


def verification_html_format(folder, fLOG=noLOG, raise_above=0.1):
    """
    dig into folders abd subfolders to find HTML files
    produced by Sphinx, does some verification to detect errors,
    the function, the function raises an exception for all mistakes

    @param      folder          folder to verifiy
    @param      fLOG            logging function
    @param      raise_above     raises an exception of the number of errors is above a given threshold
                                or a relative threshold if it is a float
    @return                     list of errors
    """
    nbfile = 0
    errors = []
    for item in explore_folder_iterfile(folder, ".[.]html", fullname=True):
        fLOG("[verification_html_format]", item)
        err = verification_html_file(item, fLOG=fLOG)
        errors.extend([(os.path.abspath(item), line, m) for line, m in err])
        nbfile += 1
    fLOG("[verification_html_format] checked:{0} errors:{1}".format(
        nbfile, len(errors)))
    if len(errors) > 0:
        e = SphinxVerificationException(errors)
        if isinstance(raise_above, int) and len(errors) >= raise_above:
            raise e
        elif len(errors) * 1.0 / nbfile >= raise_above:
            raise e
        else:
            warnings.warn(str(e))
    return errors


def verification_html_file(item, fLOG=noLOG):
    """
    verifies a file produced by Sphinx and checks basic mistakes

    @param      item        filename
    @param      fLOG        logging function
    @return                 list of errors (line, message)

    The first line is 0.
    """
    with open(item, "r", encoding="utf8") as f:
        lines = f.readlines()

    reg = re.compile("([.][.] _[-a-z_A-Z0-9][:.])")

    errors = []
    for i, line in enumerate(lines):
        if "<h1>Source code for " in line or "<h1>Code source de " in line:
            # no need to go further
            # the source takes place after this substring
            break
        if ":ref:`" in line:
            errors.append((i, "wrong :ref:` in " + line.strip("\n\r ")))
        if ":func:`" in line:
            errors.append((i, "wrong :func:` in " + line.strip("\n\r ")))
        if ":class:`" in line:
            errors.append((i, "wrong :class:` in " + line.strip("\n\r ")))
        if ":meth:`" in line:
            errors.append((i, "wrong :meth:` in " + line.strip("\n\r ")))
        if ":method:`" in line:
            errors.append((i, "wrong :method:` in " + line.strip("\n\r ")))
        if ">`" in line:
            errors.append((i, "wrong >`, missing _ in " + line.strip("\n\r ")))
        find = reg.findall(line)
        if len(find) > 0:
            errors.append(
                (i, "label or index remaining: " + str(find) + " in " + line.strip("\n\r ")))

    return errors
