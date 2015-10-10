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

if sys.version_info[0] == 2:
    from codecs import open


def set_sphinx_variables(fileconf,
                         module_name,
                         author,
                         year,
                         theme,
                         theme_path,
                         ext_locals,
                         add_extensions=None,
                         bootswatch_theme="spacelab",
                         bootswatch_navbar_links=None,
                         description_latex="",
                         use_mathjax=False):
    """
    defines variables for Sphinx

    @param      fileconf                location of the configuration file
    @param      module_name             name of the module
    @param      author                  author
    @param      year                    year
    @param      theme                   theme to use
    @param      theme_path              themepath
    @param      ext_locals              context (see `locals <https://docs.python.org/2/library/functions.html#locals>`_)
    @param      add_extensions          additional extensions
    @param      bootswatch_theme        for example, ``spacelab``, look at ` <http://bootswatch.com/spacelab/>`_
    @param      bootswatch_navbar_links see `sphinx-bootstrap-theme <http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html>`_
    @param      description latex       description latex
    @param      use_mathjax             set up the documentation to use mathjax,
                                        see `sphinx.ext.mathjax <http://sphinx-doc.org/ext/math.html?highlight=math#module-sphinx.ext.mathjax>`_,
                                        default option is True

    @example(Simple configuration file for Sphinx)

    We assume a module is configurated using the same
    structure as `pyquickhelper <https://github.com/sdpython/pyquickhelper/>`_.
    The file ``conf.py`` could just contain:

    @code
    # -*- coding: utf-8 -*-
    import sys, os, datetime, re
    import solar_theme
    from pyquickhelper.helpgen.default_conf import set_sphinx_variables

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(__file__)[0])))
    set_sphinx_variables(   __file__,
                            "pyquickhelper",
                            "Xavier Dupré",
                            2014,
                            "solar_theme",
                            solar_theme.theme_path,
                            locals())

    # custom settings
    ...
    @endcode

    *setup.py* must contain a string such as ``__version__ = 3.4``.
    Close to the setup, there must be a file ``version.txt``.
    You overwrite a value by giving a variable another value after the fucntion is called.

    @endexample

    .. versionchanged:: 1.3
        Add parameter *use_mathjax*.
    """
    # version .txt
    dirconf = os.path.abspath(os.path.dirname(fileconf))
    version_file = os.path.join(dirconf, "..", "..", "..", "version.txt")
    if not os.path.exists(version_file):
        warnings.warn(
            "a file must contain the commit number (or last part of the version): " + version_file)
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
    year = str(year)
    modindex_common_prefix = [project_var_name + ".", ]
    project = project_var_name + ' documentation'
    copyright = str(year) + ", " + author
    release = '%s.%s' % (version, first_line)
    html_title = "%s %s" % (project_var_name, release)
    htmlhelp_basename = '%s_doc' % project_var_name

    # personnalization latex
    latex_use_parts = False
    latex_documents = [('index', '%s_doc.tex' % project_var_name,
                        '%s' % project_var_name, author, 'manual', True), ]
    man_pages = [('index', '%s_doc' % project_var_name,
                  '%s Documentation' % project_var_name, [author], 1)]
    texinfo_documents = [('index',
                          '%s_documentation' % project_var_name,
                          '%s' % project_var_name,
                          author,
                          '%s documentation' % project_var_name,
                          description_latex,
                          'Miscellaneous'),
                         ]
    latex_show_pagerefs = True

    preamble = '''
            \\usepackage{fixltx2e} % LaTeX patches, \\textsubscript
            \\usepackage{cmap} % fix search and cut-and-paste in Acrobat
            \\usepackage[raccourcis]{fast-diagram}
            \\usepackage{titlesec}
            %%% Redifined titleformat
            \\setlength{\\parindent}{0cm}
            \\setlength{\\parskip}{1ex plus 0.5ex minus 0.2ex}
            \\newcommand{\\hsp}{\\hspace{20pt}}
            \\newcommand{\\HRule}{\\rule{\\linewidth}{0.5mm}}
            %\\titleformat{\\chapter}[hang]{\\Huge\\bfseries\\sffamily}{\\thechapter\\hsp}{0pt}{\\Huge\\bfseries\\sffamily}
            '''.replace("            ", "")

    latex_elements = {'papersize': 'a4', 'pointsize': '10pt',
                      'preamble': preamble,
                      }

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

    # settings
    exclude_patterns = []
    html_show_sphinx = False
    html_show_copyright = False
    __html_last_updated_fmt_dt = datetime.datetime.now()
    html_last_updated_fmt = '%04d-%02d-%02d' % (
        __html_last_updated_fmt_dt.year,
        __html_last_updated_fmt_dt.month,
        __html_last_updated_fmt_dt.day)
    autoclass_content = 'both'
    autosummary_generate = True

    # graphviz
    graphviz_output_format = "svg"
    graphviz_dot = get_graphviz_dot()

    # extensions
    extensions = ['sphinx.ext.autodoc',
                  'sphinx.ext.todo',
                  'sphinx.ext.coverage',
                  'sphinx.ext.mathjax' if use_mathjax else 'sphinx.ext.pngmath',
                  'sphinx.ext.ifconfig',
                  'sphinx.ext.viewcode',
                  'sphinxcontrib.images',
                  'sphinx.ext.autosummary',
                  'sphinx.ext.graphviz',
                  'sphinx.ext.inheritance_diagram',
                  'matplotlib.sphinxext.plot_directive',
                  'matplotlib.sphinxext.only_directives',
                  #'matplotlib.sphinxext.ipython_directive',
                  'IPython.sphinxext.ipython_console_highlighting',
                  'sphinx.ext.napoleon',
                  ]

    if not use_mathjax:
        # extensions.append('matplotlib.sphinxext.mathmpl')
        # this extension disables sphinx.ext.pngmath
        pass

    # disabled for the time being
    from .conf_path_tools import find_latex_path

    if not use_mathjax:
        pngmath_latex = find_latex_path()
        pngmath_dvipng = os.path.join(pngmath_latex, "dvipng.exe")
        if not os.path.exists(pngmath_dvipng):
            raise FileNotFoundError(pngmath_dvipng)
        env_path = os.environ.get("PATH", "")
        if pngmath_latex not in env_path:
            if len(env_path) > 0:
                env_path += ";"
            env_path += pngmath_latex

        if sys.platform.startswith("win"):
            pngmath_latex = os.path.join(pngmath_latex, "latex.exe")
        else:
            pngmath_latex = os.path.join(pngmath_latex, "latex")

        # verification
        if not os.path.exists(pngmath_latex):
            raise FileNotFoundError(pngmath_latex)
        if not os.path.exists(pngmath_dvipng):
            raise FileNotFoundError(pngmath_dvipng)

    # bokeh
    try:
        import bokeh
        extensions.append('bokeh.sphinxext.bokeh_plot')
    except ImportError as e:
        # bokeh is not installed
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
    # latex_show_urls = False
    # latex_appendices = []
    # latex_domain_indices = True
    # texinfo_appendices = []
    # texinfo_domain_indices = True
    # texinfo_show_urls = 'footnote'

    # it modifies the set of things to display inside the sidebar
    html_sidebars = {
        '[!blog]**': ['searchbox.html', 'moduletoc.html', 'relations.html', 'sourcelink.html', ],
        'blog/**': ['searchbox.html', 'blogtoc.html', 'localtoc.html', 'sourcelink.html', ],
    }

    if html_theme == "bootstrap":
        if bootswatch_navbar_links is None:
            bootswatch_navbar_links = []
        html_logo = "project_ico_small.png"
        navbar_links = True,
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
            'source_link_position': "nav",
            'bootswatch_theme': bootswatch_theme,
            'bootstrap_version': "3",
        }

    loc = locals()
    for k, v in loc.items():
        if not k.startswith("_"):
            ext_locals[k] = v

    def this_setup(app):
        return custom_setup(app, author)

    ext_locals["setup"] = this_setup


