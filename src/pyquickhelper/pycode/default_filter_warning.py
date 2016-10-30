"""
@file
@brief Function which filters ou warnings after running the unit test

.. versionadded:: 1.5
"""


def default_filter_warning(w):
    """
    filters out warning

    @param      w       warning
    @return             boolean (True to keep it)

    Interesting fields: ``w.message``, ``w.category``, ``w.filename``, ``w.lineno``.

    .. todoext::
        :title: filter warnings after the unit tests
        :tag: done
        :date: 2016-07-05
        :hidden:
        :issue: 19
        :release: 1.4
        :cost: 0.2

        Parameter *filter_warning* was added to give users
        a way to define their own filtering.
    """
    if isinstance(w.message, DeprecationWarning):
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
            if "Metadata should be set using the .tag()" in str(w.message):
                return False
        elif "jupyter_core" in w.filename:
            if "JupyterApp." in str(w.message):
                return False
            if "metadata should be set using the .tag()" in str(w.message):
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
    elif isinstance(w.message, ImportWarning):
        if w.filename.endswith("_bootstrap_external.py"):
            return False
    return True
