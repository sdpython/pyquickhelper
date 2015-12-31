"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import re

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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.cli.encryption_file_cli import encrypt_file, decrypt_file


class TestEncryptionCli(unittest.TestCase):

    def test_encrypt_decrypt_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_encrypt_file")
        dest = os.path.join(temp, "__file__.enc")
        sys.argv = ["", __file__, dest, "unittest" * 2]
        encrypt_file()

        dest2 = os.path.join(temp, "__file__.py")
        sys.argv = ["", dest, dest2, "unittest" * 2]
        decrypt_file()

        with open(__file__, "rb") as f:
            c1 = f.read()
        with open(dest2, "rb") as f:
            c2 = f.read()

        self.assertEqual(c1, c2)


if __name__ == "__main__":
    unittest.main()
