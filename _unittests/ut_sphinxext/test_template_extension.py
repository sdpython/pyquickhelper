"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import python_link_doc


class TestTemplateExtension(unittest.TestCase):

    def test_python_link_doc(self):
        link = python_link_doc("os")
        self.assertEqual(
            link,
            "`os <https://docs.python.org/3/library/os.html>`_")
        link = python_link_doc("os", "getcwd")
        self.assertEqual(
            link,
            "`os.getcwd <https://docs.python.org/3/library/os.html#os.getcwd>`_")

    def test_tpl_inline(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :tpl:`onetmpl,p1='valstr',p2=4` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        tpl_template={'onetmpl': '{{p1}}..{{p2}}'})

        t1 = "abeforea"
        if t1 not in html:
            raise Exception(html)

        t1 = "aftera"
        if t1 not in html:
            raise Exception(html)

        t1 = "valstr..4"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_tpl_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_tpl_inline_url(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :tpl:`url,name='zoo',obj='boo'` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        tpl_template={'url': '`{{name}} <http://{{obj}}>`_'})

        t1 = "abeforea"
        if t1 not in html:
            raise Exception(html)

        t1 = "aftera"
        if t1 not in html:
            raise Exception(html)

        spl = html.split("abeforea")[-1].split("aftera")[0]

        t1 = "`"
        if t1 in html:
            raise Exception("\n**{0}**\n----\n{1}".format(spl, html))

        t1 = 'href="http://boo"'
        if t1 not in html:
            raise Exception(html)

        t1 = '>zoo</a> aaftera</p>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_tpl_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_tpl_inline_function(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :tpl:`py,m='io'` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        tpl_template={'py': python_link_doc})

        t1 = "abeforea"
        if t1 not in html:
            raise Exception(html)

        t1 = "aftera"
        if t1 not in html:
            raise Exception(html)

        spl = html.split("abeforea")[-1].split("aftera")[0]

        t1 = "`"
        if t1 in html:
            raise Exception("\n**{0}**\n----\n{1}".format(spl, html))

        t1 = 'href="https://docs.python.org/3/library/io.html"'
        if t1 not in html:
            raise Exception(html)

        t1 = '>io</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_tpl_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
