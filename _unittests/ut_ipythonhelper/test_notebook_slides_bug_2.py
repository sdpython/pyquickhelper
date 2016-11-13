"""
@brief      test log(time=13s)
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

from src.pyquickhelper.ipythonhelper.notebook_helper import read_nb
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen import nb2slides


class TestNotebookSlidesBug2 (unittest.TestCase):

    def test_notebook_add_slides_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_add_slides_bug2")
        nbfile = os.path.join(
            temp, "..", "data", "simple_example_bis.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile, kernel=False)
        assert len(nb) > 0
        nb2slides(nbfile, os.path.join(temp, "ooooo.html"))


if __name__ == "__main__":
    unittest.main()
