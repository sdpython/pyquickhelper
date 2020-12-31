"""
@file
@brief Subpart related to sphinx extensions

.. todoext::
    :title: add directive for a sortable table
    :tag: enhancement
    :issue: 27

    Based on `slickgrid <https://github.com/mleibman/SlickGrid/tree/master/examples>`_.
"""
import warnings
from sphinx.ext.autodoc import setup as setup_autodoc
from sphinx.ext.imgmath import setup as setup_imgmath
from sphinxcontrib.imagesvg import setup as setup_imagesvg
from sphinx.ext.graphviz import setup as setup_graphviz
from sphinx.ext.todo import setup as setup_todo

from .blog_post import BlogPost
from .blog_post_list import BlogPostList
from .sphinx_bigger_extension import bigger_node, bigger_role
from .sphinx_blocref_extension import BlocRef, BlocRefList
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_cmdref_extension import CmdRef, CmdRefList
from .sphinx_epkg_extension import epkg_node
from .sphinx_exref_extension import ExRef, ExRefList
from .sphinx_faqref_extension import FaqRef, FaqRefList
from .sphinx_githublink_extension import githublink_node, githublink_role
from .sphinx_gitlog_extension import gitlog_node, gitlog_role
from .sphinx_mathdef_extension import MathDef, MathDefList
from .sphinx_quote_extension import QuoteNode
from .sphinx_nbref_extension import NbRef, NbRefList
from .sphinx_postcontents_extension import PostContentsDirective, postcontents_node
from .sphinx_tocdelay_extension import TocDelayDirective, tocdelay_node
from .sphinx_youtube_extension import YoutubeDirective, youtube_node
from .sphinx_sharenet_extension import ShareNetDirective, sharenet_node
from .sphinx_downloadlink_extension import process_downloadlink_role
from .sphinx_video_extension import VideoDirective, video_node
from .sphinx_image_extension import SimpleImageDirective, simpleimage_node
from .sphinx_template_extension import tpl_node
from .sphinx_todoext_extension import TodoExt, TodoExtList
from .documentation_link import python_link_doc

from ..sphinxext.sphinx_autosignature import setup as setup_signature
from ..sphinxext.sphinx_bigger_extension import setup as setup_bigger
from ..sphinxext.sphinx_blocref_extension import setup as setup_blocref
from ..sphinxext.sphinx_blog_extension import setup as setup_blog
from ..sphinxext.sphinx_collapse_extension import setup as setup_collapse
from ..sphinxext.sphinx_gdot_extension import setup as setup_gdot
from ..sphinxext.sphinx_cmdref_extension import setup as setup_cmdref
from ..sphinxext.sphinx_docassert_extension import setup as setup_docassert
from ..sphinxext.sphinx_epkg_extension import setup as setup_epkg
from ..sphinxext.sphinx_exref_extension import setup as setup_exref
from ..sphinxext.sphinx_faqref_extension import setup as setup_faqref
from ..sphinxext.sphinx_githublink_extension import setup as setup_githublink
from ..sphinxext.sphinx_gitlog_extension import setup as setup_gitlog
from ..sphinxext.sphinx_image_extension import setup as setup_simpleimage
from ..sphinxext.sphinx_mathdef_extension import setup as setup_mathdef
from ..sphinxext.sphinx_quote_extension import setup as setup_quote
from ..sphinxext.sphinx_nbref_extension import setup as setup_nbref
from ..sphinxext.sphinx_postcontents_extension import setup as setup_postcontents
from ..sphinxext.sphinx_runpython_extension import setup as setup_runpython
from ..sphinxext.sphinx_runpython_extension import RunPythonDirective, runpython_node
from ..sphinxext.sphinx_sharenet_extension import setup as setup_sharenet
from ..sphinxext.sphinx_downloadlink_extension import setup as setup_downloadlink
from ..sphinxext.sphinx_template_extension import setup as setup_tpl
from ..sphinxext.sphinx_tocdelay_extension import setup as setup_tocdelay
from ..sphinxext.sphinx_toctree_extension import setup as setup_toctree
from ..sphinxext.sphinx_todoext_extension import setup as setup_todoext
from ..sphinxext.sphinx_video_extension import setup as setup_video
from ..sphinxext.sphinx_youtube_extension import setup as setup_youtube
from ..sphinxext.sphinximages.sphinxtrib.images import setup as setup_image

