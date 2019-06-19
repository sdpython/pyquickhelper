"""
@brief      test log(time=100s)
@author     Xavier Dupre

This tesdt must be run last because it screws up with
*test_convert_doc_helper* and *test_full_documentation_module_template*.
"""

import os
import unittest
import logging

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp


class TestAppSphinx(ExtTestCase):

    def setUp(self):
        logger = logging.getLogger('gdot')
        logger.disabled = True

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
