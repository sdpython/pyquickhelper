"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import ExtTestCase, ignore_warnings
from pyquickhelper.helpgen import rst2html
from pyquickhelper.pycode import get_temp_folder


class TestDocBug(ExtTestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_param_sphinx(self):
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
