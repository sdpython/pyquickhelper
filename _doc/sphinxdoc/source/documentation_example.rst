
.. _l-example-documentation:

Examples for the documentation
==============================

.. _l-example_bokeh:

example with bokeh
------------------

.. bokeh-plot::

    from bokeh.plotting import figure, output_file, show

    output_file("example_bokeh.html")

    x = [1, 2, 3, 4, 5]
    y = [6, 7, 6, 4, 5]

    p = figure(title="example_bokeh", plot_width=300, plot_height=300)
    p.line(x, y, line_width=2)
    p.circle(x, y, size=10, fill_color="white")

    show(p)

exemple with a formula
----------------------

.. math::

    \norm{\left(\begin{array}{rr}
    1 & 0 \\ 0 & 1
    \end{array}\right)}

example with a running script
-----------------------------

.. runpython::
    :showcode:

    import numpy
    print(numpy.array([[1, 0], [0, 1]]))

a predefined link
-----------------

:epkg:`pep8`
