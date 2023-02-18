"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
try:
    from sphinx.deprecation import RemovedInSphinx70Warning
except ImportError:
    RemovedInSphinx70Warning = UserWarning
from pyquickhelper.helpgen.markdown_helper import parse_markdown, yield_sphinx_only_markup_for_pipy
from pyquickhelper.helpgen import rst2html
from pyquickhelper.pycode import ignore_warnings


class TestHelperMarkdown(unittest.TestCase):

    @ignore_warnings(RemovedInSphinx70Warning)
    def test_parse_markdown(self):
        r = parse_markdown("**r**")
        if str(r).strip("\n\r ") != "<p><strong>r</strong></p>":
            raise AssertionError([str(r)])

    @ignore_warnings(RemovedInSphinx70Warning)
    def test_parse_readme(self):
        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "..", "..", "README.rst")
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()
        r = parse_markdown(content)
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise AssertionError(f"IN\n{m}\nOUT:{str(r)}")

        ht = rst2html(content)
        # fLOG(ht)
        assert len(ht) > 0
        spl = content.split("\n")
        r = list(yield_sphinx_only_markup_for_pipy(spl))
        assert len(r) == len(spl)

    @ignore_warnings(RemovedInSphinx70Warning)
    def test_parse_readme_cb(self):
        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "data", "README.rst")
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()
        r = parse_markdown(content)
        if "<p>.. _l-README:</p>" not in str(r):
            m = [ord(c) for c in content]
            m = ",".join(str(_) for _ in m[:20])
            raise AssertionError(f"IN\n{m}\nOUT:{str(r)}")

        ht = rst2html(content)
        # fLOG(ht)
        assert len(ht) > 0

        spl = content.split("\n")
        r = list(yield_sphinx_only_markup_for_pipy(spl))
        assert len(r) == len(spl)


if __name__ == "__main__":
    unittest.main()
