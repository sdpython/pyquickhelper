"""
@brief      test log(time=6s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import ExtTestCase, get_temp_folder
from src.pyquickhelper.filehelper import get_url_content_timeout, InternetException


class TestDownloadHelper(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_download_notimeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # issue with timeout for python 2.7
            return

        url = "https://raw.githubusercontent.com/sdpython/pyquickhelper/master/src/pyquickhelper/ipythonhelper/magic_parser.py"
        content = get_url_content_timeout(url, encoding="utf8")
        self.assertIn("MagicCommandParser", content)
        self.assertIsInstance(content, str  # unicode#
                              )

    def test_download_notimeout_chunk(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # issue with timeout for python 2.7
            return

        temp = get_temp_folder(__file__, "temp_download_notimeout_chunk")
        url = "https://raw.githubusercontent.com/sdpython/pyquickhelper/master/src/pyquickhelper/ipythonhelper/magic_parser.py"
        self.assertRaise(lambda: get_url_content_timeout(
            url, encoding="utf8", chunk=100), ValueError)
        name = os.path.join(temp, "m.py")
        content = get_url_content_timeout(
            url, encoding="utf8", chunk=100, output=name)
        with open(name, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("MagicCommandParser", content)
        self.assertIsInstance(content, str  # unicode#
                              )

        self.assertRaise(lambda: get_url_content_timeout(
            url, chunk=100), ValueError)
        name = os.path.join(temp, "m2.py")
        content = get_url_content_timeout(url, chunk=100, output=name)
        with open(name, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("MagicCommandParser", content)
        self.assertIsInstance(content, str  # unicode#
                              )

    def test_download_timeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # issue with timeout for python 2.7
            return

        url = "https://localhost:878777/should_not_exists"
        try:
            get_url_content_timeout(url, encoding="utf8", timeout=2)
        except InternetException:
            return

        assert False


if __name__ == "__main__":
    unittest.main()
