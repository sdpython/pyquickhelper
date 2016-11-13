"""
@brief      test log(time=9s)
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
from src.pyquickhelper.helpgen import nb2present


class TestNotebookPresent(unittest.TestCase):

    def test_notebook_present(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_present")
        nbfile = os.path.join(
            temp, "..", "data", "simple_example_bis.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile, kernel=False)
        assert len(nb) > 0
        output = os.path.join(temp, "ooooo.html")
        nb2present(nbfile, output)
        assert os.path.exists(output)
        content = nb2present(nbfile, None)
        if isinstance(content, list):
            content = content[0]
        if len(content) < 1000:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
