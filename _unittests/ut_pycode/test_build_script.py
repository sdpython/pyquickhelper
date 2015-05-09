"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import re
import shutil
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

from src.pyquickhelper import fLOG
from src.pyquickhelper.pycode.build_helper import get_build_script, get_script_command, get_extra_script_command


class TestBuilScript(unittest.TestCase):

    def test_build_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.platform.startswith("win"):
            sc = get_build_script("pyquickhelper")
            # fLOG(sc)
            assert "c:\\Python34_x64vir\\install" in sc
            assert "__" not in sc

            scc = get_script_command(
                "unittest", "pyquickhelper", requirements=[])
            assert "setup.py" in scc
            assert "__" not in scc

            sccc = get_extra_script_command(
                "local_pypi", "pyquickhelper", port=8067, requirements=[])
            assert "python" in sccc
            if "__" in sccc:
                raise Exception(sccc)
        else:
            # not yet implemented for this platform
            return

    def test_build_script_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        project_var_name = "pyquickhelper"
        requirements = None
        port = 8067

        if sys.platform.startswith("win"):

            for c in {"build_script", "clean_space",
                      "write_version", "clean_pyd",
                      "build_sphinx", "unittests",
                      "unittests_LONG", "unittests_SKIP",
                      "copy27", "test_local_pypi"}:
                sc = get_script_command(
                    c, project_var_name, requirements=requirements, port=port)
                assert len(sc) > 0
                assert "__" not in sc

            for c in {"notebook", "publish", "publish_doc", "local_pypi", "run27",
                      "build27", "setupdep", "copy_dist",
                      "any_setup_command"}:
                sc = get_extra_script_command(
                    c, project_var_name, requirements=requirements, port=port)
                assert len(sc) > 0
                assert "__" not in sc
                if c == "run27":
                    if "nosetest" not in sc:
                        raise Exception(sc)
        else:
            # not yet implemented for this platform
            return


if __name__ == "__main__":
    unittest.main()
