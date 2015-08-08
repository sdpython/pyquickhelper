"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil


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
from src.pyquickhelper.helpgen.markdown_helper import parse_markdown
from src.pyquickhelper.helpgen import rst2html

if sys.version_info[0] == 2:
    from codecs import open


class TestHelperMarkdown(unittest.TestCase):

    def test_parse_markdown(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        r = parse_markdown("**r**")
        if str(r).strip("\n\r ") != "<p><strong>r</strong></p>":
            raise Exception([str(r)])

    def test_parse_readme(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "..", "..", "README.rst")
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()
        r = parse_markdown(content)
        if sys.version_info[0] == 2:
            return
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise Exception("IN\n{0}\nOUT:{1}".format(m, str(r)))

        ht = rst2html(content)
        fLOG(ht)

    def test_parse_readme_cb(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "data", "README.rst")
        fLOG(readme)
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()
        r = parse_markdown(content)
        if sys.version_info[0] == 2:
            return
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise Exception("IN\n{0}\nOUT:{1}".format(m, str(r)))

        ht = rst2html(content)
        fLOG(ht)

if __name__ == "__main__":
    unittest.main()
