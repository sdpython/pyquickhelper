"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.markdown_helper import parse_markdown, yield_sphinx_only_markup_for_pipy
from pyquickhelper.helpgen import rst2html


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
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise Exception("IN\n{0}\nOUT:{1}".format(m, str(r)))

        ht = rst2html(content)
        # fLOG(ht)
        assert len(ht) > 0
        spl = content.split("\n")
        r = list(yield_sphinx_only_markup_for_pipy(spl))
        assert len(r) == len(spl)

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
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise Exception("IN\n{0}\nOUT:{1}".format(m, str(r)))

        ht = rst2html(content)
        # fLOG(ht)
        assert len(ht) > 0

        spl = content.split("\n")
        r = list(yield_sphinx_only_markup_for_pipy(spl))
        assert len(r) == len(spl)


if __name__ == "__main__":
    unittest.main()
