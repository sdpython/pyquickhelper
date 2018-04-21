
.. blogpost::
    :title: Check RST syntax
    :keywords: sphinx, RST
    :date: 2018-04-21
    :categories: sphinx

    It is usually a pain to discover I made an error in a
    formula while I'm writing documentation. It fails
    quite long after after the unit tests started. The
    documentation is generated after the unit test pass.
    I also use a lot ``.. runpython::``
    (see :class:`RunPythonDirective <pyquickhelper.sphinxext.sphinx_runpython_extension.RunPythonDirective>`)
    to run pieces of code inside the documentation.
    It is quite annoying to discover it fails long after.
    So I creates a unit test which can be used to compile a
    single page of the documentation :
    `test_doc_page <https://github.com/sdpython/pyquickhelper/blob/master/_unittests/ut_module/test_doc_page.py>`_.
    I modify the page name when I have some doubt or I move to
    another one.
