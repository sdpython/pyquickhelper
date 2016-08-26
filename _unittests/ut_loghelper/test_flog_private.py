"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import shutil

if sys.version_info[0] == 2:
    import urllib as URL
else:
    import urllib.request as URL


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
from src.pyquickhelper.loghelper.flog import _first_more_recent


class TestfLOGPrivate(unittest.TestCase):

    def test_url_more_recent(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        name = "test_syncho.py"

        temp = get_temp_folder(__file__, "temp_url_more_recent")
        shutil.copy(os.path.join(this, name), temp)
        dest = os.path.join(temp, name)

        url = "https://github.com/sdpython/pyquickhelper/tree/master/_unittests/ut_loghelper/" + name
        f1 = URL.urlopen(url)
        r = _first_more_recent(f1, dest)
        f1.close()
        assert isinstance(r, bool)

        url = "http://www.lemonde.fr/"
        f1 = URL.urlopen(url)
        r = _first_more_recent(f1, dest)
        f1.close()
        assert isinstance(r, bool)
        fLOG(r)


if __name__ == "__main__":
    unittest.main()
