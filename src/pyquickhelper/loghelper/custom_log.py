# -*- coding: utf-8 -*-
"""
@file
@brief Creates a custom log (open a text file and flushes everything in it).

.. versionadded:: 1.5
"""
import datetime
import sys
import os


if sys.version_info[0] == 2:
    from codecs import open


class CustomLog:
    """
    Implements a custom logging function.
    This class is not protected against multithreading.
    Usage:

    ::

        clog = CustomLog("folder")
        clog('[fct]', info)
    """

    def __init__(self, folder=None, filename=None, create=True, parent=None):
        """
        initialisation

        @param      folder          folder (created if not exists)
        @param      filename        new filename
        @param      create          force the creation
        @param      parent          logging function (called after this one if not None)
        """
        folder = os.path.abspath(folder)
        self._folder = folder
        self._parent = parent
        if not os.path.exists(folder):
            os.makedirs(folder)
        typstr = str  # unicode#
        if filename is None:
            i = 0
            filename = "log_custom_%03d.txt" % i
            fullpath = os.path.join(folder, filename)
            while os.path.exists(fullpath):
                i += 1
                filename = "custom_log_%03d.txt" % i
                fullpath = os.path.join(folder, filename)
            self._filename = filename
            self._fullpath = fullpath
            self._handle = open(self._fullpath, "w", encoding="utf-8")
            self._close = True
        elif isinstance(filename, typstr):
            self._filename = filename
            self._fullpath = os.path.join(folder, filename)
            self._handle = open(self._fullpath, "w", encoding="utf-8")
            self._close = True
        else:
            self._handle = filename
            self._close = False
            self._filename = None
            self._fullpath = None

    @property
    def filename(self):
        """
        returns *_filename*
        """
        return self._filename

    @property
    def fullpath(self):
        """
        returns *_fullpath*
        """
        return self._fullpath

    def __del__(self):
        """
        Closes the stream if needed.
        """
        if self._close:
            self._handle.close()

    def __call__(self, *l, **p):
        """
        Log anything.
        """
        self.fLOG(*l, **p)
        if self._parent is not None:
            self._parent(*l, **p)

    def fLOG(self, *l, **p):
        """
        Builds a message on a single line with the date, it deals with encoding issues.

        @param      l       list of fields
        @param      p       dictionary of fields
        """
        dt = datetime.datetime(2009, 1, 1).now()
        typstr = str  # unicode#
        if len(l) > 0:
            if sys.version_info[0] == 2:
                def _str_process(s):
                    if isinstance(s, str  # unicode#
                                  ):
                        return s
                    elif isinstance(s, bytes):
                        return s.decode("utf8")
                    else:
                        try:
                            return typstr(s)
                        except Exception as e:
                            raise Exception(
                                "unable to convert s into string: type(s)=" + typstr(type(s))) from e
                try:
                    message = typstr(dt).split(
                        ".")[0] + " " + " ".join([_str_process(s) for s in l]) + "\n"
                except UnicodeDecodeError:
                    message = "ENCODING ERROR WITH Python 2.7, will not fix it"
            else:
                def _str_process(s):
                    if isinstance(s, str):
                        return s
                    elif isinstance(s, bytes):
                        return s.decode("utf8")
                    else:
                        try:
                            return str(s)
                        except Exception as e:
                            raise Exception(
                                "unable to convert s into string: type(s)=" + str(type(s))) from e

                message = str(dt).split(
                    ".")[0] + " " + " ".join([_str_process(s) for s in l]) + "\n"

            self._handle.write(message)
            st = "                    "
        else:
            st = typstr(dt).split(".")[0] + " "

        for k, v in p.items():
            message = st + \
                "%s = %s%s" % (
                    typstr(k), typstr(v), "\n")
            if "INNER JOIN" in message:
                break
            self._handle.write(message)
        self._handle.flush()
