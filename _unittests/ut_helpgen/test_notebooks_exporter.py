"""
@brief      test log(time=6s)
@author     Xavier Dupre
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
from src.pyquickhelper.helpgen.sphinx_main import process_notebooks
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_travis


class TestNoteBooksExporter(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis('pandoc is not installed on travis')
    def test_notebook_rst_svg(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_nb_rst_svg")
        nbs = [os.path.normpath(os.path.join(
            temp, '..', "data", "rst_notebooks", "notebook_with_svg.ipynb"))]
        formats = ["rst"]

        res = process_notebooks(nbs, temp, temp, formats=formats, fLOG=fLOG)
        name = res[0][0]
        with open(name, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('SVG in a notebook.', content)
        self.assertIn('.. image::', content)

        nb = 0
        for line in content.split('\n'):
            if '.. image::' in line:
                name = line.replace('.. image::', '').strip(' \r\t')
                dest = os.path.join(temp, name)
                self.assertExists(dest)
                nb += 1
        self.assertGreater(nb, 0)

    @skipif_travis('pandoc is not installed on travis')
    def test_notebook_rst_contents(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_nb_rst_contents")
        nbs = [os.path.normpath(os.path.join(
            temp, '..', "data", "rst_notebooks", "exemple_of_fix_menu.ipynb"))]
        formats = ["rst"]

        res = process_notebooks(nbs, temp, temp, formats=formats, fLOG=fLOG)
        name = res[0][0]
        with open(name, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('.. contents::', content)


if __name__ == "__main__":
    unittest.main()
