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
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase, is_travis_or_appveyor, skipif_azure_macosx
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import CmdRef, CmdRefList
from src.pyquickhelper.sphinxext.sphinx_cmdref_extension import cmdref_node, visit_cmdref_node, depart_cmdref_node


class TestCmdRefExtension(ExtTestCase):

    def test_post_parse_cmdref(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("cmdref", CmdRef)
        directives.register_directive("cmdreflist", CmdRefList)

    def test_cmdref(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: crypt
                        :lid: idcmd3
                        :cmd: src.pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_cmdref")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)
        t1 = "before"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "before"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = '<span class="n">STATUS</span>'
        if t1 not in html:
            raise Exception(html)

    def test_cmdreflist(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a --helpe
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: freg
                        :lid: id3
                        :cmd: src.pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    middle

                    .. cmdreflist::
                        :tag: freg
                        :sort: title

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, layout="sphinx")
        if "admonition-cmdref cmdref_node admonition" not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_cmdreflist")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = '<span class="n">STATUS</span>'
        if t1 not in html:
            raise Exception(html)

        if 'freg0"></a>' in html:
            raise Exception(html)

    def test_cmdref_rename(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: crypt
                        :lid: idcmd3
                        :cmd: encrypt2=src.pyquickhelper.cli.encryption_cli:decrypt

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_cmdref_rename")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "usage: decrypt [-h] [-r REGEX] source dest password"
        if t1 in html:
            raise Exception(html)
        t1 = "usage: encrypt2 [-h] [-r REGEX] source dest password"
        if t1 not in html:
            raise Exception(html)

    def test_cmdref_quote(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: crypt
                        :lid: idcmd3
                        :cmd: src.pyquickhelper.cli.pyq_sync_cli:pyq_sync

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_cmdref_rst")
        with open(os.path.join(temp, "out_cmdref_rst.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "epkg"
        if t1 in html:
            raise Exception(html)
        t1 = "`>_"
        if t1 in html:
            raise Exception(html)

    @skipif_azure_macosx("The Mac OS X backend will not be able to function correctly if Python is not installed as a framework.")
    def test_cmdref_module(self):
        """
        The test fails on MACOSX if it runs from a virtual envrionment.
        See https://github.com/pypa/virtualenv/issues/609,
        https://github.com/pypa/virtualenv/issues/54.
        Or use https://docs.python.org/3/library/venv.html.
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        path = src.__path__
        if isinstance(path, list):
            path = path[0]
        path = os.path.abspath(path)
        self.assertExists(path)
        from docutils import nodes as skip_

        if is_travis_or_appveyor() == "azurepipe" and sys.platform == "darwin":
            import matplotlib as mpl
            mpl.use('TkAgg')

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :cmd: -m pyquickhelper clean_files --help
                        :path: {0}

                        this code shoud appear___

                    after
                    """.replace("                    ", "").format(path)
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_cmdref_rst_module")
        with open(os.path.join(temp, "out_cmdref_rst.html"), "w", encoding="utf8") as f:
            f.write(html)

        self.assertIn("<<<", html)
        self.assertIn("python -m pyquickhelper clean_files --help", html)
        if "usage: clean_files [-h] [-f FOLDER] [-p POSREG] [-n NEGREG] [--op OP]" not in html:
            raise Exception("Unable to find a substring in\n{0}".format(html))


if __name__ == "__main__":
    unittest.main()
