"""
@brief      test log(time=8s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.helpgen import latex2rst


if sys.version_info[0] == 2:
    from codecs import open


class TestPandocHelper(unittest.TestCase):

    def test_latex2rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if is_travis_or_appveyor():
            warnings.warn("unable to test it due to pandoc")
            return
        temp = get_temp_folder(__file__, "temp_latex2rst")
        data = os.path.join(temp, "..", "data", "chap9_thread.tex")
        output = os.path.join(temp, "chap9_thread.rst")
        temp_file = os.path.join(temp, "chap_utf8.tex")
        out, err = latex2rst(data, output, encoding="latin-1",
                             fLOG=fLOG, temp_file=temp_file)
        assert os.path.exists(output)

if __name__ == "__main__":
    unittest.main()
