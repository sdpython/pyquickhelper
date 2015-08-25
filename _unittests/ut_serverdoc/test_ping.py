"""
@brief      test log(time=1s)
"""


import sys
import os
import unittest

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

from src.pyquickhelper import fLOG
from src.pyquickhelper.serverdoc import ping_machine, regular_ping_machine


class TestPing(unittest.TestCase):
    
    def get_machine(self):
        if sys.platform.startswith("win"):
            return os.environ["COMPUTERNAME"]
        else:
            r = os.environ.get("HOSTNAME", None)
            if r is None:
                raise Exception(str(os.environ))

    def test_ping(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        machine = self.get_machine()
        out = ping_machine(machine, fLOG=fLOG)
        fLOG(out)
        assert len(out) > 0

    def test_regular_ping(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        machine = self.get_machine()
        out = regular_ping_machine(machine, delay=0.1, nb_max=3, fLOG=fLOG)
        fLOG(out)
        assert len(out) > 0


if __name__ == "__main__":
    unittest.main()
