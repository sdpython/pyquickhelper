"""
@brief      test log(time=7s)

skip this test for regular run
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


from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen.install_js_dep import install_javascript_tools


class TestAlljs(unittest.TestCase):

    def test_install_alljs(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        dest = get_temp_folder(__file__, "temp_install_alljs_sphinx")
        fs = install_javascript_tools(
            dest, dest, fLOG=fLOG, revealjs_github=False)
        fLOG(fs)
        assert len(fs) > 0
        for a in fs:
            assert os.path.exists(a)
        r = os.path.join(dest, "reveal.js", "js", "reveal.min.js")
        assert os.path.exists(r)

if __name__ == "__main__":
    unittest.main()
