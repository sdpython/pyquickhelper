"""
@brief      test log(time=4s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.filehelper import gzip_files, zip_files, zip7_files, download, unzip_files, ungzip_files, un7zip_files, unrar_files
from pyquickhelper.pycode import skipif_travis, skipif_circleci, skipif_appveyor, skipif_linux, skipif_vless, skipif_azure
from pyquickhelper.pycode import is_travis_or_appveyor


class TestCompressHelper(unittest.TestCase):

    def test_compress_helper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        typbytes = bytes
        f = os.path.abspath(__file__).replace(".pyc", ".py")

        rz = zip_files(None, [f], fLOG=fLOG)
        fLOG(len(rz), type(rz))
        if not isinstance(rz, (typbytes, str)):
            raise TypeError(type(rz))

        res = unzip_files(rz)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 1)
        if not isinstance(res[0][1], (typbytes, str)):
            raise TypeError(type(res[0][1]))
        self.assertTrue(res[0][0].endswith(
            "_unittests/ut_filehelper/test_compress_helper.py"))

        # binary
        rg = gzip_files(None, [f], fLOG=fLOG)
        fLOG(len(rg), type(rg))
        if not isinstance(rg, typbytes):
            raise TypeError(type(rg))

        res = ungzip_files(rg)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 1)
        if not isinstance(res[0][1], (typbytes, str)):
            raise TypeError(type(res[0][1]))
        self.assertTrue(res[0][0].endswith(
            "_unittests/ut_filehelper/test_compress_helper.py"))

    def test_compress_helper_text(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        typbytes = bytes
        f = os.path.abspath(__file__).replace(".pyc", ".py")
        rg = gzip_files(None, [f], fLOG=fLOG, encoding="utf-8")
        fLOG(len(rg), type(rg))
        if not isinstance(rg, typbytes):
            raise TypeError(type(rg))

        res = ungzip_files(rg, encoding="utf-8")
        self.assertTrue("test_compress_helper_text" in res)

    @skipif_vless((3, 6), "only available for python 3.6+ (pylzma not compiled)")
    def test_uncompress_7zip(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        import pylzma
        self.assertTrue(pylzma)

        fold = get_temp_folder(__file__, "temp_uncompress_7zip")
        data = os.path.join(fold, "..", "data", "ftplib.7z")
        files = un7zip_files(data, where_to=fold, fLOG=fLOG)
        self.assertEqual(len(files), 1)

    @skipif_linux('py7zlib not available')
    def test_compress_7zip(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = get_temp_folder(__file__, "temp_compress_7zip")
        url = "https://docs.python.org/3/library/ftplib.html"
        f = download(url, fold)

        out7 = os.path.join(fold, "try.7z")
        zip7_files(out7, [f], fLOG=fLOG, temp_folder=fold)
        if not os.path.exists(out7):
            raise FileNotFoundError(out7)

        typbytes = bytes

        if is_travis_or_appveyor() == "appveyor":
            return

        from py7zlib import COMPRESSION_METHOD_COPY
        fLOG("***", COMPRESSION_METHOD_COPY)
        res = un7zip_files(out7)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 1)
        fLOG(res[0][0])
        if not isinstance(res[0][1], (typbytes, str)):
            raise TypeError(type(res[0][1]))
        self.assertTrue(res[0][0].endswith("ftplib.html"))

        fold = get_temp_folder(__file__, "temp_compress_7zip2")
        res = un7zip_files(out7, where_to=fold, fLOG=fLOG)

        self.assertEqual(len(res), 1)
        s = res[0].replace("\\", "/")
        if not s.endswith("_unittests/ut_filehelper/temp_compress_7zip2/ftplib.html"):
            raise Exception(res[0])

    @skipif_travis('rar not installed')
    @skipif_appveyor('rar not installed')
    @skipif_circleci('rar not installed')
    @skipif_azure('rar not installed')
    def test_uncompress_rar(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        typbytes = bytes
        fold = get_temp_folder(__file__, "temp_compress_rar")
        rz = os.path.join(fold, "..", "data", "rar5-blake.rar")
        res = unrar_files(rz, where_to=fold, fLOG=fLOG)
        self.assertTrue(isinstance(res, list))
        res.sort()
        self.assertEqual(len(res), 2)
        if not isinstance(res[0], (typbytes, str)):
            raise TypeError(type(res[0]))
        res[0] = res[0].replace("\\", "/")
        if not res[0].endswith("ut_filehelper/temp_compress_rar/stest1.txt"):
            raise Exception(res[0])


if __name__ == "__main__":
    unittest.main()
