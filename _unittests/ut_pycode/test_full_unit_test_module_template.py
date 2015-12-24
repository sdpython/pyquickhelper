"""
@brief      test log(time=80s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import shutil
import warnings
from docutils.parsers.rst import roles

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

from src.pyquickhelper.loghelper.flog import fLOG, download, noLOG
from src.pyquickhelper import get_temp_folder, is_travis_or_appveyor, process_standard_options_for_setup

if sys.version_info[0] == 2:
    from codecs import open


class TestUnitTestFull(unittest.TestCase):

    def test_full_unit_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_full_unit_test")
        url = "https://github.com/sdpython/python3_module_template/archive/master.zip"
        fLOG("download", url)
        download(url, temp)
        assert not os.path.exists(os.path.join(temp, "src"))
        root = os.path.join(temp, "python3_module_template-master")
        setup = os.path.join(root, "setup.py")
        pyq = os.path.join(os.path.dirname(src.pyquickhelper.__file__), "..")

        if "src" in sys.modules:
            memo = sys.modules["src"]
            del sys.modules["src"]
        else:
            memo = None

        def skip_function(name, code):
            return "test_example" not in name

        fLOG("unit tests", root)
        r = process_standard_options_for_setup(
            ["unittests"], setup, "python3_module_template", port=8067,
            requirements=["pyquickhelper"], blog_list="http://blog/",
            fLOG=noLOG, additional_ut_path=[pyq, (root, True)],
            skip_function=skip_function, coverage_options={"disable_coverage": True})

        if memo is not None:
            sys.modules["src"] = memo

        fLOG(r)
        assert r


if __name__ == "__main__":
    unittest.main()
