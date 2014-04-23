"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys, os, unittest


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG
from src.pyquickhelper.helpgen.sphinx_main      import process_notebooks, add_notebook_page

class TestNotebookConversion (unittest.TestCase):
    
    def test_notebook(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path    = os.path.abspath(os.path.split(__file__)[0])
        fold    = os.path.normpath(os.path.join(path, "..", "..", "_doc", "notebooks"))
        nb      = os.path.join(fold, "example pyquickhelper.ipynb")
        assert os.path.exists(nb)
        
        temp = os.path.join(path, "temp_nb")
        if not os.path.exists(temp): os.mkdir(temp)
        for file in os.listdir(temp): 
            os.remove(os.path.join(temp,file))
        
        res = process_notebooks(nb, temp, temp)
        for _ in res:
            fLOG(_)
            assert os.path.exists(_)
                
        exp = ["example pyquickhelper.html",
                "example pyquickhelper.ipynb",
                "example pyquickhelper.py",
                "example pyquickhelper.rst",
                "example pyquickhelper.ipynb",
                "example pyquickhelper.tex",
                "example pyquickhelper.pdf",
                ]
        fou = [ os.path.split(_)[-1] for _ in res ]
        if len(fou) < len(exp):
            raise Exception("length {0} != {1}\n{2}\n---\n{3}".format(len(fou),len(exp),
                    "\n".join(fou), "\n".join(exp)))
        for i,j in zip(exp,fou):
            if i != j : raise Exception("{0} != {1}".format(i,j))
     
        file = os.path.join(temp, "all_notebooks.rst")
        add_notebook_page(res, file)
        assert os.path.exists(file)
            
        
if __name__ == "__main__"  :
    unittest.main ()    
