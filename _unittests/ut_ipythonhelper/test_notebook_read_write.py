"""
@brief      test log(time=5s)
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

from src.pyquickhelper.ipythonhelper.notebook_helper import read_nb
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.loghelper import fLOG


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookReadWrite (unittest.TestCase):

    def test_notebook_read_write(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # written in Python 3
            return
        temp = get_temp_folder(__file__, "temp_notebook_read_write")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        nb.to_json(outfile)
        assert os.path.exists(outfile)

        with open(nbfile, "r", encoding="utf8") as f:
            c1 = f.read().replace("\r", "")
        with open(outfile, "r", encoding="utf8") as f:
            c2 = f.read().replace("\r", "")
        if c1 != c2:
            l1 = c1.strip("\n ").split("\n")
            l2 = c2.strip("\n ").split("\n")
            for i, cc in enumerate(zip(l1, l2)):
                a, b = cc
                if a.strip(" \n") != b.strip(" \n"):
                    raise Exception(
                        "difference at line {0}\n1: [{1}]-[{3}]\n2: [{2}]-[{4}]".format(i, a, b, type(a), type(b)))
            if len(l1) != len(l2):
                raise Exception("different length")

    def test_notebook_iter(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # written in Python 3
            return
        temp = get_temp_folder(__file__, "temp_notebook_add_slides_metadata")
        nbfile = os.path.join(
            temp, "..", "data", "having_a_form_in_a_notebook.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile)
        for i, cell in enumerate(nb.iter_cells()):
            l = nb.cell_height(cell)
            #fLOG(i,"-",nb.cell_type(cell), l)
            #if l > 400: fLOG(cell)
            assert l > 0

        new_tags = nb.add_tag_slide()
        for k, v in sorted(new_tags.items()):
            a, b, c = v
            fLOG(k, a, b)

        assert len(new_tags) > 0


if __name__ == "__main__":
    unittest.main()
