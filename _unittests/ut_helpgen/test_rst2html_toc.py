"""
@brief      test log(time=5s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import (
    get_temp_folder, is_travis_or_appveyor, ignore_warnings)
from pyquickhelper.helpgen import rst2html


class TestRst2HtmlToc(unittest.TestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_toc(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return

        if sys.version_info[:2] <= (2, 7):
            # i don't want to fix it for Python 2.7
            return

        content = """
                    ======
                    title1
                    ======

                    0

                    .. contents::
                        :local:

                    1

                    title2
                    ======

                    a

                    title3
                    ------

                    b
        """.replace("                    ", "")

        temp = get_temp_folder(__file__, "temp_rst2html_toc")
        text = rst2html(content, outdir=temp, layout="sphinx", writer="rst")
        ji = os.path.join(temp, "out.rst")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        self.assertIn("* :ref:`title2`", text)

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_autoclass(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return

        if sys.version_info[:2] <= (2, 7):
            # i don't want to fix it for Python 2.7
            return

        content = """
                    ======
                    title1
                    ======

                    .. autoclass:: pyquickhelper.sphinxext.sphinx_runpython_extension.RunPythonDirective
                        :members:

        """.replace("                    ", "")

        temp = get_temp_folder(__file__, "temp_rst2html_autoclass")
        text = rst2html(content, outdir=temp, layout="sphinx", writer="rst")
        ji = os.path.join(temp, "out.rst")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        self.assertIn("* ``:indent:<int>`` to indent the output", text)

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_toctree(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        rst = os.path.join(this, "data", "file_dattente.rst")
        if not os.path.exists(rst):
            raise FileNotFoundError(rst)
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()

        temp = get_temp_folder(__file__, "temp_rst2html_toctree")
        ht = rst2html(content, writer="rst", layout="sphinx")
        ji = os.path.join(temp, "out.rst")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(ht)
        self.assertIn("nonexisting document 'notebooks/file_dattente'>", ht)


if __name__ == "__main__":
    unittest.main()
