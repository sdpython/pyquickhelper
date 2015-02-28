"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest


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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc


class TestDoxy (unittest.TestCase):

    def test_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.join(path, "data", "session1.py")
        with open(file, "r", encoding="utf8") as f:
            rows = f.readlines()
        res = private_migrating_doxygen_doc(rows, 1, file, debug=False)
        count = {}
        for r in res:
            r = r.strip("\r\n")
            st = len(r) - len(r.lstrip())
            if st == 1:
                fLOG(st, r)
            count[st] = count.get(st, 0) + 1
        del count[0]
        mx = max(count.values())
        mi = max(k for k, v in count.items() if v == mx)
        fLOG(count, mx, mi)

        for r in res:
            r = r.strip("\r\n")
            if r.strip() == "::":
                st = len(r) - len(r.lstrip())
                if st != mi:
                    raise Exception("bad indentation:\n" + "\n".join(res))


if __name__ == "__main__":
    unittest.main()
