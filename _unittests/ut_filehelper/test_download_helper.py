"""
@brief      test log(time=5s)
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

from src.pyquickhelper import fLOG
from src.pyquickhelper.filehelper import get_url_content_timeout, InternetException


class TestDownloadHelper(unittest.TestCase):

    def test_download_notimeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        url = "https://raw.githubusercontent.com/sdpython/pyquickhelper/master/src/pyquickhelper/ipythonhelper/magic_parser.py"
        content = get_url_content_timeout(url, encoding="utf8")
        assert "MagicCommandParser" in content
        assert isinstance(content, str  # unicode#
                          )

    def test_download_timeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        url = "https://localhost:878777/should_not_exists"
        try:
            content = get_url_content_timeout(url, encoding="utf8", timeout=2)
        except InternetException:
            return

        assert False


if __name__ == "__main__":
    unittest.main()
