"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

if sys.version_info[0] == 2:
    from StringIO import StringIO
    BytesIO = StringIO
else:
    from io import StringIO, BytesIO

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


class TestAnyFHelper(unittest.TestCase):

    def test_read_content(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(__file__)
        ext = os.path.splitext(this)[-1]
        if ext != ".py":
            this = this.replace(ext, ".py")

        content1 = read_content_ufs(this)
        content2, source = read_content_ufs(this, add_source=True)
        self.assertEqual(content1, content2)
        if sys.version_info[0] != 2:
            warnings.warn("source is not reliable on Python 2.7")
            self.assertEqual(source, "r")
        content0 = content1

        content3, source = read_content_ufs(content1, add_source=True)
        self.assertEqual(content1, content3)
        if sys.version_info[0] != 2:
            self.assertEqual(source, "s")

        content4, source = read_content_ufs(
            StringIO(content1), add_source=True)
        self.assertEqual(content4, content1)
        if sys.version_info[0] != 2:
            self.assertEqual(source, "S")

        content4, source = read_content_ufs(
            BytesIO(content1.encode("utf-8")), add_source=True)
        self.assertEqual(content4, content1)
        if sys.version_info[0] != 2:
            self.assertEqual(source, "SB")

        # asbytes
        if sys.version_info[0] == 2:
            warnings.warn("read_content_ufs not tested for bytes on Python 2.7")
            return

        content1 = read_content_ufs(this, asbytes=True)
        content2, source = read_content_ufs(
            this, add_source=True, asbytes=True)
        self.assertEqual(content1, content2)
        self.assertEqual(source, "rb")
        self.assertEqual(type(content1), bytes)

        content3, source = read_content_ufs(
            content1, add_source=True, asbytes=True)
        self.assertEqual(content1, content3)
        self.assertEqual(source, "b")

        content4, source = read_content_ufs(
            StringIO(content0), add_source=True, asbytes=True)
        self.assertEqual(source, "Sb")
        content1 = content1.replace(b'\r', b'')
        if content4 != content1:
            raise Exception("\n{0}\n{1}".format(content4, content1))

        content4, source = read_content_ufs(
            BytesIO(content0.encode("utf-8")), add_source=True, asbytes=True)
        if content4 != content1:
            raise Exception("\n{0}\n{1}".format(content4, content1))
        self.assertEqual(source, "SBb")


if __name__ == "__main__":
    unittest.main()
