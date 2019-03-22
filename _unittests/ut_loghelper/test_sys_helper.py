"""
@brief      test tree node (time=2s)
"""
import sys
import os
import unittest

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.loghelper import sys_path_append, python_path_append


class TestSysHelper(ExtTestCase):

    def test_sys_path_append(self):
        self.assertNotIn("ZooZoo", sys.path)
        with sys_path_append("ZooZoo"):
            self.assertIn("ZooZoo", sys.path)
        self.assertNotIn("ZooZoo", sys.path)

    def test_sys_path_append0(self):
        self.assertNotIn("ZooZoo", sys.path)
        with sys_path_append("ZooZoo", 0):
            self.assertIn("ZooZoo", sys.path)
        self.assertNotIn("ZooZoo", sys.path)

    def test_python_path_append(self):
        self.assertNotIn("ZooZoo", os.environ.get('PYTHONPATH', ''))
        with python_path_append("ZooZoo", False):
            self.assertIn("ZooZoo", os.environ.get('PYTHONPATH', ''))
        self.assertNotIn("ZooZoo", os.environ.get('PYTHONPATH', ''))

    def test_python_path_append0(self):
        self.assertNotIn("ZooZoo", os.environ.get('PYTHONPATH', ''))
        with python_path_append("ZooZoo", True):
            self.assertIn("ZooZoo", os.environ.get('PYTHONPATH', ''))
        self.assertNotIn("ZooZoo", os.environ.get('PYTHONPATH', ''))


if __name__ == "__main__":
    unittest.main()
