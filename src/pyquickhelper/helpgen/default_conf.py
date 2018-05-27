# -*- coding: utf-8 -*-
"""
@file
@brief Default values for the Sphinx configuration.
"""


import sys
import os
import datetime
import re
import warnings
from sphinx.builders.html import Stylesheet
from sphinx.errors import ExtensionError
from .style_css_template import style_figure_notebook


if sys.version_info[0] == 2:
    from codecs import open
    FileNotFoundError = Exception


def set_sphinx_variables(fileconf, module_name, author, year, theme, theme_path, ext_locals,
                         add_extensions=None, bootswatch_theme="spacelab", bootswatch_navbar_links=None,
                         description_latex="", use_mathjax=False, use_lunrsearch=False,
                         enable_disabled_parts="enable_disabled_documented_pieces_of_code",
                         sharepost="facebook-linkedin-twitter-20-body", custom_style=None,
                         extlinks=None, github_user=None, github_repo=None, title=None,
                         book=True, link_resolve=None, nblayout='classic'):
    """
    Defines variables for :epkg:`Sphinx`.

    @param      fileconf                location of the configuration file
    @param      module_name             name of the module
    @param      author                  author
    @param      year                    year
    @param      theme                   theme to use
    @param      theme_path              themepath
    @param      ext_locals              context (see `locals <https://docs.python.org/2/library/functions.html#locals>`_)
    @param      add_extensions          additional extensions
    @param      bootswatch_theme        for example, ``spacelab``, look at `spacelab <http://bootswatch.com/spacelab/>`_
    @param      bootswatch_navbar_links see `sphinx-bootstrap-theme <http://ryan-roemer.github.io/
                                        sphinx-bootstrap-theme/README.html>`_
    @param      description_latex       description latex
    @param      use_mathjax             set up the documentation to use mathjax,
                                        see `sphinx.ext.mathjax <http://sphinx-doc.org/ext/math.html
                                        ?highlight=math#module-sphinx.ext.mathjax>`_,
                                        default option is True
    @param      use_lunrsearch          suggest autocompletion in sphinx,
                                        see `sphinxcontrib-lunrsearch <https://github.com/rmcgibbo/
                                        sphinxcontrib-lunrsearch>`_
    @param      enable_disabled_parts   @see fn remove_undesired_part_for_documentation
    @param      sharepost               add share button to share blog post on usual networks
    @param      custom_style            custom style sheet
    @param      extlinks                parameter `extlinks <http://www.sphinx-doc.org/en/stable/ext/extlinks.html#confval-extlinks>`_,
                                        example: ``{'issue': ('https://github.com/sdpython/pyquickhelper/issues/%s', 'issue ')}``
    @param      github_user             git(hub) user
    @param      github_repo             git(hub) project
    @param      title                   if not None, use *title* instead of *module_name* as a title
    @param      book                    the output is a book
    @param      link_resolve            url where the documentation is published,
                                        used for parameter *linkcode_resolve*
    @param      nblayout                ``'classic'`` or ``'table'``, specifies the layout for
                                        the notebook gallery

    If the parameter *custom_style* is not None, it will call ``app.add_stylesheet(custom_style)``
    in the setup.

    .. exref::
        :title: Simple configuration file for Sphinx

        We assume a module is configurated using the same
        structure as `pyquickhelper <https://github.com/sdpython/pyquickhelper/>`_.
        The file ``conf.py`` could just contain:

        ::

            # -*- coding: utf-8 -*-
            import sys, os, datetime, re
            import solar_theme
            from pyquickhelper.helpgen.default_conf import set_sphinx_variables

            sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
            set_sphinx_variables(__file__, "pyquickhelper", "Xavier Dupré", 2014,
                                 "solar_theme", solar_theme.theme_path, locals())

            # custom settings
            ...

        *setup.py* must contain a string such as ``__version__ = 3.4``.
        Close to the setup, there must be a file ``version.txt``.
        You overwrite a value by giving a variable another value after the fucntion is called.

        Some parts of the code can be disabled before generating the documentation.
        Those parts are surrounded by::

            # -- HELP BEGIN EXCLUDE --
            import module
            # -- HELP END EXCLUDE --

        If *enable_disabled_parts* is set to a string, these sections will become::

            # -- HELP BEGIN EXCLUDE --
            if hasattr(sys, <enable_disabled_parts>) and sys.<enable_disabled_parts>:
                import module
            # -- HELP END EXCLUDE --

    .. versionchanged:: 1.4
        Add parameters *extlinks*, *github_user*, *github_repo*,
        *title*. Add extension
        `extlinks <http://www.sphinx-doc.org/en/stable/ext/extlinks.html#module-sphinx.ext.extlinks>`_.

    .. versionchanged:: 1.5
        Parameter *nblayout* was added.
    """
    # sphinx_gallery only supports matplotlib.use('agg')
    # and it must be done first.
    try:
        import sphinx_gallery
        import sphinx_gallery.gen_rst
    except ImportError:
        warnings.warn("ImportError: sphinx-gallery.", ImportWarning)
    except ValueError:
        warnings.warn(
            "ImportError: sphinx-gallery.get_rst fails.", ImportWarning)

    # version .txt
    dirconf = os.path.abspath(os.path.dirname(fileconf))
    version_file = os.path.join(dirconf, "..", "..", "..", "version.txt")
    if not os.path.exists(version_file):
        warnings.warn(
            "File '{0}' must contain the commit number (or last part of the version).".format(version_file), UserWarning)
        first_line = "0"
    else:
        first_line = get_first_line(version_file)

    # language
    language = "en"

    # main version
    version = extract_version_from_setup(fileconf)

    # settings sphinx
    pygments_style = 'sphinx'

    # personnalization
    project_var_name = module_name
    author = author
    nblayout = nblayout
    year = str(year)
    modindex_common_prefix = [project_var_name + ".", ]
    project = (project_var_name + ' documentation') if title is None else title
    copyright = str(year) + ", " + author
    release = '%s.%s' % (version, first_line)
    html_title = ("%s %s" % (project_var_name, release)
                  ) if title is None else title
    htmlhelp_basename = '%s_doc' % project_var_name
    enable_disabled_parts = enable_disabled_parts

    # personnalization latex
    _proj = project_var_name.replace("_", "\\_")
    latex_book = book
    latex_use_parts = False
    latex_documents = [('index', '%s_doc.tex' % project_var_name, _proj if title is None else title,
                        author, 'manual', True), ]
    man_pages = [('index', '%s_doc' % project_var_name,
                  ('%s Documentation' % _proj) if title is None else title,
                  [author], 1)]
    texinfo_documents = [('index',
                          ('%s documentation' %
                           _proj) if title is None else title,
                          ('%s' % _proj) if title is None else title,
                          author,
                          ('%s documentation' %
                           _proj) if title is None else title,
                          description_latex,
                          'Miscellaneous'),
                         ]
    latex_show_pagerefs = True

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
            }
            '''.replace("            ", "")

    latex_elements = {
        'papersize': 'a4',
        'pointsize': '10pt',
        'preamble': preamble,
    }

    # pyquickhelper automation
    auto_rst_generation = True

    # latex_additional_files = ["mfgan-bw.sty", "_static/cover.png"]

    # figure
    numfig = False

    # theme
    html_theme = theme
    shtml_theme_options = {"bodyfont": "Calibri"}
    if theme_path is not None:
        if isinstance(theme_path, list):
            html_theme_path = theme_path
        else:
            html_theme_path = [theme_path]

    # static files
    html_logo = "project_ico.png"
    html_favicon = "project_ico.ico"
    html_static_path = ['phdoc_static']
    templates_path = ['phdoc_templates']

    # extensions, encoding
    source_suffix = '.rst'
    source_encoding = 'utf-8'
    master_doc = 'index'
    html_output_encoding = 'utf-8'

    # blogs (custom parameter)
    blog_background = True
    blog_background_page = False
    sharepost = sharepost

    # settings
    exclude_patterns = ["*.py", "**/*.py"]
    html_show_sphinx = False
    html_show_copyright = False
    __html_last_updated_fmt_dt = datetime.datetime.now()
    html_last_updated_fmt = '%04d-%02d-%02d' % (
        __html_last_updated_fmt_dt.year,
        __html_last_updated_fmt_dt.month,
        __html_last_updated_fmt_dt.day)
    autoclass_content = 'both'
    autosummary_generate = True

    # import helpers to find tools to build the documentation
    from .conf_path_tools import find_latex_path, find_graphviz_dot

    # graphviz
    graphviz_output_format = "svg"
    graphviz_dot = find_graphviz_dot()

    # todo, mathdef, blocref, faqref, exref, nbref
    todo_include_todos = True
    todoext_include_todosext = True
    mathdef_include_mathsext = True
    blocref_include_blocrefs = True
    faqref_include_faqrefs = True
    exref_include_exrefs = True
    nbref_include_nbrefs = True
    mathdef_link_number = "{first_letter}{number}"

    # extensions
    extensions = []
    try:
        import sphinx_gallery
        extensions.append('sphinx_gallery.gen_gallery')
        has_sphinx_gallery = True
    except ImportError:
        has_sphinx_gallery = False

    if has_sphinx_gallery:
        try:
            import sphinx_gallery.gen_rst
        except ValueError as e:
            raise ValueError("Issue with sphinx-gallery.\n{0}".format(e))

    extensions.extend(['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.coverage',
                       'sphinx.ext.extlinks', 'sphinx.ext.graphviz', 'sphinx.ext.ifconfig',
                       'sphinx.ext.inheritance_diagram',
                       'sphinx.ext.mathjax' if use_mathjax else 'sphinx.ext.imgmath',
                       'sphinx.ext.napoleon', 'sphinx.ext.todo', 'sphinx.ext.viewcode',
                       'sphinxcontrib.imagesvg',
                       # 'matplotlib.sphinxext.only_directives',
                       # 'matplotlib.sphinxext.mathmpl',
                       # 'matplotlib.sphinxext.only_directives',
                       'matplotlib.sphinxext.plot_directive',
                       # 'matplotlib.sphinxext.ipython_directive',
                       'jupyter_sphinx.embed_widgets',
                       "nbsphinx",
                       'pyquickhelper.sphinxext.sphinx_rst_builder',
                       ])

    try:
        import sphinxcontrib.jsdemo
        assert sphinxcontrib.jsdemo is not None
        extensions.append('sphinxcontrib.jsdemo')
    except ImportError:
        # No module sphinxcontrib.jsdemo.
        pass

    if use_lunrsearch:
        extensions.append('sphinxcontrib.lunrsearch')

    if not use_mathjax:
        # extensions.append('matplotlib.sphinxext.mathmpl')
        # this extension disables sphinx.ext.imgmath
        pass

    if not use_mathjax:
        sep = ";" if sys.platform.startswith("win") else ":"
        imgmath_latex = find_latex_path()
        if sys.platform.startswith("win"):
            imgmath_dvipng = os.path.join(imgmath_latex, "dvipng.exe")
            if not os.path.exists(imgmath_dvipng):
                raise FileNotFoundError(imgmath_dvipng)
        else:
            imgmath_dvipng = os.path.join(imgmath_latex, "dvipng")
        env_path = os.environ.get("PATH", "")
        if imgmath_latex not in env_path:
            if len(env_path) > 0:
                env_path += sep
            env_path += imgmath_latex

        if sys.platform.startswith("win"):
            imgmath_latex = os.path.join(imgmath_latex, "latex.exe")
        else:
            imgmath_latex = os.path.join(imgmath_latex, "latex")

        # verification
        if sys.platform.startswith("win"):
            if not os.path.exists(imgmath_latex):
                raise FileNotFoundError(imgmath_latex)
            if not os.path.exists(imgmath_dvipng):
                raise FileNotFoundError(imgmath_dvipng)
        else:
            # TODO: check on linux
            pass

    if add_extensions is not None:
        extensions.extend(add_extensions)

    # add_function_parentheses = True
    # add_module_names = True
    # show_authors = False
    # html_sidebars = {}
    # html_additional_pages = {}
    # html_domain_indices = True
    # html_use_index = True
    # html_split_index = False
    # html_show_sourcelink = True
    # html_use_opensearch = ''
    # html_file_suffix = None
    # latex_logo = None
    latex_show_urls = 'footnote'
    # latex_appendices = []
    # latex_domain_indices = True
    # texinfo_appendices = []
    # texinfo_domain_indices = True
    # texinfo_show_urls = 'footnote'

    # it modifies the set of things to display inside the sidebar
    # see http://www.sphinx-doc.org/en/stable/config.html#confval-html_sidebars
    html_sidebars = {
        '[!blog]**': ['searchbox.html', 'moduletoc.html', 'relations.html', 'sourcelink.html', ],
        'blog/**': ['searchbox.html', 'blogtoc.html', 'localtoc.html', 'sourcelink.html', ],
    }

    # tpl_role
    from ..sphinxext.documentation_link import python_link_doc
    tpl_template = {'py': python_link_doc}

    # epkg_role
    epkg_dictionary = {
        '7z': "http://www.7-zip.org/",
        'Anaconda': 'http://continuum.io/downloads',
        'appveyor': 'https://www.appveyor.com/',
        'bz2': 'https://en.wikipedia.org/wiki/Bzip2',
        'cairosvg': 'https://github.com/Kozea/CairoSVG',
        'class Sphinx': 'https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py#L107',
        'codecov': 'https://codecov.io/',
        'conda': 'https://github.com/conda/conda',
        'coverage': 'https://pypi.org/project/coverage',
        'cryptography': 'http://cryptography.readthedocs.org/',
        'cssselect2': 'http://cssselect2.readthedocs.io/en/latest/',
        'Cython': 'http://cython.org/',
        'datetime': 'https://docs.python.org/3/library/datetime.html#datetime-objects',
        'docx': 'https://en.wikipedia.org/wiki/Office_Open_XML',
        'django': 'https://www.djangoproject.com/',
        'docutils': 'http://docutils.sourceforge.net/',
        'GIT': 'http://git-scm.com/',
        'git': 'http://git-scm.com/',
        'Git': 'http://git-scm.com/',
        'github': 'https://github.com/',
        'GitHub': 'https://github.com/',
        'GraphViz': 'http://www.graphviz.org/',
        'Graphviz': 'http://www.graphviz.org/',
        'html': 'https://en.wikipedia.org/wiki/HTML',
        'Inkscape': 'https://inkscape.org/',
        'InkScape': 'https://inkscape.org/',
        'Java': 'http://www.java.com/fr/download/',
        'Jenkins': 'https://jenkins-ci.org/',
        'jinja2': 'http://jinja.pocoo.org/docs/',
        'js2py': 'https://github.com/PiotrDabkowski/Js2Py',
        'Jupyter': 'http://jupyter.org/',
        'jupyter': 'http://jupyter.org/',
        'latex': 'https://en.wikipedia.org/wiki/LaTeX',
        'LaTeX': 'https://en.wikipedia.org/wiki/LaTeX',
        'mako': 'http://www.makotemplates.org/',
        "matplotlib": "https://matplotlib.org/index.html",
        'mistune': 'https://pypi.org/project/mistune',
        'MiKTeX': 'http://miktex.org/',
        'MinGW': 'http://www.mingw.org/',
        'nbconvert': 'http://nbconvert.readthedocs.io/en/latest/',
        'nbpresent': 'https://github.com/Anaconda-Platform/nbpresent',
        'node.js': 'https://nodejs.org/en/',
        'notebook': 'https://jupyter-notebook.readthedocs.io/',
        'nose': 'https://pypi.org/project/nose',
        'numpy': ('http://www.numpy.org/',
                   ('http://docs.scipy.org/doc/numpy/reference/generated/numpy.{0}.html', 1)),
        'pandas': ('http://pandas.pydata.org/pandas-docs/stable/',
                   ('http://pandas.pydata.org/pandas-docs/stable/generated/pandas.{0}.html', 1),
                   ('http://pandas.pydata.org/pandas-docs/stable/generated/pandas.{0}.{1}.html', 2)),
        'pandoc': 'http://johnmacfarlane.net/pandoc/',
        'Pandoc': 'http://johnmacfarlane.net/pandoc/',
        'pdf': 'https://en.wikipedia.org/wiki/Portable_Document_Format',
        'PEP8': 'https://www.python.org/dev/peps/pep-0008/',
        "PEP8 codes": 'http://pep8.readthedocs.io/en/latest/intro.html#error-codes',
        'Pillow': 'http://pillow.readthedocs.io/',
        'pip': 'https://pip.pypa.io/en/stable/',
        'png': 'https://fr.wikipedia.org/wiki/Portable_Network_Graphics',
        'PNG': 'https://fr.wikipedia.org/wiki/Portable_Network_Graphics',
        'pycodestyle': 'http://pycodestyle.readthedocs.io/',
        'pycrypto': 'https://pypi.org/project/pycrypto',
        'pygments': 'http://pygments.org/',
        'pylzma': 'https://pypi.org/project/pylzma',
        'pylint': 'https://www.pylint.org/',
        'pypi': 'https://pypi.org/project/',
        'PyPI': 'https://pypi.org/project/',
        'python': 'http://www.python.org/',
        'Python': 'http://www.python.org/',
        'python-jenkins': 'http://python-jenkins.readthedocs.org/en/latest/',
        'pywin32': 'https://sourceforge.net/projects/pywin32/',
        'reveal.js': 'https://github.com/hakimel/reveal.js/releases',
        'rst': 'https://en.wikipedia.org/wiki/ReStructuredText',
        'scikit-learn': 'http://scikit-learn.org/',
        'sklearn': ('http://scikit-learn.org/stable/',
                    ('http://scikit-learn.org/stable/modules/generated/{0}.html', 1),
                    ('http://scikit-learn.org/stable/modules/generated/{0}.{1}.html', 2)),
        'scipy': 'https://www.scipy.org/',
        'sphinx': 'http://www.sphinx-doc.org/en/stable/',
        'Sphinx': 'http://www.sphinx-doc.org/en/stable/',
        'svg': 'https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics',
        'SVG': 'https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics',
        'SVN': 'https://subversion.apache.org/',
        'tar.gz': 'https://en.wikipedia.org/wiki/Tar_(computing)',
        'TexnicCenter': 'http://www.texniccenter.org/',
        'tinycss2': 'http://pythonhosted.org/tinycss2/',
        'tornado': 'http://www.tornadoweb.org/en/stable/',
        'TortoiseSVN': 'http://tortoisesvn.net/',
        'travis': 'https://travis-ci.org/',
        'Visual Studio Community Edition': 'https://www.visualstudio.com/',
        'Visual Studio Community Edition 2015': 'https://imagine.microsoft.com/en-us/Catalog/Product/101',
        'zip': 'https://en.wikipedia.org/wiki/Zip_(file_format)',
        '*py': ('https://docs.python.org/3/',
                ('https://docs.python.org/3/library/{0}.html', 1),
                ('https://docs.python.org/3/library/{0}.html#{0}.{1}', 2)),
        '*pyf': (('https://docs.python.org/3/library/functions.html#{0}', 1),),
        # Custom.
        'jyquickhelper': 'http://www.xavierdupre.fr/app/jyquickhelper/helpsphinx/index.html',
        'pymyinstall': 'http://www.xavierdupre.fr/app/pymyinstall/helpsphinx/index.html',
        'pyquickhelper': 'http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html',
        'pyrsslocal': 'http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html',
        # Specific.
        'datetime.datetime.strptime': 'https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior',
    }

    # latex
    math_number_all = False
    imgmath_latex_preamble = """
                    \\usepackage{epic}
                    \\newcommand{\\acc}[1]{\\left\\{#1\\right\\}}
                    \\newcommand{\\cro}[1]{\\left[#1\\right]}
                    \\newcommand{\\pa}[1]{\\left(#1\\right)}
                    \\newcommand{\\R}{\\mathbb{R}}
                    """
    # post processing of the full latex file
    # it should be a function, None by default
    custom_latex_processing = None

    # github or git link
    if github_user:
        releases_issue_uri = "https://github.com/{0}/{1}/issues/%s".format(
            github_user, module_name)
        githublink_options = dict(user=github_user)
        github_anchor = "source on GitHub"
    else:
        githublink_options = None
    if github_repo:
        if githublink_options is None:
            githublink_options = {}
        value = github_repo.strip("/").split("/")[-1]
        if value.endswith(".git"):
            value = value[:-4]
        githublink_options['project'] = value

        if 'anchor' not in githublink_options and "github" in github_repo.lower():
            githublink_options['anchor'] = "source on GitHub"

    if extlinks is None:
        extlinks = dict()
    elif 'issue' in extlinks:
        issue = extlinks['issue'][0].split('/')
        le = len(issue)
        if le > 0:
            user = issue[-4]
            project = issue[-3]
            if githublink_options is None:
                githublink_options = {}
            if 'user' not in githublink_options:
                githublink_options["user"] = user
            if 'project' not in githublink_options:
                githublink_options["project"] = project
            if 'anchor' not in githublink_options and 'github' in extlinks['issue'][0].lower():
                githublink_options["anchor"] = 'source on GitHub'
            if not github_repo and extlinks['issue'][0].startswith("https://github.com"):
                github_repo = "https://github.com/{0}/{1}.git".format(
                    user, project)

    # themes
    if html_theme == "bootstrap":
        if bootswatch_navbar_links is None:
            bootswatch_navbar_links = []
        html_logo = "project_ico_small.png"
        navbar_links = bootswatch_navbar_links
        html_theme_options = {
            'navbar_title': "home",
            'navbar_site_name': "Site",
            'navbar_links': navbar_links,
            'navbar_sidebarrel': True,
            'navbar_pagenav': True,
            'navbar_pagenav_name': "Page",
            'globaltoc_depth': 3,
            'globaltoc_includehidden': "true",
            'navbar_class': "navbar navbar-inverse",
            'navbar_fixed_top': "true",
            'source_link_position': "footer",
            'bootswatch_theme': bootswatch_theme,
            'bootstrap_version': "3",
        }
    elif html_theme == "guzzle_sphinx_theme":
        html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
        if "guzzle_sphinx_theme" not in extensions:
            extensions.append('guzzle_sphinx_theme')
        html_theme_options = {
            "project_nav_name": module_name,
            # specified, then no sitemap will be built.
            # "base_url": ""
            # "homepage": "index",
            # "projectlink": "http://myproject.url",
        }
    elif html_theme == "foundation_sphinx_theme":
        import foundation_sphinx_theme
        html_theme_path = foundation_sphinx_theme.HTML_THEME_PATH
        if "foundation_sphinx_theme" not in extensions:
            extensions.append('foundation_sphinx_theme')
            html_theme_options = {
                'logo_screen': 'project_ico.png',
                'logo_mobile': 'project_ico.ico',
                'favicon': 'project_ico.ico',
                'github_user': github_user,
                'github_repo': github_repo,
            }
        pygments_style = 'monokai'

    # mapping

    intersphinx_mapping = {'python': (
        'https://docs.python.org/{0}.{1}'.format(*(sys.version_info[:2])), None)}
    intersphinx_mapping['matplotlib'] = ('http://matplotlib.org/', None)
    try:
        import numpy
        intersphinx_mapping['numpy'] = (
            'http://www.numpy.org/{0}'.format(numpy.__version__), None)
    except ImportError:
        pass
    try:
        import pandas
        intersphinx_mapping['pandas'] = (
            'http://pandas.pydata.org/pandas-docs/version/{0}'.format(pandas.__version__), None)
    except ImportError:
        pass

    # disable some checkings
    check_ie_layout_html = False

    # information about code
    def linkcode_resolve_function(domain, info):
        if link_resolve is None:
            return None
        if domain != 'py':
            return None
        if not info['module']:
            return None
        filename = info['module'].replace('.', '/')
        return "%s/%s.py" % (link_resolve, filename)

    if link_resolve is not None:
        linkcode_resolve = linkcode_resolve_function
        extensions.append("sphinx.ext.linkcode")

    # commit modification
    def modify_commit_function(nbch, date, author, comment):
        if author is not None and "@" in author:
            author = author.split("@")[0]
        return nbch, date, author, comment

    modify_commit = modify_commit_function

    # sphinx gallery
    backreferences_dir = "modules/generated"
    dirname = os.path.dirname(fileconf)
    exa = os.path.join(dirname, "..", "..", "..", "_doc", "examples")
    if os.path.exists(exa):
        exa = os.path.normpath(exa)
        import pathlib
        pp = pathlib.Path(exa)
        readmes = pp.glob("**/README.txt")
        examples_dirs = []
        gallery_dirs = []
        for res in readmes:
            if not has_sphinx_gallery:
                raise ImportError(
                    "sphinx_gallery is not present for gallery '{0}'".format(exa))
            last = res.parts[-2]
            if last.startswith("temp_"):
                continue
            parts = last.replace("\\", "/").split("/")
            if any(filter(lambda x: x.startswith("temp_"), parts)):
                continue
            nn = res.parent

            # We check that a readme.txt is not present in the parent folder.
            nn_parent_read = os.path.join(os.path.split(nn)[0], "README.txt")
            if os.path.exists(nn_parent_read):
                continue

            # Main gallery.
            examples_dirs.append(str(nn))
            if last in ("notebooks", "examples"):
                last = "gy" + last
            dest = os.path.join(dirname, last)
            if dest in gallery_dirs:
                raise ValueError(
                    "Gallery '{0}' already exists (source='{1}', last={2}).".format(dest, nn, last))
            gallery_dirs.append(dest)
        if len(examples_dirs) == 0:
            raise ValueError(
                "Unable to find any 'README.txt' in '{0}'.".format(exa))
        reference_url = {k: v[0] for k, v in intersphinx_mapping.items()}
        example_dir = os.path.join(dirname, "gallery")
        if not os.path.exists(example_dir):
            os.makedirs(example_dir)
        sphinx_gallery_conf = {
            'doc_module': (module_name),
            'reference_url': {},
            'examples_dirs': examples_dirs,
            'gallery_dirs': gallery_dirs,
            'backreferences_dir': example_dir,
            'expected_failing_examples': [],
        }
    else:
        extensions = [_ for _ in extensions if _ !=
                      "sphinx_gallery.gen_gallery"]

    # notebooks replacements (post-process)
    notebook_replacements = {'html': [('\\mathbb{1}_', '\\mathbf{1\\!\\!1}_')]}

    # notebooks snippets
    notebook_custom_snippet_folder = 'notebooks_snippets'

    ###########################
    # collect local variables
    ###########################
    # do not add anything after this
    loc = locals()
    for k, v in loc.items():
        if not k.startswith("_"):
            ext_locals[k] = v

    if custom_style is not None:
        ex = False
        for st in html_static_path:
            full = os.path.join(dirconf, st, custom_style)
            if os.path.exists(full):
                ex = True
                break
        if not ex:
            raise FileNotFoundError("unable to find {0} in\n{1}\nand\n{2}".format(
                custom_style, dirconf, "\n".join(html_static_path)))

    def this_setup(app):
        if custom_style is not None:
            app.add_stylesheet(custom_style)
        return custom_setup(app, author)

    ext_locals["setup"] = this_setup


#################
# custom functions
#################

def extract_version_from_setup(filename):
    """
    Extracts the version from *setup.py* assuming it
    is located in ``../../..`` and the version is specified
    by the following line: ``sversion = "..."``.
    """
    setup = os.path.abspath(os.path.split(filename)[0])
    setups = [os.path.join(setup, "..", "..", "..", "setup.py"),
              os.path.join(setup, "..", "..", "..", "..", "setup.py")]
    setups = [os.path.normpath(setup) for setup in setups]
    for setup in setups:
        if os.path.exists(setup):
            with open(setup, "r") as f:
                content = f.read()
            exp = re.compile("sversion *= *['\\\"]([0-9.]+?)['\\\"]")
            all = exp.findall(content)
            if len(all) == 0:
                raise Exception("unable to locate the version from setup.py")
            if len(all) != 1:
                raise Exception("more than one version was found: " + str(all))
            return all[0]
    raise FileNotFoundError(
        "Unable to find *setup.py*, tried:\n{0}".format("\n".join(setups)))


def get_first_line(filename):
    """
    expects to find a text file with a line, the function extracts and returns this line
    """
    try:
        with open(filename, "r") as ff:
            first_line = ff.readlines()[0].strip(" \n\r")
    except FileNotFoundError:
        first_line = "xxx"
    return first_line


#################
# sphinx functions
#################


def skip(app, what, name, obj, skip, options):
    """
    to skip some functions,

    see `Skipping members <http://sphinx-doc.org/ext/autodoc.html#event-autodoc-skip-member>`_
    """
    if name.startswith("_") and name not in \
            ["__qualname__",
                "__module__",
                "__dict__",
                "__doc__",
                "__weakref__",
             ]:
        return False
    return skip


def custom_setup(app, author):
    """
    see `Sphinx core events <http://sphinx-doc.org/extdev/appapi.html?highlight=setup#sphinx-core-events>`_
    """
    from ..sphinxext.sphinx_bigger_extension import setup as setup_bigger
    from ..sphinxext.sphinx_githublink_extension import setup as setup_githublink
    from ..sphinxext.sphinx_blog_extension import setup as setup_blogpost
    from ..sphinxext.sphinx_blocref_extension import setup as setup_blocref
    from ..sphinxext.sphinx_exref_extension import setup as setup_exref
    from ..sphinxext.sphinx_faqref_extension import setup as setup_faqref
    from ..sphinxext.sphinx_mathdef_extension import setup as setup_mathdef
    from ..sphinxext.sphinx_nbref_extension import setup as setup_nbref
    from ..sphinxext.sphinx_runpython_extension import setup as setup_runpython
    from ..sphinxext.sphinx_sharenet_extension import setup as setup_sharenet
    from ..sphinxext.sphinx_video_extension import setup as setup_video
    from ..sphinxext.sphinx_todoext_extension import setup as setup_todoext
    from ..sphinxext.sphinx_docassert_extension import setup as setup_docassert
    from ..sphinxext.sphinx_autosignature import setup as setup_signature
    from ..sphinxext.sphinx_template_extension import setup as setup_tpl
    from ..sphinxext.sphinx_cmdref_extension import setup as setup_cmdref
    from ..sphinxext.sphinx_postcontents_extension import setup as setup_postcontents
    from ..sphinxext.sphinx_tocdelay_extension import setup as setup_tocdelay
    from ..sphinxext.sphinx_youtube_extension import setup as setup_youtube
    from ..sphinxext.sphinx_epkg_extension import setup as setup_epkg
    from ..sphinxext import setup_images
    from ..sphinxext.sphinx_toctree_extension import setup as setup_toctree
    from ..sphinxext.sphinx_collapse_extension import setup as setup_collapse
    # from ..sphinxext.sphinx_rst_builder import setup as setup_rst

    try:
        app.connect("autodoc-skip-member", skip)
    except ExtensionError as e:
        # No event autodoc-skip-member.
        warnings.warn("Sphinx extension error {0}".format(e), RuntimeError)
    app.add_config_value('author', author, True)

    setup_toctree(app)
    setup_runpython(app)
    setup_bigger(app)
    setup_githublink(app)
    setup_sharenet(app)
    setup_video(app)
    setup_todoext(app)
    setup_blogpost(app)
    setup_mathdef(app)
    setup_blocref(app)
    setup_exref(app)
    setup_faqref(app)
    setup_nbref(app)
    setup_cmdref(app)
    setup_signature(app)
    setup_docassert(app)
    setup_postcontents(app)
    setup_tocdelay(app)
    setup_youtube(app)
    setup_tpl(app)
    setup_epkg(app)
    setup_images(app)
    setup_collapse(app)
    # Already part of the added extensions.
    # setup_rst(app)
    try:
        import bokeh
        assert bokeh is not None
        from ..sphinxext.bokeh.bokeh_plot import setup as setup_bokeh
        setup_bokeh(app)
    except ImportError:
        # bokeh is not installed.
        pass

    # from sphinx.util.texescape import tex_replacements
    # tex_replacements += [('oe', '\\oe '), ]
    app.add_javascript("require.js")

    # style for notebooks
    app.add_stylesheet(style_figure_notebook[0])
    return app


def get_default_stylesheet():
    """
    Returns the style of additional style sheets

    @return         list of files

    .. versionadded:: 1.5
    """
    rel = "_static/" + style_figure_notebook[0]
    # rel2 = "_static/gallery.css"  # This should not be needed for sphinx-gallery.
    return [Stylesheet(rel="stylesheet", title="style_figure_notebook", filename=rel)]
    # Stylesheet(rel="stylesheet", title="sphinx_gallery_missing", filename=rel2)


def get_default_javascript():
    """
    Returns the style of additional style sheets

    @return         list of files

    .. versionadded:: 1.5
    """
    return ["_static/require.js"]
