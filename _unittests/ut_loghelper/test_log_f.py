"""
@brief      test log(time=1s)
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


from src.pyquickhelper.loghelper import fLOG, fLOGFormat


class TestLogFuncFormat (unittest.TestCase):

    def test_log_format(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = fLOGFormat("\n", [4, 5], {3: 4})
        assert res.endswith(" [4, 5] {3: 4}\n")


if __name__ == "__main__":
    unittest.main()
