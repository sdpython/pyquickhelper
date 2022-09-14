"""
@brief      test log(time=0s)
"""
import sys
import os
import unittest
import time

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "This file should not be imported in that location: {0}".format(
            os.path.abspath(__file__)))

from pyquickhelper.loghelper.run_cmd import run_cmd, run_script
from pyquickhelper.loghelper.flog import (
    fLOG, load_content_file_with_encoding, get_prefix,
    removedirs, unzip, guess_type_list, GetLogFile, get_relative_path,
    guess_machine_parameter)
from pyquickhelper.pycode import ExtTestCase


class TestLog(ExtTestCase):

    def test_import_problem(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        for k in sys.modules:
            if k == "core.codecs":
                if __name__ == "__main__":
                    keys = sorted(sys.modules.keys())
                    for k in keys:
                        if sys.modules[k] is None:
                            print("None ", k)
                #raise Exception ("shit")

    def test_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.platform.startswith("win"):
            cmd = "dir"
        else:
            cmd = "ls"
        out, err = run_cmd(cmd, shell=True, wait=True)
        assert len(out) > 0
        out, err = run_cmd(cmd + " *.pyc", shell=True, wait=True)
        assert len(out) > 0

    def test_cmd_noshell(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.platform.startswith("win"):
            cmd = "dir"
        else:
            cmd = "ls"
        out, err = run_cmd(cmd, wait=True)
        assert len(out) > 0

    def test_cmd_communicate(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.platform.startswith("win"):
            cmd = "dir"
        else:
            cmd = "ls"
        out, err = run_cmd(cmd, wait=True, communicate=True)
        assert len(out) > 0

    def test_cmd_communicate2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.platform.startswith("win"):
            out, err = run_cmd("dir *.py", shell=True,
                               wait=True, communicate=True)
        else:
            out, err = run_cmd("ls *.py", shell=True,
                               wait=True, communicate=True)
        self.assertNotEmpty(out)

    def test_python(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        file = os.path.join(
            os.path.split(__file__)[0],
            "..",
            "..",
            "src",
            "pyquickhelper",
            "loghelper",
            "flog_fake_classes.py")
        out, err = run_script(file)
        assert out is not None
        assert err is None
        out.__exit__(None, None, None)

    def test_prefix(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        p1 = get_prefix()
        time.sleep(1)
        p2 = get_prefix()
        self.assertNotEqual(p1, p2)

    def test_unzip(self):
        pat = os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "temp_zip22"))
        patl = os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "temp_zip22log"))
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__",
            LogPath=patl)
        if not os.path.exists(pat):
            os.mkdir(pat)

        z = os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "data",
                "test_file_nrt.zip"))
        unz = unzip(z, path_unzip=pat)
        assert os.path.exists(os.path.join(pat, "test_file_nrt.txt"))
        unz = unzip(z, path_unzip=pat)

        z = os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "data",
                "test_log_nrt.gz"))
        unz = unzip(z, path_unzip=pat)
        assert os.path.exists(os.path.join(pat, "test_log_nrt.txt"))
        unz = unzip(z, path_unzip=pat)

        fLOG("A")
        z = os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "data",
                "sample_zip.zip"))
        unz = unzip(z, path_unzip=pat)

        fLOG("B")
        f = os.path.join(pat, "tsv_error__.txt")
        if not os.path.exists(f):
            raise FileNotFoundError(f)
        f = os.path.join(pat, "tsv_file__.txt")
        if not os.path.exists(f):
            raise FileNotFoundError(f)

        fLOG("C ** ", z)
        unz = unzip(z, path_unzip=pat)
        fLOG("***", unz)
        assert len(unz) > 0

        fLOG("D")
        r = removedirs(pat, silent=True)
        if len(r) > 1:
            raise Exception("pattern: " + pat + "\n" + "\n".join(r))

    def test_guess_type(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        li = [
            '0002',
            '0003',
            '0001',
            '0',
            '0',
            '0',
            '0',
            '0',
            '',
            '0002',
            '0003',
            '0001',
            '0002',
            '0003',
            '0001',
            '0002',
            '0003',
            '0001',
            '0002',
            '0001',
            '0002',
            '0001']
        res = guess_type_list(li)
        fLOG(res)
        typstr = str  # unicode#
        if res != (typstr, 8):
            raise Exception(f"different: {res}")

    def test_load_content_file_with_encoding(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        file = __file__.replace(".pyc", ".py")
        cont, enc = load_content_file_with_encoding(file)
        assert len(file) > 0

    def test_logfile(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        r = GetLogFile()
        assert not isinstance(r, str  # unicode#
                              )

    def test_get_relative_path(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.dirname(__file__))
        file = os.path.abspath(__file__)
        rel = get_relative_path(fold, file)
        fLOG("-----", rel)

    def test_pprint(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fLOG(dict(a=1, b=3), _pp=True)

    def test_log_options(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fLOG(LogAddPath="temp")
        fLOG(LogPath="###")
        fLOG(LogPath=None, LogAddPath=None)

    def test_guess_machine_parameter(self):
        res = guess_machine_parameter()
        self.assertIsInstance(res, dict)


if __name__ == "__main__":
    unittest.main()
