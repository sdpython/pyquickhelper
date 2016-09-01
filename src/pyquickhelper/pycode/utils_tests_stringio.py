"""
@file
@brief A StringIO which also outputs its content for a file.

.. versionadded:: 1.4
"""
import os
import sys

if sys.version_info[0] == 2:
    from StringIO import StringIO
    from codecs import open
else:
    from io import StringIO


class StringIOAndFile(StringIO):
    """
    overload a StringIO to also write in a file
    """

    def __init__(self, filename):
        """
        constructor

        @param      filename        filename
        """
        StringIO.__init__(self)
        self.filename = filename
        if os.path.exists(filename):
            os.remove(filename)
        self.handle = None

    def write(self, s):
        """
        @param   s      add a string to the stream
        @return         self
        """
        StringIO.write(self, s)
        if not self.handle:
            self.handle = open(self.filename, "w",
                               encoding="utf-8", errors="ignore")
        self.handle.write(s)
        self.handle.flush()
        return self

    def flush(self):
        """
        calls two flush
        """
        StringIO.flush(self)
        if self.handle:
            self.handle.flush()

    def close(self):
        """
        calls two close
        """
        StringIO.close(self)
        if self.handle:
            self.handle.close()
