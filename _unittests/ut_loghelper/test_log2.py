"""
@brief      test tree node (time=6s)
"""
import sys
import os
import unittest
import warnings
from pyquickhelper.loghelper.flog import (
    _get_file_url, _get_file_txt, get_default_value_type, run_cmd, download)
from pyquickhelper.pycode import get_temp_folder


class TestLog2 (unittest.TestCase):

    def test_synchro(self):
        url = "http://www.xavierdupre.fr/?blogpost=1"
        uu = _get_file_url(url, "/this/")
        self.assertEqual(uu, "/this//http!!www-xavierdupre-fr!_blogpost_1")
        uu = _get_file_txt("/g/r.zip")
        self.assertEqual(uu, "r.txt")

    def test_get_default_value_type(self):
        self.assertIsNone(get_default_value_type(None))
        self.assertEqual(get_default_value_type(int), 0)

    def test_run_cmd(self):
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
        temp = get_temp_folder(__file__, "temp_download")
        url = "http://www.xavierdupre.fr/enseignement/complements/added.zip"
        try:
            down = download(url, temp)
        except TimeoutError as e:
            warnings.warn(e)
            return
        self.assertTrue(os.path.exists(down))
        self.assertTrue(down.endswith("added.txt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
