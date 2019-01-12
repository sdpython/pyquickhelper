"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from docutils.parsers.rst import directives

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
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.helpgen import rst2html


class TestCollapseExtension(ExtTestCase):

    def test_collapse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    before

                    .. collapse::

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        temp = get_temp_folder(__file__, "temp_collapse")

        # RST
        html = rst2html(content, writer="rst", keep_warnings=True)

        with open(os.path.join(temp, "out_collapse.rst"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "   this code shoud appear___"
        if t1 not in html:
            raise Exception(html)

        t1 = ".. collapse::"
        if t1 not in html:
            raise Exception(html)

        t1 = "    :legend:"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = ".. collapse::     :legend:"
        if t1 in html:
            raise Exception(html)

        # HTML
        html = rst2html(content, writer="custom", keep_warnings=True)

        with open(os.path.join(temp, "out_collapse.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = 'if (x.style.display === "none")'
        if t1 not in html:
            raise Exception(html)

        t1 = "b.innerText = 'unhide';"
        if t1 not in html:
            raise Exception(html)

    def test_collapse_legend(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    before

                    .. collapse::
                        :legend: ABC/abcd

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        # RST
        html = rst2html(content, writer="rst", keep_warnings=True)

        t1 = ":legend: ABC/abcd"
        if t1 not in html:
            raise Exception(html)

        t1 = ":hide:"
        if t1 in html:
            raise Exception(html)

        # HTML
        html = rst2html(content, writer="custom", keep_warnings=True)

        t1 = "b.innerText = 'abcd';"
        if t1 not in html:
            raise Exception(html)

    def test_collapse_show(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    before

                    .. collapse::
                        :legend: ABC/abcd
                        :hide:

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        # RST
        html = rst2html(content, writer="rst", keep_warnings=True)

        t1 = ":hide:"
        if t1 not in html:
            raise Exception(html)

        # HTML
        html = rst2html(content, writer="custom", keep_warnings=True)

        t1 = ">abcd<"
        if t1 not in html:
            raise Exception(html)

        t1 = '"display:none;"'
        if t1 not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
