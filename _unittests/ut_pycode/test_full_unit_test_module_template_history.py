"""
@brief      test log(time=600s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import time

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

try:
    import jyquickhelper as skip_
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..",
                "..",
                "jyquickhelper",
                "src")))
    if path not in sys.path:
        sys.path.append(path)
    import jyquickhelper as skip_

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder, process_standard_options_for_setup, is_travis_or_appveyor
from src.pyquickhelper.loghelper import git_clone
from src.pyquickhelper import __file__ as pyq_location

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class TestUnitTestFullModuleTemplateHistory(unittest.TestCase):

    @unittest.skipIf(sys.version_info[0] == 2, reason="does not work on Python 2")
    def test_full_unit_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if __name__ != "__main__" or not os.path.exists("temp2_full_unit_test_history"):
            temp_ = get_temp_folder(__file__, "temp2_full_unit_test_history")
            temp = os.path.join(temp_, "python3_module_template")
            if not os.path.exists(temp):
                os.mkdir(temp)
            git_clone(temp, "github.com", "sdpython",
                      "python3_module_template")
            wait = 0
            while not os.path.exists(os.path.join(temp, "src")) and wait < 5:
                fLOG("wait", wait)
                time.sleep(1000)
                wait += 1
        else:
            temp = os.path.abspath(os.path.join(
                "temp2_full_unit_test", "python3_module_template"))
        root = temp
        setup = os.path.join(root, "setup.py")
        pyq = os.path.join(os.path.dirname(src.pyquickhelper.__file__), "..")

        if "src" in sys.modules:
            memo = sys.modules["src"]
            del sys.modules["src"]
        else:
            memo = None

        def skip_function(name, code, duration):
            return "test_example" not in name

        pyq_folder = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(pyq_location), '..')))

        stdout = StringIO()
        stderr = StringIO()
        fLOG("setup", setup)
        thispath = os.path.abspath(os.path.dirname(__file__))
        thispath = os.path.normpath(os.path.join(thispath, "..", "..", "src"))
        import jyquickhelper
        jyqpath = os.path.abspath(os.path.join(
            os.path.split(jyquickhelper.__file__)[0], ".."))

        fLOG("unit tests", root)
        for command in ["build_history"]:
            fLOG("#######################################################")
            fLOG("#######################################################")
            fLOG(command)
            fLOG("#######################################################")
            rem = False
            PYTHONPATH = os.environ.get("PYTHONPATH", "")
            sep = ";" if sys.platform.startswith("win") else ":"
            new_val = PYTHONPATH + sep + thispath + sep + jyqpath
            os.environ["PYTHONPATH"] = new_val.strip(sep)
            log_lines = []

            def logging_custom(*l, **p):
                log_lines.append(l)
            lcmd = command.split() if ' ' in command else [command]
            stdout2 = StringIO()
            stderr2 = StringIO()

            r = process_standard_options_for_setup(
                lcmd, setup, "python3_module_template",
                port=8067, requirements=["pyquickhelper"], blog_list=None,
                fLOG=logging_custom, additional_ut_path=[pyq, (root, True)],
                skip_function=skip_function, coverage_options={
                    "disable_coverage": True},
                hook_print=False, stdout=stdout2, stderr=stderr2, use_run_cmd=True)

            vout = stdout2.getvalue()
            stdout.write(vout)
            verr = stderr2.getvalue()
            stderr.write(verr)
            if rem:
                del sys.path[sys.path.index(thispath)]
            os.environ["PYTHONPATH"] = PYTHONPATH

        fLOG("#######################################################")
        fLOG("#######################################################")
        fLOG("OUT:\n", stdout.getvalue())
        fLOG("ERR:\n", stderr.getvalue())

        if memo is not None:
            sys.modules["src"] = memo


if __name__ == "__main__":
    unittest.main()
