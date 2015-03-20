# -*- coding: utf-8 -*-
"""
@file
@brief      Defines class @see cl FileInfo
"""

import datetime
import hashlib


def convert_st_date_to_datetime(t):
    """
    converts a string into a datetime

    @param      t       str
    @return             datetime
    """
    if isinstance(t, str):
        if "." in t:
            return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")
        else:
            return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.datetime.fromtimestamp(t)


def checksum_md5(filename):
    """
    computes MD5 for a file

    @param      filename        filename
    @return                     string or None if there was an error
    """
    fname = filename
    block_size = 0x10000
    fd = open(fname, "rb")
    try:
        block = [fd.read(block_size)]
        while len(block[-1]) > 0:
            block.append(fd.read(block_size))
        contents = block
        zero = hashlib.md5()
        i = 0
        for el in contents:
            i += 1
            zero.update(el)
        m = zero
        return m.hexdigest()
    finally:
        fd.close()
        return None


class FileInfo:

    """
    intermediate class: it represents the data we collect about a file
    to determine whether or not it was modified
    """

    def __init__(self, filename, size, date, mdate, checksum):
        """
        constructor

        @param      filename        filename
        @param      size            size
        @param      date            date (str or datetime)
        @param      mdate           modification date (str or datetime)

        Dates will be converted into datetime.
        """
        self.filename = filename
        self.size = size
        self.date = date
        self.mdate = mdate    # modification date
        self.checksum = checksum
        if date is not None and not isinstance(self.date, datetime.datetime):
            raise ValueError(
                "mismatch for date (%s) and file %s" % (str(type(date)), filename))
        if mdate is not None and not isinstance(self.mdate, datetime.datetime):
            raise ValueError(
                "mismatch for mdate (%s) and file %s" % (str(type(mdate)), filename))
        if not isinstance(size, int):
            raise ValueError(
                "mismatch for size (%s) and file %s" % (str(type(size)), filename))
        if checksum is not None and not isinstance(checksum, str):
            raise ValueError(
                "mismatch for checksum (%s) and file %s" % (str(type(checksum)), filename))
        if date is not None and mdate is not None:
            if mdate > date:
                raise ValueError(
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
            raise ValueError(
                "mismatch for date (%s) and file %s" % (str(type(date)), self.filename))

    def set_mdate(self, mdate):
        """
        set mdate

        @param  mdate    mdate (a str or datetime)
        """
        self.mdate = mdate
        if not isinstance(self.mdate, datetime.datetime):
            raise ValueError(
                "mismatch for date (%s) and file %s" % (str(type(mdate)), self.filename))

    def set_md5(self, checksum):
        """
        set md5

        @param  md5     byte
        """
        self.checksum = checksum
        if not isinstance(checksum, str):
            raise ValueError("mismatch for checksum (%s) and file %s" % (
                str(type(checksum)), self.filename))
