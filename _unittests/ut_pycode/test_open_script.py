# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=5s)
"""
import sys
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.open_script_file import open_script, detect_encoding
from pyquickhelper.pycode.linux_scripts import _sversion


class TestOpenScript(ExtTestCase):

    def test_open_script(self):
        s = "éé"
        self.assertEqual(len(s), 2)
        file = __file__.replace(".pyc", ".py")
        enc = detect_encoding(file)
        self.assertEqual(enc, "utf-8")
        with open_script(file, "r") as f:
            r = f.read()
        self.assertGreater(len(r), 0)
        enc = detect_encoding(b"rr")
        self.assertEqual(enc, None)
        self.assertRaise(lambda: detect_encoding(1), TypeError)

    def test__sversion(self):
        self.assertEqual(_sversion(), "PY%d%d" % sys.version_info[:2])


if __name__ == "__main__":
    unittest.main()
