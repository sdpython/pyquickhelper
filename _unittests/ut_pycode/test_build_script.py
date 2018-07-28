"""
@brief      test tree node (time=2s)
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

from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode.build_helper import get_build_script, get_script_command, get_extra_script_command, _default_nofolder
from src.pyquickhelper.pycode.setup_helper import write_pyproj


class TestBuildScript(unittest.TestCase):

    def test_build_script(self):
        if sys.platform.startswith("win") and sys.version_info[0] != 2:
            sc = get_build_script("pyquickhelper")
            lines = sc.split("\n")
            for line in lines:
                if "__" in line and _default_nofolder not in line:
                    raise Exception("issue with '__' in:\n" +
                                    line + "\nFULL\n" + sc)

            scc = get_script_command(
                "unittest", "pyquickhelper", requirements=[])
            self.assertIn("setup.py", scc)
            self.assertNotIn("__", scc)

            sccc = get_extra_script_command(
                "local_pypi", "pyquickhelper", port=8067, requirements=[])
            self.assertIn("python", sccc)
            if "__" in sccc:
                raise Exception("'__' not in script\n" + sccc)
        else:
            # not yet implemented for this platform
            return

    def test_build_script_all(self):
        project_var_name = "pyquickhelper"
        requirements = None
        port = 8067

        if sys.platform.startswith("win"):

            for c in ("build_script", "clean_space",
                      "write_version", "clean_pyd",
                      "build_sphinx", "unittests",
                      "unittests_LONG", "unittests_SKIP",
                      "copy27", "test_local_pypi",
                      "setup_hook", "unittests_GUI"):
                sc = get_script_command(
                    c, project_var_name, requirements=requirements, port=port)
                self.assertTrue(len(sc) > 0)
                if "__" in sc:
                    if sys.version_info[0] == 2:
                        continue
                    raise Exception(
                        "'__' in script\n{0}\n----------\n{1}".format(c, sc))

            unit_test_folder = os.path.abspath(
                os.path.join(os.path.dirname(__file__), ".."))
            for c in {"notebook", "publish", "publish_doc", "local_pypi",
                      "setupdep", "copy_dist",
                      "any_setup_command", "build_dist"}:
                sc = get_extra_script_command(
                    c, project_var_name, requirements=requirements, port=port,
                    unit_test_folder=unit_test_folder)
                self.assertTrue(len(sc) > 0)
                if "__" in sc:
                    if sys.version_info[0] == 2:
                        continue
                    raise Exception(
                        c + "\n\n" + "\n__##__##__##__\n".join(sc.split("__")))
                if c == "run27":
                    if sys.version_info[0] == 2:
                        continue
                    if "nosetest" not in sc:
                        raise Exception(sc)
        else:
            # not yet implemented for this platform
            return

    @unittest.skipIf(sys.version_info[0] == 2, reason="not available on Python 2")
    def test_build_pyproj(self):
        temp = get_temp_folder(__file__, "temp_pyproj")
        root = os.path.normpath(os.path.join(temp, "..", "..", ".."))

        write_pyproj(root, temp)

        with open(os.path.join(temp, "ptvs_project.pyproj"), "r", encoding="utf8") as f:
            content = f.read()
        if "build\\" in content:
            raise Exception(content)
        if "setup_helper.py" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
