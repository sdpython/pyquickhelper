

.. blogpost::
    :title: Gallery of notebook
    :keywords: gallery, documentation, notebook, thumbnail
    :date: 2016-12-25
    :categories: notebook
    
    The module `sphinx-gallery <https://github.com/sphinx-gallery/sphinx-gallery>`_
    became quite popular. I discovered that
    `sphinx-nbexamples <https://github.com/Chilipp/sphinx-nbexamples>`_ was doing the same.
    I integrated the first one into pyquickhelper but I did something
    different for the second as I already had some custom logic to handle
    notebooks.
    :meth:`get_thumbnail <pyquickhelper.helpgen.ipythonhelper.notebook_runner.NotebookRunner.get_thumbnail`
    which creates a thumbnail by getting the last image if there is one
    or the last result output cell. The module uses matploblib to builds an image
    with text results.
    You can check the results at :ref:`l-notebooks`.