#################
# custom functions
#################

def extract_version_from_setup(filename):
    """
    extract the version from setup.py assuming it is located in ../../..
    and the version is specified by the following line: ``sversion = "..."``
    """
    setup = os.path.abspath(os.path.split(filename)[0])
    setup = os.path.join(setup, "..", "..", "..", "setup.py")
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
    else:
        raise FileNotFoundError("unable to find setup.py, tried: " + setup)


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


def get_graphviz_dot():
    """
    finds Graphviz executable dot, does something specific for Windows
    """
    if sys.platform.startswith("win"):
        version = range(34, 42)
        for v in version:
            graphviz_dot = r"C:\Program Files (x86)\Graphviz2.{0}\bin\dot.exe".format(
                v)
            if os.path.exists(graphviz_dot):
                break

    if sys.platform.startswith("win"):
        if not os.path.exists(graphviz_dot):
            raise FileNotFoundError(graphviz_dot)
    else:
        graphviz_dot = "dot"
    return graphviz_dot

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
    from .sphinx_blog_extension import visit_blogpost_node, depart_blogpost_node
    from .sphinx_blog_extension import visit_blogpostagg_node, depart_blogpostagg_node
    from .sphinx_blog_extension import blogpost_node, blogpostagg_node
    from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
    from .sphinx_runpython_extension import RunPythonDirective
    from .sphinx_runpython_extension import runpython_node, visit_runpython_node, depart_runpython_node

    app.connect("autodoc-skip-member", skip)
    app.add_config_value('author', author, True)

    # this command enables the parameter blog_background to be part of the
    # configuration
    app.add_config_value('blog_background', True, 'env')

    # app.add_node(blogpostlist)
    app.add_node(blogpost_node,
                 html=(visit_blogpost_node, depart_blogpost_node),
                 latex=(visit_blogpost_node, depart_blogpost_node),
                 text=(visit_blogpost_node, depart_blogpost_node))

    app.add_node(blogpostagg_node,
                 html=(visit_blogpostagg_node, depart_blogpostagg_node),
                 latex=(visit_blogpostagg_node, depart_blogpostagg_node),
                 text=(visit_blogpostagg_node, depart_blogpostagg_node))

    app.add_node(runpython_node,
                 html=(visit_runpython_node, depart_runpython_node),
                 latex=(visit_runpython_node, depart_runpython_node),
                 text=(visit_runpython_node, depart_runpython_node))

    app.add_directive('blogpost', BlogPostDirective)
    app.add_directive('blogpostagg', BlogPostDirectiveAgg)
    app.add_directive('runpython', RunPythonDirective)
    #app.add_directive('blogpostlist', BlogPostListDirective)
    #app.connect('doctree-resolved', process_blogpost_nodes)
    #app.connect('env-purge-doc', purge_blogpost)
