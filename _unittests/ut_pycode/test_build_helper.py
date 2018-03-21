"""
@brief      test tree node (time=2s)
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
from src.pyquickhelper.pycode.build_helper import private_path_choice, private_replacement_


class TestBuildHelper(unittest.TestCase):

    def test_private_path_choice(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        sep = '\\' if sys.platform.startswith('win') else '/'
        current = '%current%' if sys.platform.startswith('win') else '~'
        exps = [sep.join([current, '..', 'mod', 'src']),
                sep.join([current, '..', 'mod']),
                sep.join([current, '..', 'mod', 'build', 'lib'])]
        self.assertEqual(private_path_choice('mod'), exps[0])
        self.assertEqual(private_path_choice('ROOTmod'), exps[1])
        self.assertEqual(private_path_choice('BLIBmod'), exps[2])

    def test_private_replacement_(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = private_replacement_('__ADDITIONAL_LOCAL_PATH__',
                                   paths=['a'], key="__ADDITIONAL_LOCAL_PATH__")
        exp = ';%current%\\..\\a\\src' if sys.platform.startswith(
            'win') else ';~/../a/src'
        self.assertEqual(res, exp)


if __name__ == "__main__":
    unittest.main()
