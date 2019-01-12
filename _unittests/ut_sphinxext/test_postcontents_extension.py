"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import RunPythonDirective
from src.pyquickhelper.sphinxext import PostContentsDirective


class TestPostContentsExtension(unittest.TestCase):

    content = """
                    Contents:

                    .. contents::
                        :local:

                    Title outside
                    +++++++++++++

                    .. runpython::
                        :rst:

                        print("some text")
                        print()
                        print("Title inside")
                        print("++++++++++++")
                        print()
                        print("Title inside2")
                        print("^^^^^^^^^^^^^")
                        print()
                        print("some new text")
                    """.replace("                    ", "")

    def test_post_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("runpython", RunPythonDirective)
        directives.register_directive("postcontents", PostContentsDirective)

    def test_contents(self):
        """
        this test also test the extension runpython
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        content = TestPostContentsExtension.content

        rst = rst2html(content,  # fLOG=fLOG,
                       # layout="sphinx",
                       writer="rst", keep_warnings=True)

        if "* :ref:`title-outside`" not in rst:
            raise Exception(rst)
        if "* :ref:`title-inside`" in rst:
            raise Exception("\n" + rst)

    def test_postcontents(self):
        """
        this test also test the extension runpython
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        content = TestPostContentsExtension.content.replace(
            "contents", "postcontents")

        # 1

        rst = rst2html(content,  # fLOG=fLOG,
                       # layout="sphinx",
                       writer="rst", keep_warnings=True)

        if "* :ref:`title-outside`" in rst:
            raise Exception("\n" + rst)
        if "* :ref:`title-inside`" in rst:
            raise Exception("\n" + rst)

        # 2

        rst = rst2html(content,  # fLOG=fLOG,
                       layout="sphinx",
                       writer="html", keep_warnings=True)

        temp = get_temp_folder(__file__, "temp_postcontents")
        with open(os.path.join(temp, "postcontents.html"), "w", encoding="utf-8") as f:
            f.write(rst)
        if '<li><p><a class="reference internal" href="#title-inside2" title="Title inside2">Title inside2</a></p></li>' not in rst:
            raise Exception("\n" + rst)

        # 3

        rst = rst2html(content,  # fLOG=fLOG,
                       layout="sphinx",
                       writer="rst", keep_warnings=True)

        if "* :ref:`title-outside`" not in rst:
            raise Exception(rst)
        if "* :ref:`title-inside`" not in rst:
            raise Exception(rst)


if __name__ == "__main__":
    unittest.main()
