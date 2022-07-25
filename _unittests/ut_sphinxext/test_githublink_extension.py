"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import githublink_role
from docutils.parsers.rst.roles import register_canonical_role


class TestGitHubLinkExtension(ExtTestCase):

    def test_post_parse_sn(self):
        register_canonical_role("githublink", githublink_role)

    def test_githublink(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :githublink:`j|py`

                    after

                    :githublink:`j`

                    again

                    :githublink:`j|py|84`

                    again

                    :githublink:`j|myfile.ipynb|83`

                    again

                    :githublink:`j|myfile.ipynb|*`

                    again

                    :githublink:`%|myfile.ipynb|*`

                    this code shoud appear
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, document_name="string",
                        githublink_options=dict(user="sdpython", project="pyquickhelper", anchor="ANCHOR"))

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/string.py#L7"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/string#L11"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/string.py#L84"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/myfile.ipynb#L83"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/myfile.ipynb"
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="https://github.com/sdpython/pyquickhelper/blob/master/myfile.ipynb">ANCHOR</a></p>'
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_githublink")
        with open(os.path.join(temp, "out_githublink.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_githublink_function(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :githublink:`j|py`

                    after

                    :githublink:`j`

                    again

                    :githublink:`j|py|84`

                    again

                    :githublink:`j|myfile.ipynb|83`

                    again

                    :githublink:`j|myfile.ipynb|*`

                    this code shoud appear
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        def processor(path, lineno):
            return f"[{path}:{lineno}]", "my_sources"

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None,
                        githublink_options=dict(processor=processor),
                        document_name="string")

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "[string.py:7]"
        if t1 not in html:
            raise Exception(html)

        t1 = "[string:11]"
        if t1 not in html:
            raise Exception(html)

        t1 = "[string.py:84]"
        if t1 not in html:
            raise Exception(html)

        t1 = "[myfile.ipynb:83]"
        if t1 not in html:
            raise Exception(html)

        t1 = "[myfile.ipynb:None]"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_githublink")
        with open(os.path.join(temp, "out_githublink.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_githublink_doc(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :githublink:`j|rst-doc|84`

                    this code shoud appear
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, document_name="string",
                        githublink_options=dict(user="sdpython", project="pyquickhelper", anchor="ANCHOR"))

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/_doc/sphinxdoc/source/string.rst#L84"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_githublink_doc")
        with open(os.path.join(temp, "out_githublink.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_githublink_binaries(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    again

                    :githublink:`%|myfile.pyd|*`

                    again

                    :githublink:`%|myfile2.so|*`

                    this code shoud appear
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=None, document_name="string",
                        githublink_options=dict(user="sdpython", project="pyquickhelper", anchor="ANCHOR"))
        html = html.replace("http://docutils.sourceforge.net/", "")

        t1 = ".pyd"
        if t1 in html:
            raise Exception(html)

        t1 = ".so"
        if t1 in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/blob/master/"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_githublink_binaries")
        with open(os.path.join(temp, "out_githublink.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
