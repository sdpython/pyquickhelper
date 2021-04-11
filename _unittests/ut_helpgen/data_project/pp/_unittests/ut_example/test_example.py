"""
@brief      test log(time=1s)
"""
import unittest
from pyquickhelper.pycode import ExtTestCase
from python3_module_template import fct


class TestExample(ExtTestCase):
    """Example of a test."""

    def test_fct(self):
        fct()


if __name__ == "__main__":
    unittest.main()
