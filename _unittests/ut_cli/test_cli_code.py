"""
@brief      test tree node (time=7s)
"""
import os
import unittest
from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.__main__ import main


class TestCliCodeHelper(ExtTestCase):

    def test_code_stat_help(self):
        st = BufferedPrint()
        main(args=['code_stat', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: code_stat", res)

    def test_code_stat_pyq(self):
        st = BufferedPrint()
        main(args=['code_stat', '-n', 'pyquickhelper'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("doc_code", res)

    def test_code_stat_pyq_file(self):
        temp = get_temp_folder(__file__, "temp_code_stat_pyq_file")
        name = os.path.join(temp, "report.xlsx")
        st = BufferedPrint()
        main(args=['code_stat', '-n', 'pyquickhelper',
             '-o', name], fLOG=st.fprint)
        self.assertLess(len(str(st)), 10)
        self.assertExists(name)


if __name__ == "__main__":
    unittest.main()
