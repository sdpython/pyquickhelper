"""
@brief      test tree node (time=20s)
"""
import os
import unittest
import time
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_travis
from pyquickhelper.loghelper.time_helper import repeat_execution, repeat_script_execution


class TestTimeHelper(ExtTestCase):

    def test_repeat_execution(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        ct = [0]

        def fct_count():
            ct[0] += 1
            return ct[0]

        res = repeat_execution(fct_count, verbose=1, fLOG=fLOG)
        self.assertEqual(res, [1, 2, 3, 4, 5])

    def test_repeat_execution_exc(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        ct = [0]

        def fct_count():
            raise RuntimeError("issue")

        res = repeat_execution(fct_count, verbose=1, fLOG=fLOG, exc=False,
                               stop_after_second=2)
        self.assertEmpty(res)

    def test_repeat_execution_sleep(self):
        ct = [0]

        def fct_count():
            ct[0] += 1
            time.sleep(1.5)
            return ct[0]

        res = repeat_execution(fct_count)
        self.assertLess(len(res), 4)

    @skipif_travis("stuck")
    def test_repeat_execution_script(self):
        temp = get_temp_folder(__file__, "temp_repeat_execution_script")
        outfile = os.path.join(temp, "out.txt")
        errfile = os.path.join(temp, "err.txt")
        script = os.path.join(temp, "script.py")
        with open(script, "w") as f:
            f.write("print('machine')\n")

        res = repeat_script_execution(script, outfile=outfile, errfile=errfile,
                                      stop_after_second=3)

        with open(outfile, "r") as f:
            out = f.read()
        self.assertIn("machine\n", res)
        self.assertIn("[repeat_script_execution]", out)
        self.assertIn("iter=1\n", out)
        self.assertIn("machine\n", out)


if __name__ == "__main__":
    unittest.main()
