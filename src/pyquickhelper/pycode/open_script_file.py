"""
@file
@brief A function to read a script and reading the encoding on the first line.
"""
import os


def detect_encoding(filename):
    """
    Guesses the encoding from ``# -*- coding: ...``.

    @param      filename    filename
    @return                 encoding or None
    """
    if isinstance(filename, str) and os.path.exists(filename):
        with open(filename, 'rb') as f:
            enc = f.read(30)
    elif isinstance(filename, bytes):
        enc = filename
    else:
        raise TypeError("Unexpected type %r." % type(filename))
    s = enc.decode("ascii", errors="ignore")
    s = s.replace(" ", "").replace("\r", "")
    d = "#-*-coding:"
    if s.startswith(d):
        s = s[len(d):]
        i = s.find("-*-")
        if i > 0:
            return s[:i]
    return None


def open_script(filename, mode="r"):
    """
    Open a filename but read the encoding from the first line.

    @param      filename        filename
    @param      mode            r, only r
    @return                     stream
    """
    if mode == "r":
        encoding = detect_encoding(filename)
        return open(filename, mode, encoding=encoding)
    raise ValueError(  # pragma: no cover
        "This function only works for mode='r'.")
