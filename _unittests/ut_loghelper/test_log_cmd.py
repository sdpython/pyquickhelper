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

from src.pyquickhelper.loghelper.flog import split_cmp_command, fLOG


class TestLogFunc (unittest.TestCase):

    def test_split_cmp_command(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        assert split_cmp_command("ab cd ef") == ["ab", "cd", "ef"]
        r = split_cmp_command('ab "cd ef"')
        if r != ["ab", 'cd ef']:
            raise Exception(r)
        assert split_cmp_command('"ab cd" ef') == ["ab cd", "ef"]
        assert split_cmp_command('"ab" cd ef') == ["ab", "cd", "ef"]
        assert split_cmp_command('"ab cd ef"') == ["ab cd ef"]

if __name__ == "__main__":
    unittest.main()
