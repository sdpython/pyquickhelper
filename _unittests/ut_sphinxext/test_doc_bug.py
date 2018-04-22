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
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.pycode import get_temp_folder


class TestDocBug(unittest.TestCase):

    def test_param_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_module not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    Addition 4

                    :param a: parameter a
                    :param b: parameter b

                    :returns: ``a+b``
                    """.replace("                    ", "")
        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_param_sphinx")
        with open(os.path.join(temp, "out_param_sphinx.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = ":param a:"
        if t1 in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
