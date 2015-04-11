

.. blogpost::
    :title: Insert plot from bokeh in the documentation
    :keywords: sphinx, bokeh, bokeh-plot
    :date: 2015-04-12
    :categories: documentation, graph
    
    As graphs from 
    `matplotlib <http://matplotlib.org/>`_, 
    graphs from
    `bokeh <http://bokeh.pydata.org/>`_
    can be inserted in the documentation with the extension
    `bokeh.sphinxext.bokeh_plot <http://bokeh.pydata.org/en/dev/docs/reference/sphinxext.html#bokeh-sphinxext-bokeh-plot>`_.
    
    I replicate here the example from the documentation::
    
        .. bokeh-plot::

            from bokeh.plotting import figure, output_file, show

            output_file("example_bokeh.html")

            x = [1, 2, 3, 4, 5]
            y = [6, 7, 6, 4, 5]

            p = figure(title="example_bokeh", plot_width=300, plot_height=300)
            p.line(x, y, line_width=2)
            p.circle(x, y, size=10, fill_color="white")

            show(p)    
            
    See :ref:`l-example_bokeh` to se the result. 
    Including this code in the blog post fails but 
    it should be fixed some days.
 
        
            