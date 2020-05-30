"""
@file
@brief Buffer as a logging function.
"""
from io import StringIO


class BufferedPrint:
    """
    Buffered display. Relies on :epkg:`*py:io:StringIO`.
    Use it as follows:

    .. runpython::
        :showcode:

        def do_something(fLOG=None):
            if fLOG:
                fLOG("Did something.")
            return 3

        from pyquickhelper.loghelper import BufferedPrint
        buf = BufferedPrint()
        do_something(fLOG=buf.fprint)
        print(buf)
    """

    def __init__(self):
        "constructor"
        self.buffer = StringIO()

    def fprint(self, *args, **kwargs):
        "print function"
        mes = " ".join(str(_) for _ in args)
        self.buffer.write(mes)
        self.buffer.write("\n")

    def __str__(self):
        "Returns the content."
        return self.buffer.getvalue()
