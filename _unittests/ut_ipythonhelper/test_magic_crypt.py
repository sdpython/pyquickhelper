"""
@brief      test log(time=1s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.ipythonhelper.magic_class_crypt import MagicCrypt


class TestMagicCrypt(unittest.TestCase):

    def test_files_compress(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        password = "unittest" * 2
        this = os.path.abspath(__file__)
        temp = get_temp_folder(__file__, "temp_crypt")
        dest = os.path.join(temp, "out_crypt.enc")

        mg = MagicCrypt()

        cmd = "this dest %s" % password
        fLOG("**", cmd)
        if os.path.exists(dest):
            raise Exception(dest)
        mg.add_context({"this": this, "dest": dest})
        res = mg.encrypt_file(cmd)
        fLOG(res)
        assert os.path.exists(dest)

        dest2 = os.path.join(temp, "__file__.py")

        cmd = "dest dest2 %s" % password
        fLOG("**", cmd)
        assert not os.path.exists(dest2)
        mg.add_context({"dest": dest, "dest2": dest2})
        res = mg.decrypt_file(cmd)
        fLOG(res)
        assert os.path.exists(dest2)

        with open(__file__, "rb") as f:
            c1 = f.read()
        with open(dest2, "rb") as f:
            c2 = f.read()

        self.assertEqual(c1, c2)
        fLOG("end", len(c1), len(c2))
        assert len(c1) > 0


if __name__ == "__main__":
    unittest.main()
