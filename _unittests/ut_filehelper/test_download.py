"""
@brief      test log(time=2s)
"""

import sys, os, unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError("this file should not be imported in that location: " + os.path.abspath(__file__))

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper import download, get_temp_folder, fLOG


class TestDownload (unittest.TestCase):

    def test_download(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        fold = get_temp_folder(__file__,"temp_download")
        url = "https://docs.python.org/3.5/library/ftplib.html"
        f = download(url, fold)
        fLOG(f)
        assert os.path.exists(f)
        assert f.endswith("ftplib.html")


if __name__ == "__main__"  :
    unittest.main ()