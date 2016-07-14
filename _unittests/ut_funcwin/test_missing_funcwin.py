"""
@brief      test log(time=1s)
"""
import os
import sys
import unittest
import io


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
from src.pyquickhelper.funcwin.default_functions import _clean_name_variable, _get_format_zero_nb_integer, file_list, file_split


class TestMissingFuncWin (unittest.TestCase):

    def test_missing_funcwin_file_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert _clean_name_variable("s-6") == "s_6"
        assert _get_format_zero_nb_integer(5006) == "%04d"
        ioout = io.StringIO()
        file_list(os.path.abspath(os.path.dirname(__file__)), out=ioout)
        s = ioout.getvalue()
        assert len(s) > 0

    def test_missing_funcwin_file_split(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert _clean_name_variable("s-6") == "s_6"
        assert _get_format_zero_nb_integer(5006) == "%04d"
        ioout = [io.StringIO(), io.StringIO()]
        file_split(os.path.abspath(__file__), out=ioout, header=True)
        ioout = [io.StringIO(), io.StringIO()]
        s1 = ioout[0].getvalue()
        s2 = ioout[0].getvalue()
        self.assertEqual(s1[:5], s2[:5])
        nb = file_split(os.path.abspath(__file__), out=ioout, header=False)
        size = os.stat(os.path.abspath(__file__)).st_size
        sa = 0
        for l in ioout:
            s = l.getvalue()
            assert len(s) > 0
            sa += len(s)
        assert 0 < sa <= size
        if sa not in (size, size - nb - 1, size - nb, size - 1):
            raise Exception("{0} != {1}, nb={2}".format(sa, size, nb))

if __name__ == "__main__":
    unittest.main()
