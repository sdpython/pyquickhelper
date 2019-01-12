"""
@file
@brief A function to read a script and reading the encoding on the first line.
"""


def detect_encoding(filename):
    """
    guess the encoding from ``# -*- coding: ...``

    @param      filename    filename
    @return                 encoding or None
    """
    with open(filename, 'rb') as f:
        enc = f.read(30)
    s = enc.decode("ascii", errors="ignore").replace(" ", "").replace("\r", "")
    d = "#-*-coding:"
    if s.startswith(d):
        s = s[len(d):]
        i = s.find("-*-")
        if i > 0:
            return s[:i]
    return None


def open_script(filename, mode="r"):
    """
    open a filename but read the encoding from the first line

    @param      filename        filename
    @param      mode            r, only r
    @return                     stream
    """
    if mode == "r":
        encoding = detect_encoding(filename)
        return open(filename, mode, encoding=encoding)
    else:
        raise ValueError("this function only works for mode='r'")
