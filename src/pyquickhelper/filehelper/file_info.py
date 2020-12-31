# -*- coding: utf-8 -*-
"""
@file
@brief      Defines class @see cl FileInfo
"""
import datetime
import hashlib
import re
import urllib.parse as urlparse


def convert_st_date_to_datetime(t):
    """
    Converts a string into a datetime.

    @param      t       str
    @return             datetime
    """
    if isinstance(t, str):
        if "." in t:
            return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    return datetime.datetime.fromtimestamp(t)


def checksum_md5(filename):
    """
    Computes MD5 for a file.

    @param      filename        filename
    @return                     string
    """
    fname = filename
    block_size = 0x10000
    zero = hashlib.md5()
    with open(fname, "rb") as fd:
        block = [fd.read(block_size)]
        while len(block[-1]) > 0:
            block.append(fd.read(block_size))
        for el in block:
            zero.update(el)
        return zero.hexdigest()


_allowed = re.compile("^([a-zA-Z]:)?[^:*?\"<>|]+$")


def is_file_string(s):
    """
    Tells if the string *s* could be a filename.

    @param      s       string
    @return             boolean
    """
    if len(s) >= 5000:
        return False  # pragma: no cover
    global _allowed
    if not _allowed.search(s):
        return False
    for c in s:
        if ord(c) < 32:
            return False
    return True


def is_url_string(s):
    """
    Tells if the string s could be a url.

    @param      s       string
    @return             boolean
    """
    if "\n" in s:
        return False
    sch = urlparse.urlparse(s)
    if len(sch.scheme) > 10:
        return False  # pragma: no cover
    return sch.scheme.lower() not in ("", None, "warning")


class FileInfo:

    """
    Intermediate class: it represents the data it collects about a file
    to determine whether or not it was modified.
    """

    def __init__(self, filename, size, date, mdate, checksum):
        """
        @param      filename        filename
        @param      size            size
        @param      date            date (str or datetime)
        @param      mdate           modification date (str or datetime)
        @param      checksum        to check the file was modified

        Dates will be converted into datetime.
        """
        self.filename = filename
        self.size = size
        self.date = date
        self.mdate = mdate    # modification date
        self.checksum = checksum
        if date is not None and not isinstance(self.date, datetime.datetime):
            raise ValueError(  # pragma: no cover
                "mismatch for date (%s) and file %s" % (str(type(date)), filename))
        if mdate is not None and not isinstance(self.mdate, datetime.datetime):
            raise ValueError(  # pragma: no cover
                "mismatch for mdate (%s) and file %s" % (str(type(mdate)), filename))
        if not isinstance(size, int):
            raise ValueError(  # pragma: no cover
                "mismatch for size (%s) and file %s" % (str(type(size)), filename))
        if checksum is not None and not isinstance(checksum, str):
            raise ValueError(  # pragma: no cover
                "mismatch for checksum (%s) and file %s" % (str(type(checksum)), filename))
        if date is not None and mdate is not None:
            if mdate > date:
                raise ValueError(  # pragma: no cover
                    "expecting mdate <= date for file " + filename)

    def __str__(self):
        """
        usual
        """
        return "File[name=%s, size=%d (%s), mdate=%s (%s), date=%s (%s), md5=%s (%s)]" % \
            (self.filename,
             self.size, str(type(self.size)),
             str(self.mdate), str(type(self.mdate)),
             str(self.date), str(type(self.date)),
             self.checksum, str(type(self.checksum)))

    def set_date(self, date):
        """
        set date

        @param  date    date (a str or datetime)
        """
        self.date = date
        if not isinstance(self.date, datetime.datetime):
            raise ValueError(  # pragma: no cover
                "mismatch for date (%s) and file %s" % (str(type(date)), self.filename))

    def set_mdate(self, mdate):
        """
        set mdate

        @param  mdate    mdate (a str or datetime)
        """
        self.mdate = mdate
        if not isinstance(self.mdate, datetime.datetime):
            raise ValueError(  # pragma: no cover
                "mismatch for date (%s) and file %s" % (str(type(mdate)), self.filename))

    def set_md5(self, checksum):
        """
        set md5

        @param  checksum     checksum
        """
        self.checksum = checksum
        if not isinstance(checksum, str):
            raise ValueError(  # pragma: no cover
                "mismatch for checksum (%s) and file %s" % (
                    str(type(checksum)), self.filename))
