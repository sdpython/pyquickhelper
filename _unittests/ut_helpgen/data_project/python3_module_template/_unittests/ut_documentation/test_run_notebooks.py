# -*- coding: utf-8 -*-
"""
@brief      test log(time=11s)
"""

import os
import unittest
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode import add_missing_development_version
from pyquickhelper.ipythonhelper import test_notebook_execution_coverage

import python3_module_template


class TestRunNotebooks(ExtTestCase):
    """Runs notebooks in the documentation."""

    def setUp(self):
        add_missing_development_version(["jyquickhelper"], __file__, hide=True)

    def test_run_custom(self):
        fLOG(__file__, self._testMethodName,
             OutputPrint=__name__ == "__main__")
        self.assertTrue(python3_module_template is not None)
        folder = os.path.join(os.path.dirname(__file__),
                              "..", "..", "_doc", "notebooks")
        test_notebook_execution_coverage(
            __file__, "custom", folder, 'python3_module_template', copy_files=[], fLOG=fLOG)

    def test_run_slide(self):
        fLOG(__file__, self._testMethodName,
             OutputPrint=__name__ == "__main__")
        self.assertTrue(python3_module_template is not None)
        folder = os.path.join(os.path.dirname(__file__),
                              "..", "..", "_doc", "notebooks")
        test_notebook_execution_coverage(
            __file__, "slide", folder, 'python3_module_template', copy_files=[], fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
