"""
@brief      test log(time=11s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper.notebook_helper import read_nb
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG


class TestNotebookSlides(unittest.TestCase):

    def test_notebook_iter(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_add_slides_metadata")
        nbfile = os.path.join(
            temp, "..", "data", "having_a_form_in_a_notebook.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile, kernel=False)
        for i, cell in enumerate(nb.iter_cells()):
            ls = nb.cell_height(cell)
            # fLOG(i,"-",nb.cell_type(cell), l)
            # if l > 400: fLOG(cell)
            assert ls > 0

        new_tags = nb.add_tag_slide()
        for k, v in sorted(new_tags.items()):
            a, b, c = v
            fLOG(k, a, b)

        assert len(new_tags) > 0


if __name__ == "__main__":
    unittest.main()
