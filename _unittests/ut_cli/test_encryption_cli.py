"""
@brief      test tree node (time=7s)
"""
import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.cli.encryption_file_cli import encrypt_file, decrypt_file
from pyquickhelper.cli.encryption_cli import encrypt, decrypt


class TestEncryptionCli(unittest.TestCase):

    def test_encrypt_decrypt_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        password = "unittest" * 2

        temp = get_temp_folder(__file__, "temp_encrypt_file")
        dest = os.path.join(temp, "__file__.enc")
        sys.argv = ["", __file__, dest, password]
        encrypt_file(fLOG=fLOG)

        dest2 = os.path.join(temp, "__file__.py")
        sys.argv = ["", dest, dest2, password]
        decrypt_file(fLOG=fLOG)

        with open(__file__, "rb") as f:
            c1 = f.read()
        with open(dest2, "rb") as f:
            c2 = f.read()

        self.assertEqual(c1, c2)
        fLOG("end")

    def test_encrypt_decrypt(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        password = "unittest" * 2

        temp = get_temp_folder(__file__, "temp_encrypt")
        temp2 = get_temp_folder(__file__, "temp_encrypt2")
        tempmm = get_temp_folder(__file__, "temp_encrypt_status")
        cstatus = os.path.join(tempmm, "crypt_status.txt")
        cmap = os.path.join(tempmm, "crypt_map.txt")
        srcf = os.path.abspath(os.path.join(temp, ".."))
        sys.argv = ["", srcf, temp, password,
                    "--status", cstatus,
                    "--map", cmap]
        encrypt(fLOG=fLOG)
        this = __file__

        sys.argv = ["", temp, temp2, password]
        decrypt(fLOG=fLOG)

        with open(__file__, "rb") as f:
            c1 = f.read()
        with open(os.path.join(temp2, os.path.split(this)[-1]), "rb") as f:
            c2 = f.read()

        self.assertEqual(c1, c2)
        fLOG("end")


if __name__ == "__main__":
    unittest.main()
