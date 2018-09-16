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
from src.pyquickhelper.helpgen import rst2html


class TestPaths(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_format_history_release(self):
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

        temp = get_temp_folder(__file__, "temp_history_release")
        fsrc = os.path.join(temp, "src.rst")
        fdst = os.path.join(temp, "dst.rst")
        with open(fsrc, "w", encoding="utf-8") as f:
            f.write(history)

        format_history(fsrc, fdst, format="release")

        with open(fdst, "r", encoding="utf-8") as f:
            content = f.read()

        expect = """
                .. _l-history-l:

                =======
                History
                =======

                * :release:`1.5.???? <2017-??-??>`
                * :bug:`46`: update to Sphinx 1.6
                * :bug:`54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_
                * :feature:`36`: add support for sphinx-gallery
                * :release:`1.4.2 <2016-09-18>`
                """.replace("                ", "")

        self.assertEqual(content.strip(" \r\n\t"), expect.strip(" \r\n\t"))

    def test_format_history_basic(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        history = """
                .. _l-history-l:

                =======
                History
                =======

                1.5.1234 (2017-12-14)
                =====================

                **Bugfix**

                * `46`: update to Sphinx 1.6 (2017-12-14)
                * `54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_ (2017-12-15)

                **Features**

                * `36`: add support for sphinx-gallery (2017-12-16)

                1.4.2 (2016-09-18)
                ==================
        """.replace("                ", "")

        temp = get_temp_folder(__file__, "temp_history_basic")
        fsrc = os.path.join(temp, "src.rst")
        fdst = os.path.join(temp, "dst.rst")
        with open(fsrc, "w", encoding="utf-8") as f:
            f.write(history)

        format_history(fsrc, fdst, format="basic")

        with open(fdst, "r", encoding="utf-8") as f:
            content = f.read()

        expect = """
                .. _l-history-l:

                =======
                History
                =======

                1.5.1234 (2017-12-14)
                =====================

                **Bugfix**

                * :issue:`46`: update to Sphinx 1.6 (2017-12-14)
                * :issue:`54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_ (2017-12-15)

                **Features**

                * :issue:`36`: add support for sphinx-gallery (2017-12-16)

                1.4.2 (2016-09-18)
                ==================
                """.replace("                ", "")

        self.assertEqual(content.strip(" \r\n\t"), expect.strip(" \r\n\t"))

    def test_format_history_long(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_history_long")
        history = os.path.join(temp, '..', '..', '..', 'HISTORY.rst')
        with open(history, 'r', encoding='utf-8') as f:
            history = f.read()

        fsrc = os.path.join(temp, "src.rst")
        fdst = os.path.join(temp, "dst.rst")
        with open(fsrc, "w", encoding="utf-8") as f:
            f.write(history)

        format_history(fsrc, fdst)

        with open(fdst, "r", encoding="utf-8") as f:
            content = f.read()

        rst = rst2html(content,  # fLOG=fLOG,
                       writer="rst", keep_warnings=True,
                       directives=None, layout="sphinx",
                       extlinks=dict(issue=('https://github.com/sdpython/pyquickhelper/issues/%s', 'issue ')))
        self.assertTrue(rst is not None)
        for line in rst.split('\n'):
            if "remove <SYSTEM MESSAGE> for role ref when" not in line:
                self.assertNotIn('SYSTEM MESSAGE', line)
        self.assertIn('* `issue 136', rst)

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=None, layout="sphinx",
                        extlinks=dict(issue=('https://github.com/sdpython/pyquickhelper/issues/%s', 'issue ')))
        self.assertTrue(html is not None)
        self.assertNotIn('`', html)


if __name__ == "__main__":
    unittest.main()
