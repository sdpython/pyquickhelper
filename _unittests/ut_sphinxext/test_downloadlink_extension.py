"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from distutils.version import StrictVersion
import sphinx

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

from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import process_downloadlink_role
from docutils.parsers.rst.roles import register_canonical_role

if sys.version_info[0] == 2:
    from codecs import open


class TestDownloadlinkExtension(ExtTestCase):

    def test_post_parse_sn(self):
        register_canonical_role("downloadlink", process_downloadlink_role)

    def get_name(self):
        this = os.path.dirname(__file__)
        name = "test_rst_builder.py"
        dest = os.path.join(this, name)
        return dest.replace("\\", "/")

    @unittest.skipIf(StrictVersion(sphinx.__version__) < StrictVersion('1.8'),
                     reason="DownloadFiles not available in 1.7")
    def test_downloadlink_rst(self):
        name = self.get_name()
        content = """
                    :downloadlink:`rst::http://f.html`
                    :downloadlink:`rst::{0}`
                    :downloadlink:`{0} <rst::{0}>`
                    """.replace("                    ", "").format(name)

        out = rst2html(content,
                       writer="rst", keep_warnings=True,
                       directives=None)

        out = out.replace("\n", " ")
        self.assertNotIn('Unknown interpreted text role', out)
        self.assertIn(
            ':downloadlink:`test_rst_builder.py', out)
        self.assertNotIn("test_rst_builder.py>`test_rst_builder.py", out)
        temp = get_temp_folder(__file__, "temp_downloadlink_rst")
        with open(os.path.join(temp, "out.rst"), "w", encoding="utf8") as f:
            f.write(out)

    @unittest.skipIf(StrictVersion(sphinx.__version__) < StrictVersion("1.8"),
                     reason="DownloadFiles not available in 1.7")
    def test_downloadlink_md(self):
        name = self.get_name()
        content = """
                    :downloadlink:`gggg <md::{0}>`
                    """.replace("                    ", "").format(name)

        out = rst2html(content,
                       writer="md", keep_warnings=True,
                       directives=None)

        self.assertIn("test_rst_builder.py", out)
        self.assertNotIn('Unknown interpreted text role', out)
        temp = get_temp_folder(__file__, "temp_downloadlink_rst")
        with open(os.path.join(temp, "out.rst"), "w", encoding="utf8") as f:
            f.write(out)

    @unittest.skipIf(StrictVersion(sphinx.__version__) < StrictVersion("1.8"),
                     reason="DownloadFiles not available in 1.7")
    def test_downloadlink_html(self):
        name = self.get_name()
        content = """
                    :downloadlink:`html::{0}`
                    """.replace("                    ", "").format(name)

        out = rst2html(content,
                       writer="html", keep_warnings=True,
                       directives=None)

        self.assertNotIn("Unable to find 'html:test_rst_builder.py'", out)
        self.assertNotIn('Unknown interpreted text role', out)
        self.assertIn("test_rst_builder.py", out)
        temp = get_temp_folder(__file__, "temp_downloadlink_rst")
        with open(os.path.join(temp, "out.rst"), "w", encoding="utf8") as f:
            f.write(out)


if __name__ == "__main__":
    unittest.main()