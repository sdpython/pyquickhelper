"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
from io import StringIO


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


from src.pyquickhelper.loghelper import fLOG, BufferedPrint
from src.pyquickhelper.pycode import get_temp_folder, skipif_travis, skipif_appveyor
from src.pyquickhelper.__main__ import main


class TestProcessNotebook(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis("No latex installed.")
    @skipif_appveyor("No latex installed.")
    def test_process_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_process_notebook")
        source = os.path.join(temp, "..", "data", "td1a_unit_test_ci.ipynb")

        st = BufferedPrint()
        main(args=["process_notebooks", "-n", source, "-o",
                   temp, "-b", temp, '-f', 'rst'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("convert into  rst", res)


if __name__ == "__main__":
    unittest.main()
