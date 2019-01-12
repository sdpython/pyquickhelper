"""
@brief      test tree node (time=50s)
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode.venv_helper import check_readme_syntax


class TestReadme(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_venv_docutils08_readme(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "..", "..", "README.rst")
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()

        assert len(content) > 0

        temp = get_temp_folder(__file__, "temp_readme")

        if __name__ != "__main__":
            # does not work from a virtual environment
            return

        check_readme_syntax(readme, folder=temp, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
