"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import shutil
import urllib.request as URL


if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.loghelper.flog import _first_more_recent


class TestfLOGPrivate(ExtTestCase):

    def test_url_more_recent(self):
        this = os.path.abspath(os.path.dirname(__file__))
        name = "test_syncho.py"

        temp = get_temp_folder(__file__, "temp_url_more_recent")
        shutil.copy(os.path.join(this, name), temp)
        dest = os.path.join(temp, name)

        url = "https://github.com/sdpython/pyquickhelper/tree/master/_unittests/ut_loghelper/" + name
        f1 = URL.urlopen(url)
        r = _first_more_recent(f1, dest)
        f1.close()
        self.assertIsInstance(r, bool)

        url = "https://www.lemonde.fr/"
        f1 = URL.urlopen(url)
        r = _first_more_recent(f1, dest)
        f1.close()
        self.assertIsInstance(r, bool)


if __name__ == "__main__":
    unittest.main()
