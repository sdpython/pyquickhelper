"""
@brief      test log(time=1s)
"""
import sys
import os
import unittest
import warnings
from pyquickhelper.loghelper import run_cmd, reap_children, CustomLog
from pyquickhelper.pycode import (
    ExtTestCase, get_temp_folder, is_travis_or_appveyor)


class TestProcessHelper(ExtTestCase):

    def test_reap_children(self):
        if sys.platform.startswith("win"):
            cmd = "pause"
        else:
            cmd = 'ls -la'
        temp = get_temp_folder(__file__, "temp_reap_children")
        clog = CustomLog(temp)
        proc, _ = run_cmd(cmd, wait=False, fLOG=clog)
        self.assertTrue(_ is None)
        clog(f'proc={proc} pid={proc.pid}')
        ki = reap_children(fLOG=clog, subset={proc.pid})
        clog(f'ki={ki}')
        if ki is None and not is_travis_or_appveyor() and __name__ != '__main__':
            warnings.warn(
                "reap_children could not be fully tested ki is None.")
            return
        self.assertTrue(ki is not None)
        self.assertEqual(len(ki), 1)
        proc.returncode = 0


if __name__ == "__main__":
    unittest.main()
