"""
@brief      test log(time=4s)
"""

import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.filehelper import gzip_files, zip_files, zip7_files, download, unzip_files, ungzip_files, un7zip_files, unrar_files
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestCompressHelper(unittest.TestCase):

    def test_compress_helper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        # fold = get_temp_folder(__file__, "temp_compress_helper")

        if sys.version_info[0] == 2:
            typbytes = bytearray
        else:
            typbytes = bytes

        f = os.path.abspath(__file__).replace(".pyc", ".py")

        rz = zip_files(None, [f], fLOG=fLOG)
        fLOG(len(rz), type(rz))
        if not isinstance(rz, (typbytes, str)):
            raise TypeError(type(rz))

        if sys.version_info[0] == 2:
            return

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
        # text
        if sys.version_info[0] == 2:
            typbytes = bytearray
        else:
            typbytes = bytes

        f = os.path.abspath(__file__).replace(".pyc", ".py")
        rg = gzip_files(None, [f], fLOG=fLOG, encoding="utf-8")
        fLOG(len(rg), type(rg))
        if not isinstance(rg, typbytes):
            raise TypeError(type(rg))

        res = ungzip_files(rg, encoding="utf-8")
        self.assertTrue("test_compress_helper_text" in res)

    def test_uncompress_7zip(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        import pylzma
        # use github version, not pypi version (2016-11-11)
        # this version does not include a fix to read file produced by the
        # latest version of 7z
        self.assertTrue(pylzma)

        if is_travis_or_appveyor() == "appveyor":
            warnings.warn(
                "unzipping files with 7z on a is not tested on appveyor")
            return

        fold = get_temp_folder(__file__, "temp_uncompress_7zip")
        data = os.path.join(fold, "..", "data", "ftplib.7z")
        files = un7zip_files(data, where_to=fold, fLOG=fLOG)
        self.assertEqual(len(files), 1)

    def test_compress_7zip(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = get_temp_folder(__file__, "temp_compress_7zip")
        url = "https://docs.python.org/3.5/library/ftplib.html"
        f = download(url, fold)

        if is_travis_or_appveyor() != "travis":
            out7 = os.path.join(fold, "try.7z")
            r = zip7_files(out7, [f], fLOG=fLOG, temp_folder=fold)
            fLOG(r)
            if not os.path.exists(out7):
                raise FileNotFoundError(out7)
        else:
            warnings.warn(
                "unzipping files with 7z on a is not tested on appveyor")
            return

        if sys.version_info[0] == 2:
            typbytes = bytearray
        else:
            typbytes = bytes

        if is_travis_or_appveyor() == "appveyor":
            warnings.warn(
                "py7zlib.py requires to be updated with the github version")
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

        if sys.version_info[0] == 2:
            return

        self.assertEqual(len(res), 1)
        s = res[0].replace("\\", "/")
        if not s.endswith("_unittests/ut_filehelper/temp_compress_7zip2/ftplib.html"):
            raise Exception(res[0])

    def test_uncompress_rar(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        # fold = get_temp_folder(__file__, "temp_compress_helper")

        if is_travis_or_appveyor():
            warnings.warn(
                "7z not available")
            return

        if sys.version_info[0] == 2:
            typbytes = bytearray
        else:
            typbytes = bytes

        fold = get_temp_folder(__file__, "temp_compress_rar")
        rz = os.path.join(fold, "..", "data", "rar5-blake.rar")
        res = unrar_files(rz, where_to=fold)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 2)
        if not isinstance(res[0], (typbytes, str)):
            raise TypeError(type(res[0]))
        res[0] = res[0].replace("\\", "/")
        if not res[0].endswith("ut_filehelper/temp_compress_rar/stest1.txt"):
            raise Exception(res[0])


if __name__ == "__main__":
    unittest.main()
