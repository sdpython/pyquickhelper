"""
@brief      test tree node (time=50s)
"""

import sys
import os
import unittest
import re
import shutil
import warnings
import pandas

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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.pycode.venv_helper import create_virtual_env, run_venv_script
from src.pyquickhelper.helpgen.markdown_helper import yield_sphinx_only_markup_for_pipy


class TestReadme(unittest.TestCase):

    def test_venv_docutils08_readme(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.dirname(os.path.abspath(__file__))
        readme = os.path.join(fold, "..", "..", "README.rst")
        assert os.path.exists(readme)
        with open(readme, "r", encoding="utf8") as f:
            content = f.read()

        temp = get_temp_folder(__file__, "temp_readme")
        out = create_virtual_env(temp, fLOG=fLOG, packages=["docutils==0.8"])
        outfile = os.path.join(temp, "conv_readme.html")

        script = ["from docutils import core",
                  "import io",
                  'from docutils.readers.standalone import Reader',
                  'from docutils.parsers.rst import Parser',
                  'from docutils.parsers.rst.directives.images import Image',
                  'from docutils.parsers.rst.directives import _directives',
                  'from docutils.writers.html4css1 import Writer',
                  "from docutils.languages import _languages",
                  "from docutils.languages import en, fr",
                  "_languages['en'] = en",
                  "_languages['fr'] = fr",
                  "_directives['image'] = Image",
                  "with open('{0}', 'r', encoding='utf8') as g: s = g.read()".format(
                      readme.replace("\\", "\\\\")),
                  "settings_overrides = {'output_encoding': 'unicode', 'doctitle_xform': True, 'initial_header_level': 2, 'warning_stream': io.StringIO()}",
                  "parts = core.publish_parts(source=s, parser=Parser(), reader=Reader(), source_path=None, destination_path=None, writer=Writer(), settings_overrides=settings_overrides)",
                  "with open('{0}', 'w', encoding='utf8') as f: f.write(parts['whole'])".format(
                      outfile.replace("\\", "\\\\")),
                  ]

        file_script = os.path.join(temp, "testreadme.py")
        with open(file_script, "w") as f:
            f.write("\n".join(script))

        out = run_venv_script(temp, file_script, fLOG=fLOG, file=True)
        with open(outfile, "r", encoding="utf8") as h:
            content = h.read()

        if "System Message" in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
