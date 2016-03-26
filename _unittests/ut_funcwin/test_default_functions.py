"""
@brief      test log(time=1s)
"""
import os
import sys
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

from src.pyquickhelper.loghelper import fLOG, noLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.funcwin.default_functions import test_regular_expression, is_empty_string, IsEmptyString, file_head, file_grep


class TestWindows (unittest.TestCase):

    def test_test_regular_expression(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        test_regular_expression(fLOG=noLOG)

    def test_is_empty_string(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        assert is_empty_string(None)
        assert is_empty_string("")
        assert not is_empty_string(".")
        assert not IsEmptyString(".")

    def test_file_head(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_" + self._testMethodName)
        out = os.path.join(temp, "out.5.py")
        assert not os.path.exists(out)
        head = file_head(__file__.replace(".pyc", ".py"), out=out, head=5)
        assert os.path.exists(head)

    def test_file_grep(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_" + self._testMethodName)
        out = os.path.join(temp, "out.grep.py")
        assert not os.path.exists(out)
        head = file_grep(
            __file__.replace(
                ".pyc",
                ".py"),
            out=out,
            regex="test_.*")
        assert os.path.exists(head)


if __name__ == "__main__":
    unittest.main()
