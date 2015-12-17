

.. blogpost::
    :title: Python code to generate part of sphinx documentation
    :keywords: sphinx, extensions, runpython
    :date: 2015-12-12
    :categories: sphinx

    I used the same title as a question asked on stackoverflow:
    `Python code to generate part of sphinx documentation, is it possible? <http://stackoverflow.com/questions/7250659/python-code-to-generate-part-of-sphinx-documentation-is-it-possible>`_.
    It became the following     
    :class:`RunPythonDirective <pyquickhelper.helpgen.sphinx_runpython_extension.RunPythonDirective>`
    which does the same with more options::
    
        .. runpython:
            :showcode:
            :rst:
            
            from pyquickhelper import df2rst
            import pandas
            df = <some dataframe>
            print(df2rst(df))
            
    Because of the option *rst*, what is printed out
    becomes part of the documentation through function
    `nested_parse_with_titles <http://code.nabla.net/doc/sphinx/api/sphinx/util/nodes/sphinx.util.nodes.nested_parse_with_titles.html#sphinx.util.nodes.nested_parse_with_titles>`_.
    In sphinx configuration setup, the following lines must be added::
    
        from pyquickhelper.helpgen.sphinx_runpython_extension import RunPythonDirective
        from pyquickhelper.helpgen.sphinx_runpython_extension import runpython_node, visit_runpython_node, depart_runpython_node
            
        def setup(app):         
            app.add_node(runpython_node,
                         html=(visit_runpython_node, depart_runpython_node),
                         latex=(visit_runpython_node, depart_runpython_node),
                         text=(visit_runpython_node, depart_runpython_node)) 
            app.add_directive('runpython', RunPythonDirective)
    