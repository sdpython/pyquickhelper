"""
@brief      test log(time=100s)
@author     Xavier Dupre

This tesdt must be run last because it screws up with
*test_convert_doc_helper* and *test_full_documentation_module_template*.
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp


class TestAppSphinx(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_app_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_app_sphinx")
        src_ = os.path.join(temp, "..", "data", "doc")

        app = CustomSphinxApp(src_, temp)
        app.build()
        # app.cleanup()

        index = os.path.join(temp, "index.html")
        self.assertExists(index)

    def test_app_sphinx_custom(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_app_sphinx_custom")
        src_ = os.path.join(temp, "..", "data", "doc")

        app = CustomSphinxApp(src_, temp)
        app.build()
        # custom_setup(app, None)


if __name__ == "__main__":
    unittest.main()
