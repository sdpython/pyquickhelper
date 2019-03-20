"""
@brief      test log(time=10s)

notebook test
"""

import sys
import os
import unittest

import pyquickhelper
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.pycode import is_travis_or_appveyor
from pyquickhelper.ipythonhelper import execute_notebook_list, execute_notebook_list_finalize_ut


class TestCacheUrls(unittest.TestCase):

    def test_cache_urls(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_cache_urls")

        fnb = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "_doc", "notebooks"))
        keepnote = [os.path.join(fnb, "example_about_files.ipynb")]

        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src"))]

        res = execute_notebook_list(
            temp, keepnote, fLOG=fLOG, valid=None, additional_path=addpaths,
            cache_urls=["https://docs.python.org/3.4/library/urllib.request.html"])
        execute_notebook_list_finalize_ut(
            res, fLOG=fLOG, dump=pyquickhelper)


if __name__ == "__main__":
    unittest.main()
