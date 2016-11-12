"""
@brief      test log(time=5s)
"""

import sys
import os
import unittest
import warnings


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.ipythonhelper.notebook_helper import read_nb
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.loghelper import fLOG


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookReadWrite (unittest.TestCase):

    def test_notebook_read_write(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # written in Python 3
            return
        temp = get_temp_folder(__file__, "temp_notebook_read_write")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        assert os.path.exists(nbfile)
        # For some reason, if this instruction is included in the build,
        # the travis build completes but never ends.
        # This is removed from the whole list on tavis.
        if is_travis_or_appveyor() == "travis":
            warnings.warn("This test prevents travis from ending. The process never stops.")
            return
        nb = read_nb(nbfile)
        outfile = os.path.join(temp, "out_notebook.ipynb")
        nb.to_json(outfile)
        assert os.path.exists(outfile)

        with open(nbfile, "r", encoding="utf8") as f:
            c1 = f.read().replace("\r", "")
        with open(outfile, "r", encoding="utf8") as f:
            c2 = f.read().replace("\r", "")
        if c1 != c2:
            l1 = c1.strip("\n ").split("\n")
            l2 = c2.strip("\n ").split("\n")
            for i, cc in enumerate(zip(l1, l2)):
                a, b = cc
                if a.strip(" \n") != b.strip(" \n"):
                    raise Exception(
                        "difference at line {0}\n1: [{1}]-[{3}]\n2: [{2}]-[{4}]".format(i, a, b, type(a), type(b)))
            if len(l1) != len(l2):
                raise Exception("different length")


if __name__ == "__main__":
    unittest.main()
