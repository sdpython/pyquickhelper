
.. blogpost::
    :title: Convert a notebook into slides
    :keywords: script, notebook, slides, add_tag_slide
    :date: 2015-05-16
    :categories: notebook, automation

    I thought it would be easy to convert a notebook into
    slides. I would just have to execute
    `nbconvert <http://ipython.org/ipython-doc/3/notebook/nbconvert.html>`_.
    I went through two issues. The first one came from
    `reveal.js <https://github.com/hakimel/reveal.js/>`_.
    My first tries did not work.
    I decided to take the version included in the module
    `sphinxjp.themes.revealjs <https://github.com/tell-k/sphinxjp.themes.revealjs>`_
    and I also updated the output of *nbconvert* to remove external links as much
    as possible.

    The second issue was that all my notebooks did not include any metadata
    indicated to indicate whether or not a new slide or subslide should start.
    So I create a simple function which does that on a notebook
    :meth:`add_tag_slide <pyquickhelper.ipythonhelper.notebook_runner.NotebookRunner.add_tag_slide>`.
    It does not overwrite existing metadata but start new slides for every section
    and new subslide if the current one becomes too long::

        from pyquickhelper.ipythonhelper import read_nb
        nb = read_nb("your notebook.ipynb")
        nb.add_tag_slide()
        nb.to_json("the modified notebook.ipynb")

    It is too simple to be perfect, it is difficult to guess the size
    of the rendering of some objects (images, javascript...).
    You can check the results for this notebook:
    :ref:`examplepyquickhelperrst`.
    That what the function :func:`nb2slides <pyquickhelper.helpgen.process_notebook_api.nb2slides>`
    is doing first and then converts it into slides::

        from pyquickhelper import nb2slides
        nb2slides(("your notebook.ipynb", "convert.slides.html")
