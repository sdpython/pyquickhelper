"""
@brief      test log(time=60s)
@author     Xavier Dupre
"""

import sys, os, unittest, re


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src

from src.pyquickhelper import fLOG, process_notebooks

class TestNoteBooksBug(unittest.TestCase):

    def test_regex(self):
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        exp = re.compile(r"(.{3}[\\]\$)")
        s = ": [ ['$',"
        fLOG(s)
        r = exp.finditer(s)
        nb = 0
        for _ in r :
            fLOG("1",_.groups())
            nb += 1
        nb1 = nb

        s = r"\def\PYZdl{\char`\$}"
        fLOG(s)
        r = exp.finditer(s)
        nb = 0
        for _ in r :
            fLOG("2",_.groups())
            nb += 1

        assert nb1 == 0
        assert nb > 0

    def test_notebook(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path    = os.path.abspath(os.path.split(__file__)[0])
        fold    = os.path.normpath(os.path.join(path, "notebooks"))
        nbs     = [ os.path.join(fold, _) for _ in os.listdir(fold) if ".ipynb" in _ ]
        formats = ["ipynb", "html", "python", "rst", "pdf", "docx"]

        temp = os.path.join(path, "temp_nb_bug")
        if not os.path.exists(temp): os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp,file))

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****",len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_)




if __name__ == "__main__"  :
    unittest.main ()