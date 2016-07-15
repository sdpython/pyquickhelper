"""
@brief      test log(time=3s)
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.funcwin.default_functions import test_regular_expression, file_grep, file_head
from src.pyquickhelper.funcwin.main_window import main_loop_functions


class TestMakeWindow2 (unittest.TestCase):

    def test_file_binary(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        functions = {"test_regular_expression": test_regular_expression,
                     "test_edit_distance": file_grep,
                     "file_head": file_head}
        main_loop_functions(
            functions, title="title: TestMakeWindow2", mainloop=False)


if __name__ == "__main__":
    unittest.main()
