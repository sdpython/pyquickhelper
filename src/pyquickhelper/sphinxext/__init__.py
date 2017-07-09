"""
@file
@brief Subpart related to sphinx extensions

.. todoext::
    :title: add directive for a sortable table
    :tag: enhancement
    :issue: 27

    Based on `slickgrid <https://github.com/mleibman/SlickGrid/tree/master/examples>`_.
"""
from .blog_post import BlogPost
from .blog_post_list import BlogPostList
from .sphinx_bigger_extension import bigger_node, bigger_role
from .sphinx_githublink_extension import githublink_node, githublink_role
from .sphinx_blocref_extension import BlocRef, BlocRefList
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_exref_extension import ExRef, ExRefList
from .sphinx_faqref_extension import FaqRef, FaqRefList
from .sphinx_mathdef_extension import MathDef, MathDefList
from .sphinx_nbref_extension import NbRef, NbRefList
from .sphinx_runpython_extension import RunPythonDirective, runpython_node
from .sphinx_sharenet_extension import ShareNetDirective, sharenet_node
from .sphinx_todoext_extension import TodoExt, TodoExtList
from .sphinx_template_extension import tpl_node
from .documentation_link import python_link_doc

from sphinx.ext.autodoc import setup as setup_autodoc
from sphinx.ext.imgmath import setup as setup_imgmath
from sphinxcontrib.imagesvg import setup as setup_imagesvg
from sphinx.ext.graphviz import setup as setup_graphviz
from sphinx.ext.imgmath import setup as setup_math
from sphinx.ext.todo import setup as setup_todo

from matplotlib.sphinxext.plot_directive import setup as setup_plot
from matplotlib.sphinxext.only_directives import setup as setup_only
from ..sphinxext.sphinx_bigger_extension import setup as setup_bigger
from ..sphinxext.sphinx_githublink_extension import setup as setup_githublink
from ..sphinxext.sphinx_blocref_extension import setup as setup_blocref
from ..sphinxext.sphinx_blog_extension import setup as setup_blog
from ..sphinxext.sphinx_docassert_extension import setup as setup_docassert
from ..sphinxext.sphinx_exref_extension import setup as setup_exref
from ..sphinxext.sphinx_faqref_extension import setup as setup_faqref
from ..sphinxext.sphinx_mathdef_extension import setup as setup_mathdef
from ..sphinxext.sphinx_nbref_extension import setup as setup_nbref
from ..sphinxext.sphinx_runpython_extension import setup as setup_runpython
from ..sphinxext.sphinx_sharenet_extension import setup as setup_sharenet
from ..sphinxext.sphinx_todoext_extension import setup as setup_todoext
from ..sphinxext.sphinx_autosignature import setup as setup_signature
from ..sphinxext.sphinx_template_extension import setup as setup_tpl


def get_default_extensions():
    """
    Return a list of default extensions.

    @return     list of Sphinx extensions

    The current list is:

    .. runpython::
        :showcode:

        from pyquickhelper.sphinxext import get_default_extensions
        print("\\n".join(get_default_extensions()))

    .. versionadded:: 1.5
    """
    default_setups = [setup_blog, setup_runpython, setup_sharenet,
                      setup_todoext, setup_bigger, setup_githublink,
                      setup_runpython, setup_mathdef, setup_blocref,
                      setup_faqref, setup_exref, setup_nbref,
                      setup_docassert, setup_signature, setup_tpl,
                      # directives from sphinx
                      setup_graphviz, setup_math, setup_todo,
                      # the rest of it
                      setup_autodoc, setup_imgmath, setup_imagesvg,
                      setup_plot, setup_only]
    return [_.__module__ for _ in default_setups]
