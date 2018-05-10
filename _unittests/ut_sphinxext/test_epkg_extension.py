"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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

if sys.version_info[0] == 2:
    from codecs import open


class TestEpkgExtension(unittest.TestCase):

    def test_epkg_module(self):
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
                    test a directive
                    ================

                    abeforea :epkg:`pandas` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1))
                                         })

        t1 = "abeforea"
        if t1 not in html:
            raise Exception(html)

        t1 = "aftera"
        if t1 not in html:
            raise Exception(html)

        t1 = "http://pandas.pydata.org/pandas-docs/stable/generated/"
        if t1 not in html:
            raise Exception(html)

    def test_epkg_sub(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_sub not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame.to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1)),
                                         '7z': "http://www.7-zip.org/", })

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

        t1 = 'href="http://www.7-zip.org/">7z'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="http://pandas.pydata.org/pandas-docs/stable/generated/DataFrame.to_html.html">pandas.DataFrame.to_html'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_epkg_function(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_function not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        def pandas_link(input):
            return "MYA", "|".join(input.split(":"))

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1),
                                                    pandas_link),
                                         '7z': "http://www.7-zip.org/", })

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

        t1 = 'href="http://www.7-zip.org/">7z'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html">MYA</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_epkg_class(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_class not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        class pandas_link:
            def __call__(self, input):
                return "MYA", "|".join(input.split(":"))

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1),
                                                    pandas_link),
                                         '7z': "http://www.7-zip.org/", })

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

        t1 = 'href="http://www.7-zip.org/">7z'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html">MYA</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_epkg_function_string(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_function_string not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1),
                                                    ('src.pyquickhelper.sphinxext._private_for_unittest._private_unittest', None)),
                                         '7z': "http://www.7-zip.org/", })

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

        t1 = 'href="http://www.7-zip.org/">7z'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html">MYA</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_epkg_function_long_link(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_epkg_function_string not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    `one link on two lines <http://first.part/
                    second part>`_.
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx")

        t1 = 'href="http://first.part/secondpart">one link on two lines</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
