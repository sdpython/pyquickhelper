"""
@brief      test log(time=30s)
@author     Xavier Dupre
"""

import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.helpgen.sphinx_main import setup_environment_for_help
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugSlides(ExtTestCase):

    def test_notebook_slides(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_slides"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides"]

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        temp = get_temp_folder(__file__, "temp_nb_bug_slides")
        setup_environment_for_help()

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        with open(os.path.join(temp, "js_bokeh.slides.html"), "r", encoding="utf8") as f:
            content = f.read()
        exp = "is one if the most mature and complete library using javascript."
        if exp not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
