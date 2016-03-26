"""
@brief      test tree node (time=5s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode.code_helper import remove_extra_spaces_and_pep8, remove_extra_spaces_folder
from src.pyquickhelper.pycode.clean_helper import clean_exts
from src.pyquickhelper.pycode.ci_helper import is_travis_or_appveyor


class TestClean(unittest.TestCase):

    def test_pep8(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor():
            return

        this = os.path.abspath(__file__.replace(".pyc", ".py"))
        try:
            diff = remove_extra_spaces_and_pep8(this)
        except IndexError as e:
            warnings.warn("probably an issue with pep8: " + str(e))
        assert diff < 10

    def test_extra_space(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        diff = remove_extra_spaces_folder(this)
        assert isinstance(diff, list)

    def test_clean_exts(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        try:
            diff = clean_exts(this)
        except PermissionError as e:
            if "anaconda" in sys.executable.lower():
                # we disable it for Anaconda
                return
            raise Exception("unable to clean " + this +
                            "\nexe: " + sys.executable) from e
        assert isinstance(diff, list)


if __name__ == "__main__":
    unittest.main()
