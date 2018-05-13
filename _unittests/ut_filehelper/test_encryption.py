"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.filehelper import encrypt_stream, decrypt_stream

if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO as StreamIO
else:
    from io import BytesIO as StreamIO


class TestEncryption(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_encryption_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Cryptodome as skip_
        except ImportError:
            warnings.warn("pycryptodome is not installed")
            return

        temp = get_temp_folder(__file__, "temp_encryption0")

        infile = os.path.abspath(__file__).replace(".pyc", ".py")
        outfile = os.path.join(temp, "out_crypted.enc")
        r = encrypt_stream(b"key0" * 4, infile, outfile)
        assert r is None

        outfile2 = os.path.join(temp, "out_decrypted.enc")
        r = decrypt_stream(b"key0" * 4, outfile, outfile2)
        assert r is None

        with open(infile, "rb") as f:
            inc = f.read()
        with open(outfile2, "rb") as f:
            ouc = f.read()
        self.assertEqual(inc, ouc)

        outfile3 = os.path.join(temp, "out_decrypted2.enc")
        r = decrypt_stream(b"key1" * 4, outfile, outfile3)
        assert r is None
        with open(outfile3, "rb") as f:
            ouc3 = f.read()
        self.assertNotEqual(inc, ouc3)

    def test_encryption_file_size(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Cryptodome as skip__
        except ImportError:
            warnings.warn("pycryptodomex is not installed")
            return

        temp = get_temp_folder(__file__, "temp_encryption1")

        infile = os.path.abspath(__file__).replace(".pyc", ".py")
        outfile = os.path.join(temp, "out_crypted.enc")
        r = encrypt_stream(b"key0" * 4, infile, outfile, chunksize=16)
        assert r is None

        outfile2 = os.path.join(temp, "out_decrypted.enc")
        r = decrypt_stream(b"key0" * 4, outfile, outfile2, chunksize=16)
        assert r is None

        with open(infile, "rb") as f:
            inc = f.read()
        with open(outfile2, "rb") as f:
            ouc = f.read()
        self.assertEqual(inc, ouc)

        outfile3 = os.path.join(temp, "out_decrypted2.enc")
        r = decrypt_stream(b"key1" * 4, outfile, outfile3, chunksize=16)
        assert r is None
        with open(outfile3, "rb") as f:
            ouc3 = f.read()
        self.assertNotEqual(inc, ouc3)

    def test_encryption_bytes(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Cryptodome as skip__
        except ImportError:
            warnings.warn("pycryptodomex is not installed")
            return

        infile = bytes([0, 1, 2, 3, 4])
        r = encrypt_stream(b"key0" * 4, infile)
        assert r is not None

        r2 = decrypt_stream(b"key0" * 4, r)
        assert r2 is not None

        self.assertEqual(infile, r2)

        r3 = decrypt_stream(b"key1" * 4, r)
        assert r3 is not None
        self.assertNotEqual(infile, r3)

    def test_encryption_stream(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Cryptodome as skip___
        except ImportError:
            warnings.warn("pycryptodomex is not installed")
            return

        infile = StreamIO(bytes([0, 1, 2, 3, 4]))
        outst = StreamIO()

        r = encrypt_stream(b"key0" * 4, infile, outst)
        assert r is None

        enc = StreamIO(outst.getvalue())
        enc2 = StreamIO(outst.getvalue())
        outdec = StreamIO()
        r2 = decrypt_stream(b"key0" * 4, enc, outdec)
        assert r2 is None

        self.assertEqual(infile.getvalue(), outdec.getvalue())

        outdec2 = StreamIO()
        r3 = decrypt_stream(b"key1" * 4, enc2, outdec2)
        assert r3 is None
        self.assertNotEqual(infile.getvalue(), outdec2.getvalue())

    def test_encryption_stream_fernet(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        infile = StreamIO(bytes([0, 1, 2, 3, 4]))
        outst = StreamIO()

        r = encrypt_stream("key0" * 8, infile, outst, algo="fernet")
        assert r is None

        enc = StreamIO(outst.getvalue())
        enc2 = StreamIO(outst.getvalue())
        outdec = StreamIO()
        r2 = decrypt_stream("key0" * 8, enc, outdec, algo="fernet")
        assert r2 is None

        self.assertEqual(infile.getvalue(), outdec.getvalue())

        outdec2 = StreamIO()
        try:
            r3 = decrypt_stream("key1" * 8, enc2, outdec2, algo="fernet")
        except Exception:
            return
        assert r3 is None
        self.assertNotEqual(infile.getvalue(), outdec2.getvalue())

    def test_encryption_stream_fernet_chunck_size(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        infile = StreamIO(bytes(list(i % 255 for i in range(0, 10000))))
        outst = StreamIO()

        r = encrypt_stream("key0" * 8, infile, outst,
                           algo="fernet", chunksize=256)
        assert r is None

        enc = StreamIO(outst.getvalue())
        enc2 = StreamIO(outst.getvalue())
        outdec = StreamIO()
        r2 = decrypt_stream("key0" * 8, enc, outdec,
                            algo="fernet", chunksize=256)
        assert r2 is None

        self.assertEqual(infile.getvalue(), outdec.getvalue())

        outdec2 = StreamIO()
        try:
            r3 = decrypt_stream("key1" * 8, enc2, outdec2,
                                algo="fernet", chunksize=256)
        except Exception:
            return
        assert r3 is None
        self.assertNotEqual(infile.getvalue(), outdec2.getvalue())


if __name__ == "__main__":
    unittest.main()
