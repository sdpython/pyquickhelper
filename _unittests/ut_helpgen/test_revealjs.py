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


from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.helpgen.install_custom import download_revealjs
from src.pyquickhelper.helpgen.install_js_dep import install_javascript_tools


class TestRevealjs(unittest.TestCase):

    def test_install_revealjs_github(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])

        temp = get_temp_folder(__file__, "temp_install_revealjs_github")
        dest = get_temp_folder(__file__, "temp_install_revealjs_github_dest")
        fs = download_revealjs(temp, dest, fLOG=fLOG)
        fLOG(fs)
        assert len(fs) > 0
        for a in fs:
            assert os.path.exists(a)

    def test_install_revealjs_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])

        dest = get_temp_folder(__file__, "temp_install_revealjs_sphinx")
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
