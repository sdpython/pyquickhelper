"""
@brief      test log(time=10s)

notebook test
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
from src.pyquickhelper.pycode import is_travis_or_appveyor
from src.pyquickhelper.ipythonhelper import install_python_kernel_for_unittest
from src.pyquickhelper.ipythonhelper import execute_notebook_list


class TestCacheUrls(unittest.TestCase):

    def test_cache_urls(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # notebooks are not converted into python 2.7, so not tested
            return

        kernel_name = None if is_travis_or_appveyor() is not None else install_python_kernel_for_unittest(
            "pyquickhelper")

        temp = get_temp_folder(__file__, "temp_cache_urls")

        fnb = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "_doc", "notebooks"))
        keepnote = [os.path.join(fnb, "example_about_files.ipynb")]

        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src"))]

        res = execute_notebook_list(
            temp, keepnote, fLOG=fLOG, valid=None, additional_path=addpaths, kernel_name=kernel_name,
            cache_urls=["https://docs.python.org/3.4/library/urllib.request.html"])

        assert len(res) > 0
        fails = [(os.path.split(k)[-1], v)
                 for k, v in sorted(res.items()) if not v[0]]
        for f in fails:
            fLOG(f)
        for k, v in sorted(res.items()):
            name = os.path.split(k)[-1]
            fLOG(name, v[0], v[1])
        if len(fails) > 0:
            raise fails[0][1][-1]


if __name__ == "__main__":
    unittest.main()
