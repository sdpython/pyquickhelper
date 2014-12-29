"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys, os, unittest, pandas, datetime


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src

from src.pyquickhelper.loghelper.flog           import fLOG
from src.pyquickhelper.helpgen.sphinx_main      import generate_changes_repo, produce_code_graph_changes

class TestGraphChanges (unittest.TestCase):

    def test_graph_changes(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path, "data", "changes.txt")
        df = pandas.read_csv(data, sep="\t")
        fLOG(type(df.ix[0,"date"]),df.ix[0,"date"])
        code = produce_code_graph_changes(df)
        fLOG(code)

        if __name__ != "__main__":
            code = code.replace("plt.show","#plt.show")

        obj = compile(code, "", "exec")
        exec(obj, globals(), locals())



if __name__ == "__main__"  :
    unittest.main ()