"""
@brief      test log(time=100s)

You should indicate a time in seconds. The program ``run_unittests.py``
will sort all test files by increasing time and run them.
"""

import unittest
from pyquickhelper.pycode import ExtTestCase


class TestSKIPExample(ExtTestCase):
    """Test in SKIP series, skipped by default."""

    def test_src(self):
        "skip pylint"
        self.assertFalse(ExtTestCase is None)

    def test_skip_void(self):
        self.assertTrue(ExtTestCase is not None)


if __name__ == "__main__":
    unittest.main()