from ..sphinxext.sphinx_doctree_builder import setup as setup_doctree
from ..sphinxext.sphinx_latex_builder import setup as setup_latex
from ..sphinxext.sphinx_md_builder import setup as setup_md
from ..sphinxext.sphinx_rst_builder import setup as setup_rst


def get_default_extensions(load_bokeh=False):
    """
    Returns a list of default extensions.

    @param      load_bokeh  loads :epkg:`bokeh` extensions
                            (can be disabled as it is quite slow)
    @return                 list of :epkg:`Sphinx` extensions

    The current list is:

    .. runpython::
        :showcode:

        from pyquickhelper.sphinxext import get_default_extensions
        print("\\n".join(get_default_extensions()))
    """
    # We delay these imports.
    # They change matplotlib backend if executed.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from matplotlib.pyplot import get_backend, switch_backend
    backend = get_backend()
    from matplotlib.sphinxext.plot_directive import setup as setup_plot
    backend_ = get_backend()
    if backend_ != backend:  # pragma: no cover
        import matplotlib
        try:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("error", UserWarning)
                matplotlib.use('Agg')
        except UserWarning:
            import matplotlib.pyplot as plt  # pylint: disable=W0611
            switch_backend("Agg")

    default_setups = [setup_toctree,
                      setup_blog, setup_runpython, setup_sharenet,
                      setup_todoext, setup_bigger, setup_githublink,
                      setup_runpython, setup_mathdef, setup_blocref,
                      setup_faqref, setup_exref, setup_nbref,
                      setup_docassert, setup_signature, setup_tpl,
                      setup_cmdref, setup_epkg, setup_rst, setup_md,
                      setup_latex, setup_doctree,
                      setup_postcontents, setup_tocdelay, setup_youtube,
                      # directives from sphinx
                      setup_graphviz, setup_imgmath, setup_todo,
                      # the rest of it
                      setup_autodoc, setup_imagesvg,
                      setup_plot, setup_image, setup_collapse, setup_gdot,
                      setup_video, setup_simpleimage, setup_downloadlink,
                      setup_quote, setup_gitlog]

    if load_bokeh:
        try:
            import bokeh  # pylint: disable=W0611
            from ..sphinxext.bokeh.bokeh_plot import setup as setup_bokeh
            default_setups.append(setup_bokeh)
        except ImportError:  # pragma: no cover
            # bokeh is not installed.
            pass

    return [_.__module__ for _ in default_setups]


def get_default_standard_extensions(use_mathjax=False):
    """
    Returns a list of standard extensions.

    @param      use_mathjax     use :epkg:`mathjax` or :epkg:`imgmath`
    @return                     list of standard extension.
    """
    extensions = [
        'sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.coverage',
        'sphinx.ext.extlinks', 'sphinx.ext.graphviz', 'sphinx.ext.ifconfig',
        'sphinx.ext.inheritance_diagram',
        'sphinx.ext.mathjax' if use_mathjax else 'sphinx.ext.imgmath',
        'sphinx.ext.napoleon', 'sphinx.ext.todo', 'sphinx.ext.viewcode',
        'jupyter_sphinx.execute',
        'sphinxcontrib.imagesvg',
        'matplotlib.sphinxext.plot_directive',
    ]

    try:
        import sphinxcontrib.jsdemo
        assert sphinxcontrib.jsdemo is not None
        extensions.append('sphinxcontrib.jsdemo')
    except ImportError:  # pragma: no cover
        # No module sphinxcontrib.jsdemo.
        pass

    return extensions
