# -*- coding: utf-8 -*-
"""
@brief      test log(time=38s)
"""

import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen import rst2html
from pyquickhelper.pycode import ExtTestCase, get_temp_folder, skipif_travis, skipif_appveyor


class TestDocPage(ExtTestCase):

    preamble = '''
            \\usepackage{etex}
            \\usepackage{fixltx2e} % LaTeX patches, \\textsubscript
            \\usepackage{cmap} % fix search and cut-and-paste in Acrobat
            \\usepackage[raccourcis]{fast-diagram}
            \\usepackage{titlesec}
            \\usepackage{amsmath}
            \\usepackage{amssymb}
            \\usepackage{amsfonts}
            \\usepackage{graphics}
            \\usepackage{epic}
            \\usepackage{eepic}
            %\\usepackage{pict2e}
            %%% Redefined titleformat
            \\setlength{\\parindent}{0cm}
            \\setlength{\\parskip}{1ex plus 0.5ex minus 0.2ex}
            \\newcommand{\\hsp}{\\hspace{20pt}}
            \\newcommand{\\acc}[1]{\\left\\{#1\\right\\}}
            \\newcommand{\\cro}[1]{\\left[#1\\right]}
            \\newcommand{\\pa}[1]{\\left(#1\\right)}
            \\newcommand{\\R}{\\mathbb{R}}
            \\newcommand{\\HRule}{\\rule{\\linewidth}{0.5mm}}
            %\\titleformat{\\chapter}[hang]{\\Huge\\bfseries\\sffamily}{\\thechapter\\hsp}{0pt}{\\Huge\\bfseries\\sffamily}
            '''.replace("            ", "")

    custom_preamble = """\n
            \\usepackage[all]{xy}
            \\newcommand{\\norm}[1]{\\left\\Vert#1\\right\\Vert}
            """.replace("            ", "")

    @skipif_travis("latex is not installed")
    @skipif_appveyor("latex is not installed")
    def test_doc_page(self):
        temp = get_temp_folder(__file__, "temp_doc_page")
        preamble = TestDocPage.preamble + TestDocPage.custom_preamble
        this = os.path.abspath(os.path.dirname(__file__))
        rst = os.path.join(this, "..", "..", "_doc", "sphinxdoc",
                           "source", "documentation_example.rst")
        content = self.read_file(rst)

        writer = 'html'
        ht = rst2html(content, writer=writer, layout="sphinx", keep_warnings=True,
                      imgmath_latex_preamble=preamble, outdir=temp,
                      load_bokeh=True,
                      epkg_dictionary={'pep8': 'https://www.python.org/dev/peps/pep-0008/'})
        ht = ht.replace('src="_images/', 'src="')
        ht = ht.replace('/scripts\\bokeh', '../bokeh_plot\\bokeh')
        ht = ht.replace('/scripts/bokeh', '../bokeh_plot/bokeh')
        rst = os.path.join(temp, f"out.{writer}")
        self.write_file(rst, ht)

        # Tests the content.
        self.assertNotIn('runpythonerror', ht)
        self.assertIn("https://www.python.org/dev/peps/pep-0008/", ht)


if __name__ == "__main__":
    unittest.main()
