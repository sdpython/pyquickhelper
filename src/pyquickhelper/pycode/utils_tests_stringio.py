"""
@file
@brief A :epkg:`*py:io:StringIO` which also outputs its content for a file.
"""
import os
from io import StringIO


class StringIOAndFile(StringIO):
    """
    Overloads a StringIO to also writes in a file.
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
        self.redirect = {}
        self.to = None

    def write(self, s):
        """
        Appends a string.

        @param   s      add a string to the stream
        @return         self
        """
        if self.to is not None:
            self.redirect[self.to].write(s)
        else:
            StringIO.write(self, s)
        if not self.handle:
            self.handle = open(self.filename, "w",
                               encoding="utf-8", errors="ignore")
        self.handle.write(s)
        self.handle.flush()
        return self

    def flush(self):
        """
        Calls two flush.
        """
        StringIO.flush(self)
        if self.handle:
            self.handle.flush()

    def close(self):
        """
        Calls two close.
        """
        StringIO.close(self)
        if self.handle:
            self.handle.close()

    def begin_test(self, name):
        """
        Redirects output to a :epkg:`*py:io:StringIO`.

        @param      name        name
        """
        if self.to is not None:
            raise Exception(  # pragma: no cover
                "A test has not finished: '{0}'".format(self.to))
        if name is None:
            raise ValueError(  # pragma: no cover
                "name is None")
        self.to = name
        self.redirect[name] = StringIO()

    def end_test(self, name):
        """
        Ends the redirection.

        @param      name        name
        """
        if name != self.to:
            raise ValueError(  # pragma: no cover
                "Inconsistency in test name '{0}' != '{1}'".format(
                    name, self.to))
        self.to = None

    def getvalue(self):
        """
        Returns the content of the buffer.
        """
        if self.to is not None:
            return self.redirect[self.to].getvalue()
        return StringIO.getvalue(self)
