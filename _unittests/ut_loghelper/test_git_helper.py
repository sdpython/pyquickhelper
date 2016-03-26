"""
@brief      test log(time=42s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

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

from src.pyquickhelper.loghelper import fLOG, removedirs
from src.pyquickhelper.filehelper import change_file_status
from src.pyquickhelper.loghelper.repositories.pygit_helper import clone, rebase
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestGit(unittest.TestCase):

    def test_clone_repo(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        fold = os.path.abspath(os.path.split(__file__)[0])
        temp = os.path.join(fold, "temp_clone_repo")
        if os.path.exists(temp):
            removedirs(temp, use_command_line=True)
        if not os.path.exists(temp):
            os.mkdir(temp)

        if is_travis_or_appveyor() is not None:
            return

        to = os.path.join(temp, "pq")
        out, err = clone(to, "github.com", "sdpython", "pyquickhelper")
        fLOG("OUT:", out)
        fLOG("ERR:", err)
        assert "Cloning into" in err
        assert os.path.exists(
            os.path.join(
                to,
                "src",
                "pyquickhelper",
                "__init__.py"))

        out, err = rebase(to, "github.com", "sdpython", "pyquickhelper")
        fLOG("OUT:", out)
        fLOG("ERR:", err)

        r = change_file_status(temp)
        assert len(r) > 0


if __name__ == "__main__":
    unittest.main()
