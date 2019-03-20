"""
@brief      test tree node (time=2s)
"""

import sys
import os
import unittest
import pandas

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode.pip_helper import get_packages_list, package2dict
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.pip_helper import PQPipError


class TestPipHelper(ExtTestCase):

    def test_exc(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        exc = PQPipError('cmd', 'out', 'err')
        msg = str(exc)
        self.assertEqual([msg.replace('\n', '')], [
                         'CMD:cmdOUT:out[piperror]err'])

    def test_pip_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        li = get_packages_list()
        dt = package2dict(li[0])
        avoid = {'py_version'}
        empty = []
        for k, v in dt.items():
            if k not in avoid:
                if k is None:
                    empty.append(k)
        self.assertEmpty(empty)
        self.assertNotEmpty(li)


if __name__ == "__main__":
    unittest.main()
