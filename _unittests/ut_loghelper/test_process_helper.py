"""
@brief      test log(time=1s)
"""
import sys
import os
import unittest
import warnings
from pyquickhelper.loghelper import run_cmd, reap_children, CustomLog
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor


class TestProcessHelper(unittest.TestCase):

    def test_reap_children(self):
        if sys.platform.startswith("win"):
            cmd = "pause"
        else:
            cmd = 'ls -la | less'
        temp = get_temp_folder(__file__, "temp_reap_children")
        clog = CustomLog(temp)
        proc, _ = run_cmd(cmd, wait=False, fLOG=clog)
        self.assertTrue(_ is None)
        clog('proc={} pid={}'.format(proc, proc.pid))
        ki = reap_children(fLOG=clog, subset={proc.pid})
        clog('ki={0}'.format(ki))
        if ki is None and not is_travis_or_appveyor() and __name__ != '__main__':
            warnings.warn(
                "reap_children could not be fully tested ki is None.")
            return
        self.assertTrue(ki is not None)
        self.assertEqual(len(ki), 1)
        proc.returncode = 0


if __name__ == "__main__":
    unittest.main()
