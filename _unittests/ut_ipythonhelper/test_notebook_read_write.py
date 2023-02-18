"""
@brief      test log(time=5s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper.notebook_helper import read_nb
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from pyquickhelper.loghelper import fLOG


class TestNotebookReadWrite (unittest.TestCase):

    def test_notebook_read_write(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_read_write")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        self.assertTrue(os.path.exists(nbfile))
        # For some reason, if this instruction is included in the build,
        # the travis build completes but never ends.
        # This is removed from the whole list on tavis.
        if is_travis_or_appveyor() == "travis":
            # This test prevents travis from ending. The process never stops.
            return
        nb = read_nb(nbfile, kernel=False)
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
                    raise AssertionError(
                        f"difference at line {i}\n1: [{a}]-[{type(a)}]\n2: [{b}]-[{type(b)}]")
            if len(l1) != len(l2):
                raise AssertionError("different length")

    def test_notebook_to_python(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_topython")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        self.assertTrue(os.path.exists(nbfile))
        # For some reason, if this instruction is included in the build,
        # the travis build completes but never ends.
        # This is removed from the whole list on tavis.
        if is_travis_or_appveyor() == "travis":
            # "This test prevents travis from ending. The process never stops.
            return
        nb = read_nb(nbfile, kernel=False)
        outfile = os.path.join(temp, "out_notebook.py")
        code = nb.to_python()
        self.assertTrue(len(code) > 0)
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(code)


if __name__ == "__main__":
    unittest.main()
