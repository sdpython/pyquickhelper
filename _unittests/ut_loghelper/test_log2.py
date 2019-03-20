"""
@brief      test tree node (time=6s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG, _get_file_url, _get_file_txt, get_default_value_type, run_cmd, download
from pyquickhelper.pycode import get_temp_folder


class TestLog2 (unittest.TestCase):

    def test_synchro(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        url = "http://www.xavierdupre.fr/?blogpost=1"
        uu = _get_file_url(url, "/this/")
        self.assertEqual(uu, "/this//http!!www-xavierdupre-fr!_blogpost_1")
        uu = _get_file_txt("/g/r.zip")
        self.assertEqual(uu, "r.txt")

    def test_get_default_value_type(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertIsNone(get_default_value_type(None))
        self.assertEqual(get_default_value_type(int), 0)

    def test_run_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "dir" if sys.platform.startswith("win") else "ls"
        cmd += " " + os.path.abspath(os.path.split(__file__)[0])
        out, err = run_cmd(cmd, wait=True)
        if os.path.split(__file__)[-1] not in out and "setup.py" not in out:
            raise Exception("unable to find {0} in\n{1}\nCMD:\n{2}".format(
                os.path.split(__file__)[-1], out, cmd))

        out, err = run_cmd(cmd, wait=True, communicate=False)
        if os.path.split(__file__)[-1] not in out and "setup.py" not in out:
            raise Exception("unable to find {0} in\n{1}\nCMD:\n{2}".format(
                os.path.split(__file__)[-1], out, cmd))

    def test_download(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_download")
        url = "http://www.xavierdupre.fr/enseignement/complements/added.zip"
        down = download(url, temp)
        self.assertTrue(os.path.exists(down))
        self.assertTrue(down.endswith("added.txt"))


if __name__ == "__main__":
    unittest.main()
