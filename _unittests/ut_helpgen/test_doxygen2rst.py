"""
@brief      test log(time=8s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen.utils_sphinx_doc import migrating_doxygen_doc
from src.pyquickhelper.helpgen.utils_sphinx_doc_helpers import process_var_tag

if sys.version_info[0] == 2:
    from codecs import open


class TestDoxygen2rst (unittest.TestCase):

    def test_doxygen2rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            #~ # not test on python 2
            return

        file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "myexample2.py")
        with open(file, "r", encoding="utf8") as f:
            content = f.read()

        res = migrating_doxygen_doc(
            content, __file__, debug=False, silent=True, log=False)
        rst = res[1]
        lines = rst.split("\n")
        eq = [_ for _ in lines if "x^2" in _ and ":math:" not in _]
        for e in eq:
            if e.lstrip() == e:
                raise ValueError(
                    "no indentation: -{}-\nCONTENT\n{}".format(e, rst))

    def test_process_var_tag(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        test_string = """
        This is the documentation for this class.

        @var   pa   an example of an attribute.

        Inline :math:`x^2 + y + z`. Another equation to test:

        .. math::

            x^2 + y

        .. math::

            \\sum_{i=1}^n x^2
        """
        rst = process_var_tag(test_string, True)
        exp = """
        This is the documentation for this class.

        +-----------+-----------------------------+
        | attribute | meaning                     |
        +===========+=============================+
        | pa        | an example of an attribute. |
        +-----------+-----------------------------+

        Inline :math:`x^2 + y + z`. Another equation to test:

        .. math::

            x^2 + y

        .. math::

            \\sum_{i=1}^n x^2
        """
        self.assertEqual(rst.strip("\n ").replace(" ", ""),
                         exp.strip("\n ").replace(" ", ""))

    def test_doxygen2rst_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            #~ # not test on python 2
            return

        file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "completion.py")
        with open(file, "r", encoding="utf8") as f:
            content = f.read()

        res = migrating_doxygen_doc(
            content, __file__, debug=False, silent=True, log=False)
        rst = res[1]
        lines = rst.split("\n")
        eq = [_ for _ in lines if "@param" in _ or "@see" in _]
        for e in eq:
            if e.lstrip() == e:
                raise ValueError(
                    "no indentation: -{}-\nCONTENT\n{}".format(e, rst))


if __name__ == "__main__":
    unittest.main()
