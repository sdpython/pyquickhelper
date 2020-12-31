"""
@file
@brief Function which filters ou warnings after running the unit test
"""
import warnings


def default_filter_warning(w):  # pragma: no cover
    """
    Filters out warnings.

    @param      w       warning
    @return             boolean (True to keep it)

    Interesting fields: ``w.message``, ``w.category``, ``w.filename``, ``w.lineno``.
    """
    if "RemovedInSphinx40Warning" in str(w):
        return False

    class UnusedException(Exception):
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            from matplotlib.cbook import MatplotlibDeprecationWarning
        except ImportError:
            MatplotlibDeprecationWarning = UnusedException

    if isinstance(w.message, RuntimeWarning):
        if "_bootstrap.py" in w.filename:
            if "numpy.dtype size changed" in str(w.message):
                return False
            if "More than 20 figures have been opened." in str(w.message):
                return False
    elif isinstance(w.message, UserWarning):
        if "matplotlib" in w.filename:
            if "findfont: Font family" in str(w.message):
                return False
        if "pyquickhelper" in w.filename:
            if "pymyinstall" in str(w.message):
                return False
    elif isinstance(w.message, MatplotlibDeprecationWarning):
        if "basemap" in w.filename:
            if "The ishold function was deprecated in version 2.0." in str(w.message):
                return False
    elif isinstance(w.message, ResourceWarning):
        if "pyquickhelper" in w.filename:
            if "Unable to retrieve content from" in str(w):
                return False
    elif isinstance(w.message, DeprecationWarning):
        if "RemovedInSphinx40Warning" in str(w):
            return False
        if w.filename.endswith("kernelspec.py"):
            return False
        if "jupyter_client" in w.filename:
            return False
        if "IPython" in w.filename:
            if "DisplayFormatter." in str(w.message):
                return False
            if "ScriptMagics." in str(w.message):
                return False
            if "HistoryManager." in str(w.message):
                return False
            if "ProfileDir." in str(w.message):
                return False
            if "InteractiveShell." in str(w.message):
                return False
            if "on_trait_change" in str(w.message):
                return False
            if "PlainTextFormatter." in str(w.message):
                return False
            if "Metadata should be set using the .tag()" in str(w.message):
                return False
        elif "nbconvert" in w.filename:
            if "SlidesExporter." in str(w.message):
                return False
            if "TemplateExporter." in str(w.message):
                return False
            if "HTMLExporter." in str(w.message):
                return False
            if "SVG2PDFPreprocessor." in str(w.message):
                return False
            if "on_trait_change" in str(w.message):
                return False
            if "PresentExporter." in str(w.message):
                return False
            if "NbConvertApp." in str(w.message):
                return False
            if "RSTExporter." in str(w.message):
                return False
            if "PythonExporter." in str(w.message):
                return False
            if "LatexExporter." in str(w.message):
                return False
            if "metadata should be set using the .tag()" in str(w.message).lower():
                return False
            if 'cgi.escape is deprecated, use html.escape instead' in str(w.message):
                return False
        elif "jupyter_core" in w.filename:
            if "JupyterApp." in str(w.message):
                return False
            if "metadata should be set using the .tag()" in str(w.message).lower():
                return False
        elif "nbextensions.py" in w.filename:
            if "metadata should be set using the .tag()" in str(w.message).lower():
                return False
        elif "docutils" in w.filename:
            if "'U' mode is deprecated" in str(w.message):
                return False
            if "Metadata should be set using the .tag()" in str(w.message):
                return False
        elif "sympy" in w.filename:
            if "inspect.getargspec() is deprecated" in str(w.message):
                return False
        elif "_mode_cbc.py" in w.filename:
            if "will be forbidden in the future" in str(w.message):
                return False
        elif "mpl_toolkits" in w.filename:
            if "The ishold function was deprecated in version 2.0." in str(w.message):
                return False
            if "The hold function was deprecated in version 2.0." in str(w.message):
                return False
            if "axes.hold is deprecated." in str(w.message):
                return False
        elif "_bootstrap.py" in w.filename:
            if "can't resolve package from __spec__" in str(w.message):
                return False
        elif "basemap" in w.filename:
            if "The ishold function was deprecated in version 2.0." in str(w.message):
                return False
        elif "pandas" in w.filename:
            if "ix is deprecated" in str(w.message):
                return False
        elif "sphinx" in w.filename:
            if "sphinx.util.compat.Directive is deprecated and will be removed" in str(w.message):
                return False
        elif "markdown_mistune.py" in w.filename:
            if "cgi.escape is deprecated, use html.escape instead" in str(w.message):
                return False
    elif isinstance(w.message, ImportWarning):
        if "_bootstrap.py" in w.filename:
            if "can't resolve package from __spec__" in str(w.message):
                return False
        elif w.filename.endswith("_bootstrap_external.py"):
            return False
    elif "MatplotlibDeprecationWarning" in str(type(w.message)):
        if "basemap" in w.filename:
            return False
    return True
