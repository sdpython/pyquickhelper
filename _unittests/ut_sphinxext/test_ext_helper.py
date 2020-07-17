"""
@brief      test log(time=3s)
"""
import sys
import os
import unittest
from docutils.parsers.rst import directives

from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext.sphinx_ext_helper import get_index


class TestExtHelper(ExtTestCase):

    def test_load_index(self):
        temp = get_temp_folder(__file__, "temp_load_index")
        url = "https://pandas.pydata.org/docs/"
        res = get_index(url, temp)
        self.assertNotEmpty(res)
        self.assertGreater(len(res), 2)
        self.assertIsInstance(res, dict)
        res2 = get_index(url, temp)
        self.assertNotEmpty(res2)
        self.assertEqual(len(res2), len(res))


if __name__ == "__main__":
    unittest.main()
