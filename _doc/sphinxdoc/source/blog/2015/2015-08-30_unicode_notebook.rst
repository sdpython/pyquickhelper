
.. index:: babel, sphinx, issue

.. blogpost::
    :title: Why do I see invered question in a notebook converted into PDF?
    :keywords: latex,
    :date: 2015-08-30
    :categories: sphinx, notebook

    The function :func:`process_notebooks <pyquickhelper.helpgen.process_notebooks.process_notebooks>`
    still uses the executable
    `pdflatex <https://en.wikipedia.org/w/index.php?title=PdfTeX&redirect=no>`_
    and not
    `xetex <https://en.wikipedia.org/wiki/XeTeX>`_
    which can handle inline unicode characters.
    That's why they are replaced by *¿* by function
    :func:`post_process_latex <pyquickhelper.helpgen.post_process.post_process_latex>`.
