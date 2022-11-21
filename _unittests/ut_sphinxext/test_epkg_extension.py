"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.helpgen import rst2html
from pyquickhelper.cli.cli_helper import clean_documentation_for_cli


class TestEpkgExtension(ExtTestCase):

    @skipif_appveyor("logging error")
    def test_epkg_module(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas` aaftera
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content, writer="custom", keep_warnings=True,
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

    @skipif_appveyor("logging error")
    def test_epkg_module_twice(self):
        from docutils import nodes as skip_

        content = """
                    abeforea :epkg:`pandas` aaftera

                    test a directive
                    ================

                    abeforea :epkg:`pandas` aaftera
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content, writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': 'http://pandas.pydata.org/pandas-docs/stable/generated/', })
        self.assertIn(
            "http://pandas.pydata.org/pandas-docs/stable/generated/", html)

    @skipif_appveyor("logging error")
    def test_epkg_sub(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame.to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content, writer="custom", keep_warnings=True,
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
            raise Exception(f"\n**{spl}**\n----\n{html}")

        t1 = 'href="http://www.7-zip.org/"'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="http://pandas.pydata.org/pandas-docs/stable/generated/DataFrame.to_html.html"'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging error")
    def test_epkg_function(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        def pandas_link(input):
            return "MYA", "|".join(input.split(":"))

        html = rst2html(content, writer="custom", keep_warnings=True,
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
            raise Exception(f"\n**{spl}**\n----\n{html}")

        t1 = 'href="http://www.7-zip.org/"'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html"'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging error")
    def test_epkg_class(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        class pandas_link:
            def __call__(self, input):
                return "MYA", "|".join(input.split(":"))

        html = rst2html(content, writer="custom", keep_warnings=True,
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
            raise Exception(f"\n**{spl}**\n----\n{html}")

        t1 = 'href="http://www.7-zip.org/"'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html"'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging error")
    def test_epkg_function_string(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas:DataFrame:to_html` aaftera

                    7za :epkg:`7z` 7zb
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content, writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx",
                        epkg_dictionary={'pandas': ('http://pandas.pydata.org/pandas-docs/stable/generated/',
                                                    ('http://pandas.pydata.org/pandas-docs/stable/generated/{0}.html', 1),
                                                    ('pyquickhelper.sphinxext._private_for_unittest._private_unittest', None)),
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
            raise Exception(f"\n**{spl}**\n----\n{html}")

        t1 = 'href="http://www.7-zip.org/"'
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="pandas|DataFrame|to_html"'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging error")
    def test_epkg_function_long_link(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    `one link on two lines <http://first.part/
                    second part>`_.
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content,
                        writer="custom", keep_warnings=True,
                        directives=None, layout="sphinx")

        t1 = 'href="http://first.part/secondpart"'
        if t1 not in html:
            raise Exception(html)

        t1 = '>one link on two lines</a>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_epkg_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging error")
    def test_epkg_module_clean(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :epkg:`pandas` aaftera
                    """.replace("                    ", "")

        res = clean_documentation_for_cli(content, cleandoc=("epkg", "link"))
        self.assertIn('abeforea `pandas` aaftera', res)


if __name__ == "__main__":
    unittest.main()
