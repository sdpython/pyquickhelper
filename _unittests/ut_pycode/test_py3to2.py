"""
@brief      test tree node (time=15s)
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

from src.pyquickhelper.loghelper import fLOG, run_cmd
from src.pyquickhelper.pycode import get_temp_folder, py3to2_convert_tree


class TestPy3to2(unittest.TestCase):

    def test_py3to2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        temp = get_temp_folder(__file__, "temp_py3to2")
        root = os.path.abspath(os.path.dirname(__file__))
        root = os.path.normpath(os.path.join(root, "..", ".."))
        conv = py3to2_convert_tree(root, temp, fLOG=fLOG)

        if len(conv) < 20:
            raise Exception("not enough copied files")

        script = """
            import sys
            sys.path = [ p for p in sys.path if "src" not in p and "ut_" not in p ]
            sys.path.append(r"{0}")
            print ""
            for k in sys.path:
                print k
            import pyquickhelper
            """.replace("            ", "")
        script = script.format(os.path.join(temp, "src"))

        to = os.path.join(temp, "simpletry.py")
        with open(to, "w", encoding="utf8") as f:
            f.write(script)

        pyexe2 = None
        for location in [r"C:\Anaconda2",
                         r"C:\Anaconda",
                         r"C:\WinPython-64bit-2.7.9.3\python-2.7.9.amd64",
                         ]:
            exe = os.path.join(location, "python.exe")
            if os.path.exists(exe):
                pyexe2 = exe
                break

        if pyexe2 is not None:
            cmd = "{0} {1}".format(pyexe2, to)
            out, err = run_cmd(cmd, wait=True)
            if len(err) > 0:
                raise Exception(
                    "conversion did not work:\nOUT\n:{0}\nERR:\n{1}".format(out, err))
        else:
            fLOG("python 2.7 was not found")


if __name__ == "__main__":
    unittest.main()
