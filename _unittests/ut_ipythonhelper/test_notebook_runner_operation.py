"""
@brief      test log(time=11s)
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

from src.pyquickhelper.ipythonhelper import read_nb
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.loghelper import fLOG


class TestNotebookRunnerOperation (unittest.TestCase):

    def test_notebook_runner_operation(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # written in Python 3
            return
        temp = get_temp_folder(__file__, "temp_notebook_operation")

        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        nbfile2 = os.path.join(
            temp, "..", "data", "td2a_cenonce_session_4B.ipynb")
        nb1 = read_nb(nbfile, kernel=False)
        n1 = len(nb1)
        nb2 = read_nb(nbfile2, kernel=False)
        n2 = len(nb2)
        add = nb1 + nb2
        nb1.merge_notebook([nb2])
        n3a = len(add)
        n3 = len(nb1)
        if n1 + n2 != n3:
            raise Exception("{0} + {1} != {2}".format(n1, n2, n3))
        if n3a != n3:
            raise Exception("{0} != {1}".format(n3a, n3))

        fLOG(n1, n2, n3, n3a)
        outfile = os.path.join(temp, "merge_nb.ipynb")
        nb1.to_json(outfile)
        assert os.path.exists(outfile)
        outfile = os.path.join(temp, "merge_nb_add.ipynb")
        add.to_json(outfile)
        assert os.path.exists(outfile)


if __name__ == "__main__":
    unittest.main()
