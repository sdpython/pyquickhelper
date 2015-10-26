"""
@brief      test tree node (time=10s)
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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.pycode.build_helper import get_build_script, get_script_command, get_extra_script_command, _default_nofolder
from src.pyquickhelper.pycode.setup_helper import write_pyproj


class TestBuildScript(unittest.TestCase):

    def test_build_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.platform.startswith("win") and sys.version_info[0] != 2:
            sc = get_build_script("pyquickhelper")
            # fLOG(sc)
            ver = "%d%s" % sys.version_info[:2]
            if "c:\\Python{0}_x64vir%virtual_env_suffix%\\install".format(
                    ver) not in sc:
                raise Exception(
                    "c:\\Python{0}_x64vir%virtual_env_suffix%\\install".format(ver))
            lines = sc.split("\n")
            for line in lines:
                if "__" in line and _default_nofolder not in line:
                    raise Exception("issue with __ in:\n" + line)

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
                      "copy27", "test_local_pypi",
                      "setup_hook"}:
                sc = get_script_command(
                    c, project_var_name, requirements=requirements, port=port)
                assert len(sc) > 0
                if "__" in sc:
                    raise Exception(sc)

            unit_test_folder = os.path.abspath(
                os.path.join(os.path.dirname(__file__), ".."))
            for c in {"notebook", "publish", "publish_doc", "local_pypi", "run27",
                      "build27", "setupdep", "copy_dist",
                      "any_setup_command", "build_dist"}:
                sc = get_extra_script_command(
                    c, project_var_name, requirements=requirements, port=port,
                    unit_test_folder=unit_test_folder)
                assert len(sc) > 0
                if "__" in sc:
                    raise Exception(sc)
                if c == "run27":
                    if "nosetest" not in sc:
                        raise Exception(sc)
        else:
            # not yet implemented for this platform
            return

    def test_build_pyproj(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_pyproj")
        root = os.path.normpath(os.path.join(temp, "..", "..", ".."))

        if sys.version_info[0] == 2:
            # not available
            return

        write_pyproj(root, temp)

        with open(os.path.join(temp, "ptvs_project.pyproj"), "r", encoding="utf8") as f:
            content = f.read()
        if "build\\" in content:
            raise Exception(content)
        if "setup_helper.py" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
