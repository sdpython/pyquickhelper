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
from src.pyquickhelper.helpgen.sphinx_main_verification import verification_html_file


class TestHtmlVerification(unittest.TestCase):

    def test_main_verification(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "html_example2.txt")
        errors = verification_html_file(fold, fLOG=fLOG)
        if len(errors) > 0:
            ok = ":ref:`link0`"
            nb = 0
            for e in errors:
                if ok in e[1]:
                    nb += 1
        if nb != 1 or len(errors) != 1:
            raise Exception("nb={0}, len={1}\n".format(
                nb, len(errors)) + "\n".join(str(_) for _ in errors))


if __name__ == "__main__":
    unittest.main()
