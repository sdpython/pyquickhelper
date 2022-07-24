# -*- coding: utf-8 -*-
"""
@file
@brief Default values for the Sphinx configuration.
"""
import sys


def latex_preamble():
    """
    Default latex preamble.
    """
    preamble = '''
            %% addition by pyquickhelper(1) %%
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
            \\usepackage{media9}
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

            \\renewcommand{\\Verbatim}[1][1]{%
            \\bgroup\\parskip=0pt%
            \\smallskip%
            \\list{}{%
                \\setlength\\parskip{0pt}%
                \\setlength\\itemsep{0ex}%
                \\setlength\\topsep{0ex}%
                \\setlength\\partopsep{0pt}%
                \\setlength\\leftmargin{10pt}%
            }%
            \\item\\MakeFramed{\\FrameRestore}%
            \\tiny
            \\OriginalVerbatim[#1]%
            %% addition by pyquickhelper(1) %%
            }
            '''.replace("            ", "")
    return preamble


def get_epkg_dictionary():
    """
    Returns default dictionary for extension @see fn epkg_role.
    """
    epkg_dictionary = {
        '7z': "https://www.7-zip.org/",
        'ASCII': "https://en.wikipedia.org/wiki/ASCII",
        'Anaconda': 'https://continuum.io/downloads',
        'appveyor': 'https://www.appveyor.com/',
        'autopep8': 'https://github.com/hhatto/autopep8',
        'azure pipeline': 'https://azure.microsoft.com/en-us/services/devops/pipelines/',
        'azure pipelines': 'https://azure.microsoft.com/en-us/services/devops/pipelines/',
        'Azure Pipelines': 'https://azure.microsoft.com/en-us/services/devops/pipelines/',
        'bokeh': 'https://bokeh.pydata.org/en/latest/',
        'builderapi': 'https://www.sphinx-doc.org/en/master/extdev/builderapi.html',
        'bz2': 'https://en.wikipedia.org/wiki/Bzip2',
        'cairosvg': 'https://github.com/Kozea/CairoSVG',
        'chrome': 'https://www.google.com/chrome/',
        'class Sphinx': 'https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107',
        'circleci': 'https://circleci.com/',
        'codecov': 'https://codecov.io/',
        'conda': 'https://github.com/conda/conda',
        'coverage': 'https://pypi.org/project/coverage',
        'cryptography': 'https://cryptography.readthedocs.org/',
        'cssselect2': 'https://cssselect2.readthedocs.io/en/latest/',
        'C++': 'https://en.wikipedia.org/wiki/C%2B%2B',
        'Cython': 'https://cython.org/',
        'dataframe': 'https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html',
        'datetime': 'https://docs.python.org/3/library/datetime.html#datetime-objects',
        'docx': 'https://en.wikipedia.org/wiki/Office_Open_XML',
        'DOT': 'https://www.graphviz.org/doc/info/lang.html',
        'doxygen': 'https://www.doxygen.org/',
        'django': 'https://www.djangoproject.com/',
        'docutils': 'https://docutils.sourceforge.net/',
        'dvipng': 'https://ctan.org/pkg/dvipng?lang=en',
        'FastAPI': 'https://fastapi.tiangolo.com/',
        'format style': 'https://pyformat.info/>`_',
        'FTP': 'https://en.wikipedia.org/wiki/File_Transfer_Protocol',
        'getsitepackages': 'https://docs.python.org/3/library/site.html#site.getsitepackages',
        'GIT': 'https://git-scm.com/',
        'git': 'https://git-scm.com/',
        'Git': 'https://git-scm.com/',
        'github': 'https://github.com/',
        'GitHub': 'https://github.com/',
        'graphviz': 'https://www.graphviz.org/',
        'GraphViz': 'https://www.graphviz.org/',
        'Graphviz': 'https://www.graphviz.org/',
        'html': 'https://en.wikipedia.org/wiki/HTML',
        'HTML': 'https://en.wikipedia.org/wiki/HTML',
        'imgmath': 'https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.imgmath',
        'img2pdf': 'https://gitlab.mister-muffin.de/josch/img2pdf',
        'Inkscape': 'https://inkscape.org/',
        'InkScape': 'https://inkscape.org/',
        'IPython': 'https://en.wikipedia.org/wiki/IPython',
        'Java': 'https://www.java.com/fr/download/',
        'javascript': 'https://en.wikipedia.org/wiki/JavaScript',
        'Jenkins': 'https://jenkins-ci.org/',
        'Jenkins API': 'https://python-jenkins.readthedocs.org/en/latest/api.html',
        'jinja2': 'https://jinja.pocoo.org/docs/',
        'js2py': 'https://github.com/PiotrDabkowski/Js2Py',
        'json': 'https://docs.python.org/3/library/json.html',
        'JSON': 'https://en.wikipedia.org/wiki/JSON',
        'Jupyter': 'https://jupyter.org/',
        'jupyter': 'https://jupyter.org/',
        'JupyterLab': 'https://jupyterlab.readthedocs.io/en/stable/',
        'Jupyter Lab': 'https://jupyterlab.readthedocs.io/en/stable/',
        'jupyter_sphinx': 'https://jupyter-sphinx.readthedocs.io/en/latest/index.html',
        'keyring': 'https://github.com/jaraco/keyring',
        'keyrings.cryptfile': 'https://github.com/frispete/keyrings.cryptfile',
        'latex': 'https://en.wikipedia.org/wiki/LaTeX',
        'LaTeX': 'https://en.wikipedia.org/wiki/LaTeX',
        'LaTex': 'https://en.wikipedia.org/wiki/LaTeX',
        'Latex': 'https://en.wikipedia.org/wiki/LaTeX',
        'Linux': 'https://en.wikipedia.org/wiki/Linux',
        'linux': 'https://en.wikipedia.org/wiki/Linux',
        'mako': 'https://www.makotemplates.org/',
        "matplotlib": "https://matplotlib.org/index.html",
        'Markdown': 'https://en.wikipedia.org/wiki/Markdown',
        'markdown': 'https://en.wikipedia.org/wiki/Markdown',
        'mathjax': 'https://www.mathjax.org/',
        'MD': 'https://en.wikipedia.org/wiki/Markdown',
        'md': 'https://en.wikipedia.org/wiki/Markdown',
        'mistune': 'https://pypi.org/project/mistune',
        'MiKTeX': 'https://miktex.org/',
        'Miktex': 'https://miktex.org/',
        'miktex': 'https://miktex.org/',
        'MinGW': 'https://www.mingw.org/',
        'MyBinder': 'https://gke.mybinder.org/',
        'nbconvert': 'https://nbconvert.readthedocs.io/en/latest/',
        'nbpresent': 'https://github.com/Anaconda-Platform/nbpresent',
        'node.js': 'https://nodejs.org/en/',
        'notebook': 'https://jupyter-notebook.readthedocs.io/',
        'nose': 'https://pypi.org/project/nose',
        'npm': 'https://www.npmjs.com/',
        'numpy': ('https://www.numpy.org/',
                   ('https://docs.scipy.org/doc/numpy/reference/generated/numpy.{0}.html', 1),
                   ('https://docs.scipy.org/doc/numpy/reference/generated/numpy.{0}.{1}.html', 2)),
        'pandas': ('https://pandas.pydata.org/pandas-docs/stable/',
                   ('https://pandas.pydata.org/pandas-docs/stable/generated/pandas.{0}.html', 1),
                   ('https://pandas.pydata.org/pandas-docs/stable/generated/pandas.{0}.{1}.html', 2)),
        'pandoc': 'https://johnmacfarlane.net/pandoc/',
        'Pandoc': 'https://johnmacfarlane.net/pandoc/',
        'paramiko': 'https://www.paramiko.org/',
        'pdf': 'https://en.wikipedia.org/wiki/Portable_Document_Format',
        'pep8': 'https://www.python.org/dev/peps/pep-0008/',
        'PEP8': 'https://www.python.org/dev/peps/pep-0008/',
        "PEP8 codes": 'https://pep8.readthedocs.io/en/latest/intro.html#error-codes',
        'Pillow': 'https://pillow.readthedocs.io/',
        'PIL': 'https://pillow.readthedocs.io/',
        'pip': 'https://pip.pypa.io/en/stable/',
        'png': 'https://fr.wikipedia.org/wiki/Portable_Network_Graphics',
        'PNG': 'https://fr.wikipedia.org/wiki/Portable_Network_Graphics',
        'pycodestyle': 'https://pycodestyle.readthedocs.io/',
        'pycrypto': 'https://pypi.org/project/pycrypto',
        'pycryptodome': 'https://pypi.org/project/pycryptodome/',
        'pycryptodomex': 'https://pypi.org/project/pycryptodomex/',
        'pyformat.info': 'https://pyformat.info/>`_',
        'pygments': 'https://pygments.org/',
        'pyinstrument': 'https://github.com/joerick/pyinstrument',
        'pylzma': 'https://pypi.org/project/pylzma',
        'pylint': 'https://www.pylint.org/',
        'pylint error codes': 'https://pylint-messages.wikidot.com/all-codes',
        'pypi': 'https://pypi.org/project/',
        'PyPI': 'https://pypi.org/project/',
        'pysftp': 'https://pysftp.readthedocs.io/',
        'pytest': 'https://docs.pytest.org/en/latest/',
        'python': 'https://www.python.org/',
        'Python': 'https://www.python.org/',
        'python-jenkins': 'https://python-jenkins.readthedocs.org/en/latest/',
        'pywin32': 'https://sourceforge.net/projects/pywin32/',
        'REST': 'https://en.wikipedia.org/wiki/Representational_state_transfer',
        'reveal.js': 'https://github.com/hakimel/reveal.js/releases',
        'rst': 'https://en.wikipedia.org/wiki/ReStructuredText',
        'RST': 'https://en.wikipedia.org/wiki/ReStructuredText',
        'scikit-learn': 'https://scikit-learn.org/',
        'SciTe': 'https://www.scintilla.org/SciTE.html',
        'sklearn': ('https://scikit-learn.org/stable/',
                    ('https://scikit-learn.org/stable/modules/generated/{0}.html', 1),
                    ('https://scikit-learn.org/stable/modules/generated/{0}.{1}.html', 2)),
        'scipy': ('https://www.scipy.org/',
                   ('https://docs.scipy.org/doc/scipy/reference/generated/scipy.{0}.html', 1),
                   ('https://docs.scipy.org/doc/scipy/reference/generated/scipy.{0}.{1}.html', 2)),
        'SFTP': 'https://en.wikipedia.org/wiki/SSH_File_Transfer_Protocol',
        'sphinx': 'https://www.sphinx-doc.org/en/master/',
        'Sphinx': 'https://www.sphinx-doc.org/en/master/',
        'sphinx.ext.autodoc': 'https://www.sphinx-doc.org/en/master/ext/autodoc.html#module-sphinx.ext.autodoc',
        'sphinx.ext.intersphinx': 'https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html',
        'sphinx-gallery': 'https://sphinx-gallery.readthedocs.io/en/latest/',
        'Sphinx application': 'https://www.sphinx-doc.org/en/master/_modules/sphinx/application.html',
        'svg': 'https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics',
        'SVG': 'https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics',
        'SVN': 'https://subversion.apache.org/',
        'svn': 'https://subversion.apache.org/',
        'tar.gz': 'https://en.wikipedia.org/wiki/Tar_(computing)',
        'toctree': 'https://www.sphinx-doc.org/en/master/markup/toctree.html',
        'TexnicCenter': 'https://www.texniccenter.org/',
        'tinycss2': 'https://pythonhosted.org/tinycss2/',
        'tkinter': 'https://docs.python.org/3/library/tkinter.html',
        'tornado': 'https://www.tornadoweb.org/en/stable/',
        'TortoiseSVN': 'https://tortoisesvn.net/',
        'travis': 'https://travis-ci.com/',
        'uvicorn': 'https://www.uvicorn.org/',
        'vis.js': 'https://visjs.org/',
        'viz.js': 'https://github.com/mdaines/viz.js/',
        'Visual Studio Community Edition 2015': 'https://imagine.microsoft.com/en-us/Catalog/Product/101',
        'Windows': 'https://en.wikipedia.org/wiki/Microsoft_Windows',
        'xml': 'https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree',
        'yaml': 'https://en.wikipedia.org/wiki/YAML',
        'YAML': 'https://en.wikipedia.org/wiki/YAML',
        'yml': 'https://en.wikipedia.org/wiki/YAML',
        'zip': 'https://en.wikipedia.org/wiki/Zip_(file_format)',
        '*py': ('https://docs.python.org/3/',
                ('https://docs.python.org/3/library/{0}.html', 1),
                ('https://docs.python.org/3/library/{0}.html#{0}.{1}', 2),
                ('https://docs.python.org/3/library/{0}.html#{0}.{1}.{2}', 3)),
        '*pyf': (('https://docs.python.org/3/library/functions.html#{0}', 1),),
        # Custom.
        'jyquickhelper': 'http://www.xavierdupre.fr/app/jyquickhelper/helpsphinx/index.html',
        'pymyinstall': 'http://www.xavierdupre.fr/app/pymyinstall/helpsphinx/index.html',
        'pyquickhelper': 'http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html',
        'pyrsslocal': 'http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html',
        'tkinterquickhelper': 'http://www.xavierdupre.fr/app/tkinterquickhelper/helpsphinx/index.html',
        # Specific.
        'datetime.datetime.strptime': 'https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior',
    }
    return epkg_dictionary


def get_intersphinx_mapping():
    """
    Returns default dictionary
    for extension :epkg:`sphinx.ext.intersphinx`.
    """
    return {
        'cpyquickhelper': (
            'http://www.xavierdupre.fr/app/cpyquickhelper/helpsphinx/', None),
        'joblib': ('https://joblib.readthedocs.io/en/latest/', None),
        'jyquickhelper': (
            'http://www.xavierdupre.fr/app/jyquickhelper/helpsphinx/', None),
        'matplotlib': ('https://matplotlib.org/', None),
        'numpy': ('https://docs.scipy.org/doc/numpy/', None),
        'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
        'pyquickhelper': (
            'http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/', None),
        'python': (
            f'https://docs.python.org/{sys.version_info.major}',
            None),
        'scikit-learn': ('https://scikit-learn.org/stable/', None),
        'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
        'sklearn': ('https://scikit-learn.org/stable/', None)
    }
