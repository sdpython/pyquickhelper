"""
@brief      test log(time=3s)
"""

import sys
import os
import unittest

if sys.version_info[0] == 2:
    from StringIO import StringIO
    from io import BytesIO
else:
    from io import StringIO, BytesIO

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
from src.pyquickhelper.filehelper import read_content_ufs


class TestDownloadContent (unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_read_content_ufs(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        url = "https://raw.githubusercontent.com/sdpython/pyquickhelper/master/src/pyquickhelper/ipythonhelper/magic_parser.py"
        content = read_content_ufs(url, encoding="utf8")
        assert "MagicCommandParser" in content
        assert isinstance(content, str  # unicode#
                          )

        typstr = str  # unicode#

        file = typstr(__file__)
        file_, ext = os.path.splitext(file)
        if ext != ".py":
            file = file_ + ".py"
        content = read_content_ufs(file, encoding="utf8")
        assert "TestDownloadContent" in content

        content2 = read_content_ufs(content, encoding="utf8")
        self.assertEqual(content2, content)

        st = StringIO(content)
        content2 = read_content_ufs(st, encoding="utf8")
        self.assertEqual(content2, content)

        if sys.version_info[0] > 2:
            by = BytesIO(content.encode("utf8"))
            content2 = read_content_ufs(by, encoding="utf8")
            self.assertEqual(content2, content)


if __name__ == "__main__":
    unittest.main()
