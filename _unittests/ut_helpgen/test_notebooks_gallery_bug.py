"""
@brief      test log(time=15s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen.sphinx_main import build_notebooks_gallery
from src.pyquickhelper.pycode import get_temp_folder


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookGalleryBug(unittest.TestCase):

    def test_notebook_gallery_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        temp = get_temp_folder(__file__, "temp_gallery_bug")
        fold = os.path.normpath(os.path.join(
            temp, "..", "notebooks_js"))
        assert os.path.exists(fold)

        file = os.path.join(temp, "all_notebooks.rst")
        build_notebooks_gallery(fold, file, fLOG=fLOG)
        if not os.path.exists(file):
            raise FileNotFoundError(file)

        with open(file, "r", encoding="utf8") as f:
            text = f.read()

        if "GitHub/pyquickhelper" in text.replace("\\", "/"):
            raise Exception(text)
        spl = text.split("using_qgrid_with_jsdf")
        if len(spl) != 3:
            raise Exception(text)


if __name__ == "__main__":
    unittest.main()
