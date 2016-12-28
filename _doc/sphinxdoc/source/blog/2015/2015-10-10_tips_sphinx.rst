
.. blogpost::
    :title: A few tips with Sphinx
    :keywords: sphinx, tips, latex, bullets
    :date: 2015-10-10
    :categories: sphinx, latex

    Sphinx generates many warning when it builds
    the documentation despite the fact the result looks good.
    Some cases.

    **nested bullets**

    According to `How to create a nested list in reStructuredText? <http://stackoverflow.com/questions/5550089/how-to-create-a-nested-list-in-restructuredtext>`_,
    a space must be inserted for nested bullets. The wrong syntax::

        * level 1
            * level 2
            * level 2 as well
        * level 1 again

    The right syntax::

        * level 1

            * level 2
            * level 2 as well

        * level 1 again

    **latex formulas**

    The page `Math support in Sphinx <http://sphinx-doc.org/ext/math.html?highlight=math#module-sphinx.ext.mathbase>`_
    explains how to set up math environment (latex or mathjax).
    But if you add matplotlib to convert equations into images
    (`matplotlib.sphinxext.mathmpl <http://matplotlib.org/sampledoc/extensions.html#using-math>`_),
    the sphinx extension
    `sphinx.ext.pngmath is disabled <http://sphinx-doc.org/ext/math.html#module-sphinx.ext.pngmath>`_.
    Matplotlib extension has some limitations. ``\text`` does not work.

    **formulas in docstring**

    When included in a doc string, backslashes must be doubled::

        """
        \\min_i \\{ ...
        """
