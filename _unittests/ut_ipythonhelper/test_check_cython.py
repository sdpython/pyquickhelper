"""
@brief      test log(time=1s)

notebook test
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.ipythonhelper import ipython_cython_extension
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestCheckCython(unittest.TestCase):

    def test_ipython_cython_extension(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2 or "condavir" in sys.executable:
            return

        if is_travis_or_appveyor() == "appveyor":
            # We skip that as it would imply
            # we modify the pyhon distribution.
            return

        if sys.version_info[:2] <= (3, 4):
            ipython_cython_extension()


if __name__ == "__main__":
    unittest.main()
