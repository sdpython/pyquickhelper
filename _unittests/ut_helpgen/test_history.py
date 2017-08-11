"""
@brief      test log(time=2s)
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen.sphinx_main_helper import format_history


class TestPaths(unittest.TestCase):

    def test_format_history(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        history = """
                .. _l-history-l:

                =======
                History
                =======

                1.5.???? (2017-??-??)
                =====================

                **Bugfix**

                * `46`: update to Sphinx 1.6
                * `54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_

                **Features**

                * `36`: add support for sphinx-gallery

                1.4.2 (2016-09-18)
                ==================
        """.replace("                ", "")

        temp = get_temp_folder(__file__, "temp_history")
        fsrc = os.path.join(temp, "src.rst")
        fdst = os.path.join(temp, "dst.rst")
        with open(fsrc, "w", encoding="utf-8") as f:
            f.write(history)

        format_history(fsrc, fdst)

        with open(fdst, "r", encoding="utf-8") as f:
            content = f.read()

        expect = """
                .. _l-history-l:

                =======
                History
                =======

                * :releases:`1.5.???? <2017-??-??>`
                * :bug:`46`: update to Sphinx 1.6
                * :bug:`54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_
                * :features:`36`: add support for sphinx-gallery
                * :releases:`1.4.2 <2016-09-18>`
                """.replace("                ", "")

        self.assertEqual(content.strip(" \r\n\t"), expect.strip(" \r\n\t"))


if __name__ == "__main__":
    unittest.main()
