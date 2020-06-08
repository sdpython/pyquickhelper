"""
@file
@brief Simplified function versions.
"""
import os


_preamble = '''
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
'''

_custom_preamble = """\n
\\usepackage[all]{xy}
\\newcommand{\\vecteur}[2]{\\pa{#1,\\dots,#2}}
\\newcommand{\\N}[0]{\\mathbb{N}}
\\newcommand{\\indicatrice}[1]{\\mathbf{1\\!\\!1}_{\\acc{#1}}}
\\newcommand{\\infegal}[0]{\\leqslant}
\\newcommand{\\supegal}[0]{\\geqslant}
\\newcommand{\\ensemble}[2]{\\acc{#1,\\dots,#2}}
\\newcommand{\\fleche}[1]{\\overrightarrow{ #1 }}
\\newcommand{\\intervalle}[2]{\\left\\{#1,\\cdots,#2\\right\\}}
\\newcommand{\\independant}[0]
{\\;\\makebox[3ex]{\\makebox[0ex]{\\rule[-0.2ex]{3ex}{.1ex}}\\!\\!\\!\\!\\makebox[.5ex][l]
{\\rule[-.2ex]{.1ex}{2ex}}\\makebox[.5ex][l]{\\rule[-.2ex]{.1ex}{2ex}}} \\,\\,}
\\newcommand{\\esp}{\\mathbb{E}}
\\newcommand{\\espf}[2]{\\mathbb{E}_{#1}\\pa{#2}}
\\newcommand{\\var}{\\mathbb{V}}
\\newcommand{\\pr}[1]{\\mathbb{P}\\pa{#1}}
\\newcommand{\\loi}[0]{{\\cal L}}
\\newcommand{\\vecteurno}[2]{#1,\\dots,#2}
\\newcommand{\\norm}[1]{\\left\\Vert#1\\right\\Vert}
\\newcommand{\\norme}[1]{\\left\\Vert#1\\right\\Vert}
\\newcommand{\\dans}[0]{\\rightarrow}
\\newcommand{\\partialfrac}[2]{\\frac{\\partial #1}{\\partial #2}}
\\newcommand{\\partialdfrac}[2]{\\dfrac{\\partial #1}{\\partial #2}}
\\newcommand{\\trace}[1]{tr\\pa{#1}}
\\newcommand{\\sac}[0]{|}
\\newcommand{\\abs}[1]{\\left|#1\\right|}
\\newcommand{\\loinormale}[2]{{\\cal N} \\pa{#1,#2}}
\\newcommand{\\loibinomialea}[1]{{\\cal B} \\pa{#1}}
\\newcommand{\\loibinomiale}[2]{{\\cal B} \\pa{#1,#2}}
\\newcommand{\\loimultinomiale}[1]{{\\cal M} \\pa{#1}}
\\newcommand{\\variance}[1]{\\mathbb{V}\\pa{#1}}
\\newcommand{\\scal}[2]{\\left<#1,#2\\right>}
"""


def sphinx_rst(input="", writer="html", keep_warnings=False,
               directives=None, language="en",
               layout='sphinx', output="output"):
    """
    Converts a string from *RST*
    to *HTML* or *RST* format.

    :param input: text of filename
    :param writer: ``'html'`` for :epkg:`HTML` format,
        ``'rst'`` for :epkg:`RST` format,
        ``'md'`` for :epkg:`MD` format,
        ``'elatex'`` for :epkg:`latex` format,
        ``'doctree'`` to get the doctree, *writer* can also be a tuple
        for custom formats and must be like ``('buider_name', builder_class)``.
    :param keep_warnings: keep_warnings in the final HTML
    :param directives: new directives to add, comma separated values
    :param language: language
    :param layout: ``'docutils'``, ``'sphinx'``, ``'sphinx_body'``, see below.
    :param output: document name, the function adds the extension
    :return: output

    .. cmdref::
        :title: Convert RST document into HTML
        :cmd: -m pyquickhelper sphinx_rst --help

        Converts RST documents into HTML or even RST.
    """
    from ..helpgen import rst2html
    from ..helpgen.default_conf import get_epkg_dictionary
    from ..filehelper import read_content_ufs
    if output:
        ext = os.path.splitext(output)[-1]
        if not ext:
            output += "." + writer
    if len(input) <= 5000 and \
        (input.startswith('http') or
         os.path.exists(input)):
        content = read_content_ufs(input)
    else:
        content = input
    if directives:
        raise NotImplementedError(
            "Cannot specify directives yet.")  # pragma: no cover

    preamble = _preamble + _custom_preamble
    epkg_dictionary = get_epkg_dictionary()

    ht = rst2html(content, writer=writer, keep_warnings=keep_warnings,
                  language=language, layout=layout,
                  document_name=output, imgmath_latex_preamble=preamble,
                  epkg_dictionary=epkg_dictionary)
    ht = ht.replace('src="_images/', 'src="')
    ht = ht.replace('/scripts\\bokeh', '../bokeh_plot\\bokeh')
    ht = ht.replace('/scripts/bokeh', '../bokeh_plot/bokeh')
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(ht)
    return ht
